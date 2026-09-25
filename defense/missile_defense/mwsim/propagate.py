"""SGP4/SDP4 propagation and frame conversion (task S-03).

Everything downstream — coverage, stereo availability, detection geometry, tracking,
fusion placement — sits on top of this module, so it is the one place where being wrong is
unrecoverable. It is gated by tests/test_propagation.py against Vallado's published SGP4
verification vectors.

**Accuracy, stated plainly because the proposal has to state it plainly.** TLE/OMM mean
elements propagated with SGP4 carry roughly 1 km of position error at epoch, growing about
1-3 km per day away from it. Mean elements cannot be converted to osculating elements
without error, so they must be propagated with a simplified-perturbations model and nothing
else. A one-second time error is about 7 km of position error in LEO, so time handling is
not a detail. This fidelity is entirely adequate for a trade study over notional geometry
and entirely inadequate for fire control; the proposal says so in those words.

Frames: SGP4 natively produces TEME (True Equator, Mean Equinox) of date. ``teme_to_ecef``
rotates about the pole by Greenwich Mean Sidereal Time, neglecting polar motion and the
equation-of-equinoxes correction between TEME and PEF. Polar motion is **measured** at no
more than 0.545 arcsec — 17 m of surface displacement — against the IERS series (task
D-15), some sixty times below the SGP4 error we already accept. Bounded rather than merely
asserted; see `mwsim.earth_orientation`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import numpy as np
from sgp4 import omm
from sgp4.api import SGP4_ERRORS, Satrec, SatrecArray, jday

from .catalog import OmmRecord

#: WGS-84, the ellipsoid the geodetic conversion assumes.
WGS84_A_KM = 6378.137
WGS84_F = 1.0 / 298.257223563
WGS84_B_KM = WGS84_A_KM * (1.0 - WGS84_F)
WGS84_E2 = WGS84_F * (2.0 - WGS84_F)

#: Nominal geostationary radius, for the S-03 sanity check.
GEO_RADIUS_KM = 42164.0


class PropagationError(RuntimeError):
    """SGP4 reported an error code for every step of a requested propagation."""


@dataclass(frozen=True)
class Ephemeris:
    """A propagated track: positions and velocities on a shared time grid.

    Shapes are ``(n_sat, n_time, 3)`` for the vectors and ``(n_sat, n_time)`` for the mask,
    so a one-satellite ephemeris still has a leading axis of 1. Keeping the rank fixed
    stops the coverage code from growing special cases.
    """

    norad_ids: np.ndarray       # (n_sat,)  int
    times: np.ndarray           # (n_time,) datetime64[us], UTC
    position_teme_km: np.ndarray    # (n_sat, n_time, 3)
    velocity_teme_km_s: np.ndarray  # (n_sat, n_time, 3)
    valid: np.ndarray           # (n_sat, n_time) bool — False where SGP4 errored

    def __post_init__(self) -> None:
        n_sat, n_time = len(self.norad_ids), len(self.times)
        expected = (n_sat, n_time, 3)
        if self.position_teme_km.shape != expected:
            raise ValueError(
                f"position shape {self.position_teme_km.shape} != expected {expected}"
            )
        if self.velocity_teme_km_s.shape != expected:
            raise ValueError(
                f"velocity shape {self.velocity_teme_km_s.shape} != expected {expected}"
            )
        if self.valid.shape != (n_sat, n_time):
            raise ValueError(f"valid shape {self.valid.shape} != expected {(n_sat, n_time)}")

    @property
    def n_sat(self) -> int:
        return len(self.norad_ids)

    @property
    def n_time(self) -> int:
        return len(self.times)

    def radius_km(self) -> np.ndarray:
        """Geocentric radius, ``(n_sat, n_time)``."""
        return np.linalg.norm(self.position_teme_km, axis=-1)

    def index_of(self, norad_id: int) -> int:
        matches = np.flatnonzero(self.norad_ids == norad_id)
        if matches.size == 0:
            raise KeyError(f"NORAD {norad_id} is not in this ephemeris")
        return int(matches[0])

    def select(self, norad_id: int) -> "Ephemeris":
        """A single-satellite view, keeping the rank-3 shape."""
        i = self.index_of(norad_id)
        return Ephemeris(
            norad_ids=self.norad_ids[i : i + 1],
            times=self.times,
            position_teme_km=self.position_teme_km[i : i + 1],
            velocity_teme_km_s=self.velocity_teme_km_s[i : i + 1],
            valid=self.valid[i : i + 1],
        )


def satrec_from_omm(record: OmmRecord) -> Satrec:
    """Build an SGP4 satellite record from an OMM record.

    Works for both SGP4 (near-earth) and SDP4 (deep-space, i.e. our GEO layer); the library
    selects the model from the mean motion.
    """
    sat = Satrec()
    omm.initialize(sat, record.fields)
    return sat


def satrec_epoch(sat: Satrec) -> datetime:
    """The element-set epoch of an initialised Satrec, as a UTC datetime.

    Useful for anchoring a time grid to a satellite rather than to a hand-typed date, which
    is the difference between propagating from epoch and propagating from an arbitrary
    offset that happens to look right.
    """
    jd = sat.jdsatepoch + sat.jdsatepochF
    # Fliegel-Van Flandern, via the standard Julian-day inverse.
    z = int(jd + 0.5)
    frac = (jd + 0.5) - z
    alpha = int((z - 1867216.25) / 36524.25)
    a = z + 1 + alpha - alpha // 4 if z >= 2299161 else z
    b = a + 1524
    c = int((b - 122.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6001)
    day = b - d - int(30.6001 * e) + frac
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    whole_day = int(day)
    seconds = (day - whole_day) * 86400.0
    return datetime(year, month, whole_day, tzinfo=timezone.utc) + timedelta(seconds=seconds)


def time_grid(
    start: datetime,
    duration: timedelta,
    step: timedelta,
) -> np.ndarray:
    """A UTC time grid as ``datetime64[us]``.

    Step size is a swept parameter in the coverage study: too coarse and short accesses are
    missed, too fine and the sweeps stop fitting in the schedule.
    """
    if step <= timedelta(0):
        raise ValueError("step must be positive")
    if duration < timedelta(0):
        raise ValueError("duration must not be negative")
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    start_utc = start.astimezone(timezone.utc).replace(tzinfo=None)
    n = int(duration / step) + 1
    base = np.datetime64(start_utc, "us")
    offsets = (np.arange(n, dtype=np.int64) * int(step / timedelta(microseconds=1)))
    return base + offsets.astype("timedelta64[us]")


def _julian_dates(times: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Split a datetime64 grid into SGP4's (whole-day, fractional-day) Julian pair.

    The split is what keeps the arithmetic well conditioned: a single float64 Julian date
    resolves to roughly 20 microseconds, and at LEO speeds time error is position error.
    """
    days = times.astype("datetime64[D]")
    micros = (times - days).astype("timedelta64[us]").astype(np.int64)

    jd = np.empty(times.shape, dtype=np.float64)
    fr = np.empty(times.shape, dtype=np.float64)
    for i, day in enumerate(days):
        d = day.astype(object)
        jd_i, _ = jday(d.year, d.month, d.day, 0, 0, 0.0)
        jd[i] = jd_i
    fr[:] = micros / 86_400_000_000.0
    return jd, fr


def propagate(satrecs: dict[int, Satrec], times: np.ndarray) -> Ephemeris:
    """Propagate a set of satellites over a shared time grid.

    Steps SGP4 flags as errored are marked invalid and filled with NaN rather than dropped,
    so the time axis stays aligned across satellites. A satellite that fails at *every*
    step is a real problem and raises.
    """
    if not satrecs:
        raise ValueError("no satellites to propagate")

    norad_ids = np.array(sorted(satrecs), dtype=np.int64)
    ordered = [satrecs[int(n)] for n in norad_ids]
    jd, fr = _julian_dates(times)

    errors, positions, velocities = SatrecArray(ordered).sgp4(jd, fr)

    valid = errors == 0
    positions = np.where(valid[..., None], positions, np.nan)
    velocities = np.where(valid[..., None], velocities, np.nan)

    dead = ~valid.any(axis=1)
    if dead.any():
        first = int(np.flatnonzero(dead)[0])
        code = int(errors[first].flat[0])
        reason = SGP4_ERRORS.get(code, f"code {code}")
        raise PropagationError(
            f"NORAD {int(norad_ids[first])} failed at every step: {reason}"
        )

    return Ephemeris(
        norad_ids=norad_ids,
        times=times,
        position_teme_km=positions,
        velocity_teme_km_s=velocities,
        valid=valid,
    )


def propagate_records(records: dict[int, OmmRecord], times: np.ndarray) -> Ephemeris:
    """Convenience wrapper: OMM records straight to an ephemeris."""
    return propagate({k: satrec_from_omm(v) for k, v in records.items()}, times)


def gmst_rad(times: np.ndarray) -> np.ndarray:
    """Greenwich Mean Sidereal Time, IAU-82, radians in [0, 2*pi).

    UT1 is approximated by UTC. **Measured** against the IERS finals2000A series (task
    D-15): |UT1-UTC| reaches 0.199 s from 2023 onward, which is at most **90 m** of
    Earth-rotation error at the equator — roughly ten times below the ~1 km SGP4 error
    floor. See `mwsim.earth_orientation`, which provides the lookup if this ever needs
    correcting.

    (An earlier version of this note quoted ~0.4 km, reasoning from the 0.9 s leap-second
    bound. That is right as a historical worst case — the full IERS record reaches 0.81 s,
    or ~370 m — but pessimistic by about 4x for current epochs.)
    """
    jd, fr = _julian_dates(times)
    t = ((jd - 2451545.0) + fr) / 36525.0
    # Vallado, Fundamentals of Astrodynamics and Applications, eq. 3-47 (seconds).
    seconds = (
        67310.54841
        + (876600.0 * 3600.0 + 8640184.812866) * t
        + 0.093104 * t * t
        - 6.2e-6 * t * t * t
    )
    return np.deg2rad((seconds / 240.0) % 360.0)


def teme_to_ecef(position_teme_km: np.ndarray, times: np.ndarray) -> np.ndarray:
    """Rotate TEME positions into an Earth-fixed frame.

    Polar motion and the TEME-to-PEF equation-of-equinoxes term are neglected; see the
    module docstring. ``position_teme_km`` is ``(..., n_time, 3)``.
    """
    theta = gmst_rad(times)
    cos_t, sin_t = np.cos(theta), np.sin(theta)
    x, y, z = (
        position_teme_km[..., 0],
        position_teme_km[..., 1],
        position_teme_km[..., 2],
    )
    return np.stack(
        [x * cos_t + y * sin_t, -x * sin_t + y * cos_t, z],
        axis=-1,
    )


def ecef_to_geodetic(position_ecef_km: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """WGS-84 geodetic latitude (deg), longitude (deg), altitude (km).

    Bowring's closed-form method: accurate to well under a millimetre for any altitude we
    care about, and free of the convergence checks an iterative solution would need.
    """
    x, y, z = position_ecef_km[..., 0], position_ecef_km[..., 1], position_ecef_km[..., 2]
    lon = np.arctan2(y, x)

    p = np.hypot(x, y)
    ep2 = (WGS84_A_KM**2 - WGS84_B_KM**2) / WGS84_B_KM**2
    beta = np.arctan2(WGS84_A_KM * z, WGS84_B_KM * p)
    lat = np.arctan2(
        z + ep2 * WGS84_B_KM * np.sin(beta) ** 3,
        p - WGS84_E2 * WGS84_A_KM * np.cos(beta) ** 3,
    )
    n = WGS84_A_KM / np.sqrt(1.0 - WGS84_E2 * np.sin(lat) ** 2)

    # Near the poles p -> 0 and the h = p/cos(lat) - N form loses all its precision, so
    # switch to the z/sin(lat) form there. Both branches are evaluated, so both
    # denominators are floored away from zero first: the guarded branch is discarded, but
    # an unguarded divide would still raise a warning and produce a NaN.
    cos_lat, sin_lat = np.cos(lat), np.sin(lat)
    near_equator = np.abs(cos_lat) > 1e-6
    alt_equatorial = p / np.where(near_equator, cos_lat, 1.0) - n
    alt_polar = np.abs(z) / np.where(near_equator, 1.0, np.abs(sin_lat)) - n * (1.0 - WGS84_E2)
    alt = np.where(near_equator, alt_equatorial, alt_polar)

    return np.rad2deg(lat), np.rad2deg(lon), alt


def mean_altitude_km(eph: Ephemeris) -> np.ndarray:
    """Mean geodetic altitude per satellite, ``(n_sat,)``. NaN-safe."""
    ecef = teme_to_ecef(eph.position_teme_km, eph.times)
    _, _, alt = ecef_to_geodetic(ecef)
    return np.nanmean(alt, axis=1)


def inclination_deg(satrecs: dict[int, Satrec]) -> dict[int, float]:
    """Mean inclination straight from the element sets, in degrees."""
    return {k: float(np.rad2deg(v.inclo)) for k, v in satrecs.items()}


def revs_per_day(satrecs: dict[int, Satrec]) -> dict[int, float]:
    """Mean motion in revolutions per day, straight from the element sets."""
    return {k: float(v.no_kozai * 1440.0 / (2.0 * np.pi)) for k, v in satrecs.items()}
