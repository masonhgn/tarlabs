"""Solar and lunar geometry: occultation, terminator, exclusion angles (task D-08).

An infrared sensor cannot look wherever it likes. Three geometric constraints gate whether
a detection is even possible, and none of them appear in a coverage calculation that only
tests line of sight:

*   **Earth occultation** — the target is behind the Earth from the sensor's viewpoint.
*   **Solar exclusion** — the line of sight passes too close to the Sun, which saturates or
    blinds the detector. This removes a cone of sky that *moves* through the day.
*   **Terminator and illumination** — whether the target and the background beneath it are
    sunlit. In the shortwave bands (D-04, D-05) reflected sunlight is a major background
    term, so the day/night state changes the detection threshold, not merely the scene.

Positions come from a JPL development ephemeris (DE421) through Skyfield. DE421 covers
1900–2050 and is accurate far beyond anything this study needs; the choice is about having
a real ephemeris rather than a low-precision analytic Sun, because the solar exclusion cone
is a hard geometric gate and an approximate Sun would move it.

Frames: Skyfield works in ICRF/J2000; SGP4 produces TEME. The two differ by precession and
nutation — at the tens-of-kilometres level for a Sun direction at 1 AU this is irrelevant
to an exclusion-angle test, but it is *not* irrelevant if these positions are ever
differenced against satellite positions directly. Use ``sun_direction_*`` for angles, and
convert explicitly if you need a vector difference.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np

_DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
EPHEMERIS_DIR = _DATA_ROOT / "raw" / "ephemeris"
DEFAULT_KERNEL = "de421.bsp"

#: Mean equatorial radius, km. The occultation test uses a spherical Earth: the 21 km
#: equatorial-polar difference is small against the grazing-ray ambiguity introduced by
#: atmospheric refraction, which this model does not attempt.
EARTH_RADIUS_KM = 6378.137

#: Angular radius of the Sun at 1 AU, degrees. Exclusion half-angles are quoted relative
#: to the Sun's centre, so a meaningful exclusion is always larger than this.
SOLAR_ANGULAR_RADIUS_DEG = 0.266


class EphemerisUnavailable(RuntimeError):
    """The ephemeris kernel is not present and could not be loaded."""


@lru_cache(maxsize=2)
def _load(kernel: str = DEFAULT_KERNEL):
    """Load and cache the ephemeris kernel and Skyfield timescale."""
    try:
        from skyfield.api import Loader
    except ImportError as exc:  # pragma: no cover - dependency is declared
        raise EphemerisUnavailable(f"skyfield is not installed: {exc}") from exc

    EPHEMERIS_DIR.mkdir(parents=True, exist_ok=True)
    loader = Loader(str(EPHEMERIS_DIR), verbose=False)
    try:
        eph = loader(kernel)
    except Exception as exc:
        raise EphemerisUnavailable(
            f"could not load {kernel} from {EPHEMERIS_DIR}: {exc}. "
            "It downloads automatically when a network is available."
        ) from exc
    return eph, loader.timescale()


def _skyfield_times(times: np.ndarray):
    """datetime64 array → Skyfield Time."""
    _, ts = _load()
    t = np.atleast_1d(times).astype("datetime64[us]")
    frac = (t - t.astype("datetime64[D]")).astype("timedelta64[us]").astype(np.int64)
    days = t.astype("datetime64[D]").astype(object)
    return ts.utc(
        [d.year for d in days],
        [d.month for d in days],
        [d.day for d in days],
        0,
        0,
        frac / 1e6,
    )


def sun_position_gcrs_km(times: np.ndarray) -> np.ndarray:
    """Sun position relative to Earth's centre, km, shape ``(n_time, 3)``."""
    eph, _ = _load()
    t = _skyfield_times(times)
    vec = (eph["earth"].at(t).observe(eph["sun"]).apparent()).position.km
    return np.atleast_2d(np.asarray(vec).T)


def moon_position_gcrs_km(times: np.ndarray) -> np.ndarray:
    """Moon position relative to Earth's centre, km, shape ``(n_time, 3)``."""
    eph, _ = _load()
    t = _skyfield_times(times)
    vec = (eph["earth"].at(t).observe(eph["moon"]).apparent()).position.km
    return np.atleast_2d(np.asarray(vec).T)


def _unit(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return np.divide(v, n, out=np.zeros_like(v), where=n > 0)


def angle_between_deg(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Angle between two vector fields, degrees.

    Uses ``arctan2`` of the cross and dot products rather than ``arccos`` of the dot: the
    arccos form loses all its precision for nearly-parallel vectors, which is precisely
    the case a solar-exclusion test spends its time evaluating.
    """
    a, b = np.atleast_2d(a), np.atleast_2d(b)
    cross = np.linalg.norm(np.cross(a, b), axis=-1)
    dot = np.einsum("...i,...i->...", a, b)
    return np.degrees(np.arctan2(cross, dot))


def solar_exclusion_angle_deg(
    sensor_pos_km: np.ndarray, target_pos_km: np.ndarray, times: np.ndarray
) -> np.ndarray:
    """Angle between the sensor→target line of sight and the sensor→Sun direction.

    Small values mean the sensor is looking towards the Sun. A detection is rejected when
    this falls below the instrument's exclusion half-angle — a parameter we sweep, since
    real values are not public.
    """
    sensor = np.atleast_2d(sensor_pos_km)
    target = np.atleast_2d(target_pos_km)
    sun = sun_position_gcrs_km(times)
    return angle_between_deg(target - sensor, sun - sensor)


def earth_occulted(
    sensor_pos_km: np.ndarray,
    target_pos_km: np.ndarray,
    *,
    earth_radius_km: float = EARTH_RADIUS_KM,
) -> np.ndarray:
    """True where the Earth blocks the sensor→target line of sight.

    Tests the perpendicular distance from Earth's centre to the *segment* between sensor
    and target, not to the infinite line. The distinction matters: the infinite line
    through two satellites on the same side of the Earth passes close to the centre on the
    far side, and an infinite-line test would report an occultation that does not exist.
    """
    p0 = np.atleast_2d(np.asarray(sensor_pos_km, dtype=float))
    p1 = np.atleast_2d(np.asarray(target_pos_km, dtype=float))
    d = p1 - p0
    denom = np.einsum("...i,...i->...", d, d)

    # Parameter of the closest approach to the origin, clamped to the segment.
    s = np.divide(
        -np.einsum("...i,...i->...", p0, d), denom, out=np.zeros(denom.shape), where=denom > 0
    )
    s = np.clip(s, 0.0, 1.0)
    closest = p0 + s[..., None] * d
    return np.linalg.norm(closest, axis=-1) < earth_radius_km


def is_sunlit(position_km: np.ndarray, times: np.ndarray) -> np.ndarray:
    """True where a point is outside Earth's shadow.

    A cylindrical shadow model: adequate for deciding whether a target is illuminated, and
    deliberately not a penumbra model. Refraction and the penumbral gradient matter for
    photometry, not for a trade study's illumination flag — but the simplification is
    stated rather than implied.
    """
    pos = np.atleast_2d(np.asarray(position_km, dtype=float))
    sun_dir = _unit(sun_position_gcrs_km(times))
    along = np.einsum("...i,...i->...", pos, sun_dir)
    perp = np.linalg.norm(pos - along[..., None] * sun_dir, axis=-1)
    # In shadow only when behind the Earth (anti-sunward) AND inside the shadow cylinder.
    return ~((along < 0.0) & (perp < EARTH_RADIUS_KM))


def solar_zenith_angle_deg(
    lat_deg: np.ndarray, lon_deg: np.ndarray, times: np.ndarray
) -> np.ndarray:
    """Solar zenith angle at a point on the Earth's surface, degrees.

    90° is the terminator; greater than 90° is night. This sets whether the *background*
    beneath a target is sunlit, which in the shortwave bands changes the detection
    threshold rather than merely the appearance of the scene.
    """
    from .propagate import gmst_rad

    lat = np.radians(np.atleast_1d(lat_deg))
    lon = np.radians(np.atleast_1d(lon_deg))
    theta = gmst_rad(np.atleast_1d(times))

    # Surface normal in an inertial frame: rotate the geodetic direction by GMST.
    right_ascension = lon + theta
    normal = np.stack(
        [np.cos(lat) * np.cos(right_ascension),
         np.cos(lat) * np.sin(right_ascension),
         np.sin(lat) * np.ones_like(right_ascension)],
        axis=-1,
    )
    return angle_between_deg(normal, _unit(sun_position_gcrs_km(times)))
