"""Space-Track REST client, for the historical element sets CelesTrak does not serve
(task D-01, feeding the multi-epoch orbit audit in D-14).

CelesTrak gives us the *current* GP record for an object. To tell a commanded manoeuvre
apart from secular decay we need the whole `gp_history` series, and that requires a
Space-Track account.

**Redistribution.** The User Agreement (10 USC 2274(c)(2)) says not to transfer received
data or analysis of it to third parties without approval. USSPACECOM grants express
blanket approval for "basic SSA data" -- TLE, OMM, SATCAT, decay -- conditioned on
citation. Our working rule, per `analysis/compliance/itar_posture.md`: cite Space-Track,
publish derived products, and never mirror bulk raw pulls. `data/raw/spacetrack/` is
gitignored for exactly this reason.

**Rate limits**, verbatim from the API Use Guidelines: "Limit API queries to less than 30
requests per 1 minute(s) and 300 requests per 1 hour(s)." The full catalogue only updates
a few times a day, so this module throttles hard and caches everything.
"""

from __future__ import annotations

import json
import os
import time
from collections import deque
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

import requests

BASE = "https://www.space-track.org"
LOGIN_URL = f"{BASE}/ajaxauth/login"
QUERY_URL = f"{BASE}/basicspacedata/query"

_DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
HISTORY_CACHE = _DATA_ROOT / "raw" / "spacetrack"

#: Published limits are 30/min and 300/hr. We sit well inside both: nothing here is
#: latency-sensitive, and a throttled client that never trips a limit is worth more than
#: a fast one that gets the account suspended mid-study.
_MAX_PER_MINUTE = 20
_MAX_PER_HOUR = 200
_MIN_INTERVAL_S = 3.0


class SpaceTrackError(RuntimeError):
    """Authentication failed, a query failed, or the response was unusable."""


def load_dotenv(start: Path | None = None) -> dict[str, str]:
    """Find the nearest `.env` walking upward, and return its key/value pairs.

    The file lives at the monorepo root rather than in this package, so searching upward
    is what lets the client work from any working directory. Values already present in the
    real environment win, so a CI secret or a shell export overrides the file.
    """
    here = (start or Path(__file__).resolve().parent).resolve()
    values: dict[str, str] = {}
    for directory in [here, *here.parents]:
        candidate = directory / ".env"
        if not candidate.is_file():
            continue
        for raw in candidate.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            values.setdefault(key.strip(), value.strip().strip("'\""))
        break
    return values


def credentials() -> tuple[str, str]:
    """Space-Track username and password, from the environment or the nearest `.env`.

    Raises rather than returning empty strings: a silent anonymous request would come back
    as an HTML login page, which is a far more confusing failure than a missing key.
    """
    env = load_dotenv()
    user = os.environ.get("SPACETRACK_USERNAME") or env.get("SPACETRACK_USERNAME")
    password = os.environ.get("SPACETRACK_PASSWORD") or env.get("SPACETRACK_PASSWORD")
    if not user or not password:
        raise SpaceTrackError(
            "SPACETRACK_USERNAME / SPACETRACK_PASSWORD not found in the environment or in "
            "a .env file in this directory or any parent. See PLAN.md task D-01."
        )
    return user, password


class SpaceTrackClient:
    """A throttled, caching Space-Track session.

    Use as a context manager so the session is closed and the auth cookie dropped:

        with SpaceTrackClient() as client:
            records = client.gp_history(56171)
    """

    def __init__(self, *, cache_dir: Path = HISTORY_CACHE, timeout: float = 60.0) -> None:
        self._session = requests.Session()
        self._authenticated = False
        self._cache_dir = cache_dir
        self._timeout = timeout
        self._recent: deque[float] = deque()
        self._last_request = 0.0

    def __enter__(self) -> "SpaceTrackClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._session.close()
        self._authenticated = False

    # -- plumbing ----------------------------------------------------------------

    def _throttle(self) -> None:
        """Block until another request is within both the minute and hour budgets."""
        now = time.monotonic()
        gap = _MIN_INTERVAL_S - (now - self._last_request)
        if gap > 0:
            time.sleep(gap)

        while True:
            now = time.monotonic()
            while self._recent and now - self._recent[0] > 3600.0:
                self._recent.popleft()
            in_last_minute = sum(1 for t in self._recent if now - t < 60.0)
            if in_last_minute < _MAX_PER_MINUTE and len(self._recent) < _MAX_PER_HOUR:
                break
            time.sleep(2.0)

        self._recent.append(time.monotonic())
        self._last_request = time.monotonic()

    def authenticate(self) -> None:
        if self._authenticated:
            return
        user, password = credentials()
        self._throttle()
        try:
            response = self._session.post(
                LOGIN_URL,
                data={"identity": user, "password": password},
                timeout=self._timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise SpaceTrackError(f"Space-Track login request failed: {exc}") from exc

        # A failed login returns HTTP 200 with a JSON error body, so the status code
        # alone does not tell us whether we are in.
        body = response.text.strip()
        if "Failed" in body or "login" in body.lower() and len(body) > 200:
            raise SpaceTrackError(
                "Space-Track rejected the credentials, or the account is not yet approved. "
                "Check the username and password, and that the registration email was "
                "confirmed and the account activated."
            )
        self._authenticated = True

    def query(self, path: str) -> list[dict[str, Any]]:
        """Run one `basicspacedata` query. ``path`` is everything after `/query`."""
        self.authenticate()
        url = f"{QUERY_URL}/{path.lstrip('/')}"
        self._throttle()
        try:
            response = self._session.get(url, timeout=self._timeout)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise SpaceTrackError(f"query failed ({url}): {exc}") from exc
        except json.JSONDecodeError as exc:
            raise SpaceTrackError(
                f"query returned non-JSON ({url}); the session may have expired: {exc}"
            ) from exc
        if isinstance(payload, dict):
            raise SpaceTrackError(f"query returned an error object ({url}): {payload}")
        return payload

    # -- the queries we actually need ---------------------------------------------

    def gp_history(
        self,
        norad_id: int,
        *,
        since: datetime | None = None,
        max_age: timedelta = timedelta(days=7),
        refresh: bool = False,
    ) -> list[dict[str, Any]]:
        """Every historical GP record for one object, oldest first, cached on disk.

        This is the query CelesTrak cannot answer and the reason the account exists.
        """
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        path = self._cache_dir / f"gp_history_{norad_id}.json"

        if path.exists() and not refresh:
            try:
                cached = json.loads(path.read_text(encoding="utf-8"))
                fetched = datetime.fromisoformat(cached["fetched_at"])
                if datetime.now(timezone.utc) - fetched <= max_age:
                    return cached["records"]
            except (OSError, json.JSONDecodeError, KeyError, ValueError):
                pass  # unreadable cache is a refetch, not an error

        query = f"class/gp_history/NORAD_CAT_ID/{norad_id}"
        if since is not None:
            query += f"/EPOCH/%3E{since.date().isoformat()}"
        query += "/orderby/EPOCH%20asc/format/json"

        records = self.query(query)
        path.write_text(
            json.dumps(
                {
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "source": f"{QUERY_URL}/{query}",
                    "norad_cat_id": norad_id,
                    "records": records,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return records

    def gp_history_many(
        self,
        norad_ids: Sequence[int],
        *,
        since: datetime | None = None,
        refresh: bool = False,
    ) -> dict[int, list[dict[str, Any]]]:
        """``gp_history`` for several objects. One failure does not abort the rest."""
        out: dict[int, list[dict[str, Any]]] = {}
        for norad_id in norad_ids:
            try:
                out[norad_id] = self.gp_history(norad_id, since=since, refresh=refresh)
            except SpaceTrackError:
                continue
        return out

    def satcat(self, norad_ids: Iterable[int]) -> list[dict[str, Any]]:
        """SATCAT entries: launch date, decay date, object type, operational status.

        This is how we resolve DSP-23 properly -- whether an object is decayed is a
        catalogue fact, not something to infer from a missing GP record.
        """
        ids = ",".join(str(i) for i in norad_ids)
        return self.query(f"class/satcat/NORAD_CAT_ID/{ids}/format/json")
