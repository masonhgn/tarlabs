"""Ingest of public orbital elements (task S-02).

Pulls OMM (Orbit Mean-Elements Message, CCSDS 502.0-B-3) records from the CelesTrak GP API
and caches them on disk. Anonymous, no login.

    https://celestrak.org/NORAD/elements/gp.php?{QUERY}=VALUE&FORMAT=json

Two deliberate choices, both of which belong in the proposal:

*   **OMM/JSON, not fixed-width TLE.** CelesTrak exhausted 5-digit catalogue numbers in
    July 2026; objects numbered 100000+ are not published in legacy TLE format at all. An
    ingest built on TLE column positions has a hard expiry date. OMM does not.
*   **Cache everything, refresh on a timer.** The catalogue updates only a few times a day.
    Space-Track's published limits are <30 requests/minute and <300/hour; CelesTrak asks for
    the same restraint. Cached pulls also make every run reproducible after the fact.

Redistribution: USSPACECOM grants blanket approval to redistribute "basic SSA data"
(TLE/OMM/SATCAT/decay) with citation, so derived products are publishable — but per the
repo data policy we keep raw bulk pulls out of any public repo. See
analysis/compliance/itar_posture.md (G-05).
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

import requests

GP_URL = "https://celestrak.org/NORAD/elements/gp.php"

#: CelesTrak asks for one query at a time and no hammering. The catalogue only moves a few
#: times a day, so this is generous.
_MIN_SECONDS_BETWEEN_REQUESTS = 2.0

#: Cached records older than this are refetched.
DEFAULT_MAX_AGE = timedelta(hours=12)

_DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
OMM_CACHE = _DATA_ROOT / "raw" / "omm"

_last_request_at = 0.0


class CatalogError(RuntimeError):
    """A catalogue query failed or returned nothing usable."""


@dataclass(frozen=True)
class OmmRecord:
    """One OMM record plus the provenance we need to cite it."""

    fields: dict[str, Any]
    fetched_at: datetime
    source: str

    @property
    def norad_id(self) -> int:
        return int(self.fields["NORAD_CAT_ID"])

    @property
    def name(self) -> str:
        return str(self.fields.get("OBJECT_NAME", "")).strip()

    @property
    def epoch(self) -> datetime:
        """Element-set epoch, UTC-aware."""
        raw = str(self.fields["EPOCH"])
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    @property
    def age(self) -> timedelta:
        """How stale the elements are. SGP4 error grows roughly 1-3 km per day of this."""
        return datetime.now(timezone.utc) - self.epoch

    def citation(self) -> str:
        return (
            f"{self.name} (NORAD {self.norad_id}), OMM epoch "
            f"{self.epoch.isoformat()}, retrieved from CelesTrak "
            f"{self.fetched_at.date().isoformat()}"
        )


def _throttle() -> None:
    global _last_request_at
    wait = _MIN_SECONDS_BETWEEN_REQUESTS - (time.monotonic() - _last_request_at)
    if wait > 0:
        time.sleep(wait)
    _last_request_at = time.monotonic()


def _cache_path(key: str, cache_dir: Path) -> Path:
    return cache_dir / f"{key}.json"


def _read_cache(path: Path, max_age: timedelta) -> list[dict[str, Any]] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    fetched = datetime.fromisoformat(payload["fetched_at"])
    if datetime.now(timezone.utc) - fetched > max_age:
        return None
    return payload["records"]


def _write_cache(path: Path, records: list[dict[str, Any]], source: str) -> datetime:
    path.parent.mkdir(parents=True, exist_ok=True)
    fetched = datetime.now(timezone.utc)
    path.write_text(
        json.dumps(
            {"fetched_at": fetched.isoformat(), "source": source, "records": records},
            indent=2,
        ),
        encoding="utf-8",
    )
    return fetched


def fetch_gp(
    *,
    catnr: int | None = None,
    intdes: str | None = None,
    group: str | None = None,
    cache_dir: Path = OMM_CACHE,
    max_age: timedelta = DEFAULT_MAX_AGE,
    offline: bool = False,
    timeout: float = 30.0,
) -> list[OmmRecord]:
    """Fetch OMM records for one CelesTrak GP query, using the disk cache when it is fresh.

    Exactly one of ``catnr``, ``intdes`` or ``group`` must be given, mirroring the API.
    With ``offline=True`` the cache is used regardless of age and no request is made, which
    is what the test suite and any air-gapped rerun want.
    """
    given = {"CATNR": catnr, "INTDES": intdes, "GROUP": group}
    query = {k: v for k, v in given.items() if v is not None}
    if len(query) != 1:
        raise ValueError("give exactly one of catnr, intdes or group")
    (param, value), = query.items()

    key = f"{param.lower()}_{value}"
    path = _cache_path(key, cache_dir)

    if offline:
        cached = _read_cache(path, max_age=timedelta.max)
        if cached is None:
            raise CatalogError(f"offline and no cached records for {param}={value} at {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        fetched = datetime.fromisoformat(payload["fetched_at"])
        return [OmmRecord(r, fetched, payload["source"]) for r in cached]

    cached = _read_cache(path, max_age)
    if cached is not None:
        payload = json.loads(path.read_text(encoding="utf-8"))
        fetched = datetime.fromisoformat(payload["fetched_at"])
        return [OmmRecord(r, fetched, payload["source"]) for r in cached]

    params = {param: str(value), "FORMAT": "json"}
    _throttle()
    try:
        response = requests.get(GP_URL, params=params, timeout=timeout)
        response.raise_for_status()
        records = response.json()
    except requests.RequestException as exc:
        raise CatalogError(f"CelesTrak request failed for {param}={value}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise CatalogError(f"CelesTrak returned non-JSON for {param}={value}: {exc}") from exc

    # CelesTrak answers an unknown catalogue number with a body of "No GP data found",
    # which json-decodes to a string rather than raising.
    if not isinstance(records, list) or not records:
        raise CatalogError(f"no GP data found for {param}={value}")

    source = f"{GP_URL}?{param}={value}&FORMAT=json"
    fetched = _write_cache(path, records, source)
    return [OmmRecord(r, fetched, source) for r in records]


def fetch_many(
    norad_ids: Sequence[int],
    *,
    cache_dir: Path = OMM_CACHE,
    max_age: timedelta = DEFAULT_MAX_AGE,
    offline: bool = False,
) -> dict[int, OmmRecord]:
    """Fetch several catalogue numbers, skipping any that fail rather than aborting.

    Missing objects are the caller's problem to report; a decayed or renumbered satellite
    should not take down a whole analysis run.
    """
    out: dict[int, OmmRecord] = {}
    for norad_id in norad_ids:
        try:
            records = fetch_gp(
                catnr=norad_id, cache_dir=cache_dir, max_age=max_age, offline=offline
            )
        except CatalogError:
            continue
        for record in records:
            out[record.norad_id] = record
    return out


def load_cached(cache_dir: Path = OMM_CACHE) -> Iterable[OmmRecord]:
    """Every OMM record on disk, regardless of age. For offline reruns and inspection."""
    if not cache_dir.exists():
        return
    for path in sorted(cache_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        fetched = datetime.fromisoformat(payload["fetched_at"])
        for record in payload["records"]:
            yield OmmRecord(record, fetched, payload["source"])
