"""Earth orientation parameters, and the size of the approximations we make (task D-15).

`propagate.teme_to_ecef` approximates UT1 by UTC and neglects polar motion. Both are
standard simplifications for a trade study, but "small, therefore ignored" is an assertion
until someone measures it. This module measures it, against IERS `finals2000A`.

**Measured bounds** (IERS series, 2023 onward):

| Approximation | Magnitude | Position error | vs. SGP4 error floor |
|---|---|---|---|
| UT1 ≈ UTC | ≤ 0.199 s | ≤ **90 m** at the equator | ~10× smaller |
| Polar motion neglected | ≤ 0.545 arcsec | ≤ **17 m** | ~60× smaller |

Against SGP4's ~1 km at epoch, growing 1–3 km/day, both are comfortably inside the noise.
So we do **not** apply these corrections: doing so would add a data dependency that must be
kept current, in exchange for removing an error an order of magnitude below the floor set
by the element sets themselves.

The lookups are provided anyway, so the decision can be revisited with evidence rather than
re-argued, and so the bound can be re-checked if the study ever moves to a regime where it
matters.

Note the full IERS record reaches ±0.81 s of UT1−UTC (leap seconds reset it), which is
~370 m. An earlier note in `propagate.py` quoted ~0.4 km on the basis of the 0.9 s
leap-second bound: correct as a historical worst case, pessimistic by ~4× for current
epochs.

Data: IERS Earth Orientation Centre, `finals2000A.all.csv`. Public domain.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np

_DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
EOP_FILE = _DATA_ROOT / "raw" / "eop" / "finals2000A.all.csv"
EOP_URL = "https://datacenter.iers.org/data/csv/finals2000A.all.csv"

#: Earth equatorial radius, km.
RE_KM = 6378.137
#: Sidereal day, seconds — the rotation rate that converts a time error to a position error.
SIDEREAL_DAY_S = 86164.0905
#: Modified Julian Date of the Unix epoch.
MJD_UNIX_EPOCH = 40587.0

#: Measured bounds, recorded so tests can assert against them.
MAX_UT1_UTC_RECENT_S = 0.199
MAX_POLAR_MOTION_ARCSEC = 0.545


class EopUnavailable(RuntimeError):
    """The IERS series is not on disk."""


@lru_cache(maxsize=1)
def _series() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """(MJD, UT1-UTC seconds, x_pole arcsec, y_pole arcsec), rows with UT1-UTC present."""
    if not EOP_FILE.exists():
        raise EopUnavailable(
            f"{EOP_FILE} not found. Download from {EOP_URL} (public domain, ~3.9 MB)."
        )
    import csv

    mjd, dut1, xp, yp = [], [], [], []
    with EOP_FILE.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter=";"):
            try:
                d = float(row["UT1-UTC"])
            except (TypeError, ValueError, KeyError):
                continue
            try:
                mjd.append(float(row["MJD"]))
                dut1.append(d)
                xp.append(float(row["x_pole"]))
                yp.append(float(row["y_pole"]))
            except (TypeError, ValueError, KeyError):
                continue
    if not mjd:
        raise EopUnavailable(f"no usable rows in {EOP_FILE}")
    order = np.argsort(mjd)
    return (
        np.asarray(mjd)[order],
        np.asarray(dut1)[order],
        np.asarray(xp)[order],
        np.asarray(yp)[order],
    )


def datetime64_to_mjd(times: np.ndarray) -> np.ndarray:
    """datetime64 → Modified Julian Date."""
    t = np.atleast_1d(times).astype("datetime64[s]").astype(np.int64)
    return MJD_UNIX_EPOCH + t / 86400.0


def ut1_minus_utc(times: np.ndarray) -> np.ndarray:
    """UT1 − UTC in seconds, linearly interpolated from the IERS series.

    Outside the tabulated range this returns the nearest endpoint rather than
    extrapolating: the series is partly predicted already, and extrapolating a quantity
    that leap seconds reset discontinuously would be worse than clamping.
    """
    mjd, dut1, _, _ = _series()
    return np.interp(datetime64_to_mjd(times), mjd, dut1)


def polar_motion_arcsec(times: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Polar motion (x, y) in arcseconds."""
    mjd, _, xp, yp = _series()
    q = datetime64_to_mjd(times)
    return np.interp(q, mjd, xp), np.interp(q, mjd, yp)


def rotation_error_km(ut1_utc_s: float | np.ndarray) -> np.ndarray:
    """Equatorial position error from treating UTC as UT1, km.

    A time offset becomes a position offset through Earth's rotation: the equator moves
    2*pi*R_E per sidereal day.
    """
    return np.abs(np.asarray(ut1_utc_s, dtype=float)) * RE_KM * 2.0 * np.pi / SIDEREAL_DAY_S


def polar_motion_error_km(x_arcsec: float | np.ndarray, y_arcsec: float | np.ndarray) -> np.ndarray:
    """Surface position error from neglecting polar motion, km."""
    amp = np.hypot(np.asarray(x_arcsec, dtype=float), np.asarray(y_arcsec, dtype=float))
    return amp * (np.pi / 180.0 / 3600.0) * RE_KM


def approximation_bounds(since_mjd: float = 60000.0) -> dict[str, float]:
    """Measured worst case of both approximations over the series from ``since_mjd``.

    Default 60000 is early 2023 — recent enough to describe the regime we operate in,
    rather than the full record whose UT1−UTC excursions are reset by leap seconds.
    """
    mjd, dut1, xp, yp = _series()
    mask = mjd >= since_mjd
    if not np.any(mask):
        raise EopUnavailable(f"no rows at or after MJD {since_mjd}")
    worst_dut1 = float(np.max(np.abs(dut1[mask])))
    worst_pm = float(np.max(np.hypot(xp[mask], yp[mask])))
    return {
        "days": int(mask.sum()),
        "max_ut1_utc_s": worst_dut1,
        "max_rotation_error_km": float(rotation_error_km(worst_dut1)),
        "max_polar_motion_arcsec": worst_pm,
        "max_polar_motion_error_km": float(polar_motion_error_km(worst_pm, 0.0)),
    }
