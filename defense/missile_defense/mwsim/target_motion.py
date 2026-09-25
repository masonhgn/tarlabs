"""Target motion, sourced externally rather than modelled here (task S-06, DEC-38).

This study needs moving targets to detect and track. It does **not** implement the physics
that produces them. Instead it consumes the Berkeley Risk and Security Lab's published
simulator — the tool built by the same research lineage whose peer-reviewed model we would
otherwise have re-implemented — and treats its output as an input, in exactly the way
`catalog.py` treats orbital elements and `goes.py` treats radiance scenes.

## Why this is better methodology, not just a workaround

Re-implementing published equations invites an obvious objection: *did you transcribe them
correctly?* D-03 found two genuine transcription ambiguities in the source paper's glyphs,
resolved only by dimensional analysis and by physical reasoning. Every such resolution is
a place a reviewer can push.

Consuming the authors' own implementation removes that class of objection entirely. We
already confirmed it reproduces the paper's published maximum range to **0.09%**, so the
external tool is validated against the literature independently of us.

It also removes a maintenance burden. A trajectory model we own is a model we must defend,
tune, and keep correct. A cited external source is a citation.

## What this module does and does not do

* **Does**: fetch trajectories for requested flight conditions, cache them on disk with
  provenance, resample them onto a simulation time grid, and convert them into the
  Earth-centred inertial positions the coverage and detection code expects.
* **Does not**: integrate equations of motion, define vehicle parameters, or model any
  specific real system. The flight conditions passed in are the published notional ones
  recorded in `data/reference/threat_model_reference.json`.

Results are cached because the service is a free public research tool and should not be
hammered — one request per distinct condition, reused thereafter.
"""

from __future__ import annotations

import hashlib
import json
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

#: Berkeley Risk and Security Lab public simulator.
BRSL_URL = "https://hypersonic-missile-flight-model.onrender.com/simulate"

_DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
CACHE_DIR = _DATA_ROOT / "reference" / "target_motion"

RE_KM = 6371.0


class TargetMotionUnavailable(RuntimeError):
    """The external source could not be reached and no cached result exists."""


@dataclass(frozen=True)
class TargetTrack:
    """One target's motion over time, as supplied by the external source."""

    time_s: np.ndarray
    altitude_km: np.ndarray
    downrange_km: np.ndarray
    crossrange_km: np.ndarray
    speed_km_s: np.ndarray
    flight_path_deg: np.ndarray
    heading_deg: np.ndarray
    conditions: dict
    source: str

    def __len__(self) -> int:
        return len(self.time_s)

    @property
    def duration_s(self) -> float:
        return float(self.time_s[-1] - self.time_s[0])

    @property
    def max_range_km(self) -> float:
        return float(self.downrange_km[-1])

    def resample(self, times_s: np.ndarray) -> "TargetTrack":
        """Interpolate onto a simulation time grid.

        Values outside the source track's span are clamped rather than extrapolated: a
        target that has landed has landed, and inventing motion past the end of a cited
        trajectory would be exactly the kind of un-sourced number this project avoids.
        """
        t = np.clip(np.asarray(times_s, dtype=float), self.time_s[0], self.time_s[-1])
        interp = lambda y: np.interp(t, self.time_s, y)  # noqa: E731
        return TargetTrack(
            time_s=t,
            altitude_km=interp(self.altitude_km),
            downrange_km=interp(self.downrange_km),
            crossrange_km=interp(self.crossrange_km),
            speed_km_s=interp(self.speed_km_s),
            flight_path_deg=interp(self.flight_path_deg),
            heading_deg=interp(self.heading_deg),
            conditions=self.conditions,
            source=self.source,
        )

    def to_eci_km(
        self, *, start_lat_deg: float = 0.0, start_lon_deg: float = 0.0
    ) -> np.ndarray:
        """Positions in an Earth-centred inertial frame, ``(n_time, 3)`` km.

        The source gives motion in a track-relative frame — downrange, crossrange and
        altitude from a start point. This places that track on a spherical Earth at a
        chosen origin, heading due east, which is what the coverage geometry consumes.

        Spherical Earth, consistent with the source model's own assumption. Using an
        ellipsoid here would be more precise than the data warrants and would silently
        disagree with the trajectory it is placing.
        """
        lat0 = np.radians(start_lat_deg)
        lon0 = np.radians(start_lon_deg)

        # Angular displacement along and across the initial heading.
        d_down = self.downrange_km / RE_KM
        d_cross = self.crossrange_km / RE_KM

        lat = lat0 + d_cross
        lon = lon0 + d_down / np.maximum(np.cos(lat), 1e-6)
        r = RE_KM + self.altitude_km

        return np.stack(
            [
                r * np.cos(lat) * np.cos(lon),
                r * np.cos(lat) * np.sin(lon),
                r * np.sin(lat),
            ],
            axis=-1,
        )


def _cache_key(conditions: dict) -> str:
    """Stable hash of a condition set.

    Numeric values are normalised to float first: ``0`` and ``0.0`` are the same flight
    condition but serialise differently, which would silently miss the cache and re-hit a
    free public service for a trajectory already on disk.
    """
    normalised = {
        k: (float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v)
        for k, v in conditions.items()
    }
    blob = json.dumps(normalised, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def _from_payload(payload: dict) -> TargetTrack:
    r = payload["results"]
    return TargetTrack(
        time_s=np.asarray(r["time"], dtype=float),
        altitude_km=np.asarray(r["altitude"], dtype=float),
        downrange_km=np.asarray(r["range"], dtype=float),
        crossrange_km=np.asarray(r["crossrange"], dtype=float),
        speed_km_s=np.asarray(r["velocity"], dtype=float),
        flight_path_deg=np.asarray(r["gamma_deg"], dtype=float),
        heading_deg=np.asarray(r["kappa_deg"], dtype=float),
        conditions=payload.get("_params", {}),
        source=payload.get("_url", BRSL_URL),
    )


def fetch(
    *,
    speed_km_s: float,
    ballistic_coefficient: float,
    lift_to_drag: float,
    roll_deg: float = 0.0,
    flight_path_deg: float = 0.0,
    heading_deg: float = 0.0,
    mass_kg: float = 1000.0,
    cache_dir: Path = CACHE_DIR,
    offline: bool = False,
    timeout: float = 180.0,
) -> TargetTrack:
    """Request a trajectory for one set of published flight conditions, with caching.

    The defaults are the notional values recorded in D-03 from the open literature. Roll
    angle is the manoeuvre control: zero flies straight, non-zero turns.
    """
    conditions = {
        "v0": speed_km_s,
        "rolld0": roll_deg,
        "gammad0": flight_path_deg,
        "kappad0": heading_deg,
        "payload": mass_kg,
        "beta": ballistic_coefficient,
        "LtoD": lift_to_drag,
        "r0": 0,
        "cr0": 0,
        "t0": 0,
    }
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"brsl_{_cache_key(conditions)}.json"

    if path.exists():
        return _from_payload(json.loads(path.read_text(encoding="utf-8")))
    if offline:
        raise TargetMotionUnavailable(
            f"offline and no cached trajectory for {conditions} at {path}"
        )

    request = urllib.request.Request(
        BRSL_URL,
        data=json.dumps(conditions).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        response = json.loads(urllib.request.urlopen(request, timeout=timeout).read())
    except Exception as exc:  # network, timeout, or service error
        raise TargetMotionUnavailable(f"BRSL request failed: {exc}") from exc

    if not response.get("success") or not response.get("results", {}).get("time"):
        raise TargetMotionUnavailable(f"BRSL returned no usable trajectory: {conditions}")

    payload = {
        "_source": "Berkeley Risk and Security Lab, Hypersonic Glide Vehicle Simulator",
        "_url": BRSL_URL,
        "_retrieved": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "_params": conditions,
        "_note": "External published tool. We consume its output; we do not model this "
                 "motion ourselves. See mwsim/target_motion.py and DEC-38.",
        "results": response["results"],
    }
    path.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    return _from_payload(payload)


def load_cached(cache_dir: Path = CACHE_DIR) -> list[TargetTrack]:
    """Every trajectory already on disk. For offline reruns and inspection."""
    if not cache_dir.exists():
        return []
    out = []
    for p in sorted(cache_dir.glob("brsl_*.json")):
        try:
            out.append(_from_payload(json.loads(p.read_text(encoding="utf-8"))))
        except (OSError, json.JSONDecodeError, KeyError):
            continue
    return out
