"""U.S. Standard Atmosphere 1976 (task D-07).

Tracy & Wright integrate their trajectories against this model, so reproducing their
results requires the same one. It also sets the equilibrium glide altitude through
equation 7, which means an error here moves every glide trajectory and every detection
geometry that depends on altitude.

**Geopotential versus geometric altitude.** The 1976 model defines its layers in
*geopotential* altitude H, which absorbs the variation of gravity with height:

    H = r₀·z / (r₀ + z),     r₀ = 6356.766 km

At 57 km geometric that is 56.5 km geopotential — a 0.5 km difference, small but not
negligible when the whole glide-altitude sweep spans 38–57 km. Functions here take
**geometric** altitude by default, because that is what a trajectory integrator carries,
and convert internally. Pass ``geopotential=True`` to supply H directly; published tables
are indexed by H, which is why the validation tests use it.

Valid to 86 km geometric. Above that the 1976 model changes form (molecular composition
varies, the simple lapse-rate layers stop applying) and this implementation stops rather
than extrapolating. The glide regime of interest is 20–60 km, well inside the valid range.
"""

from __future__ import annotations

import numpy as np

#: Effective Earth radius used by the 1976 geopotential definition, metres.
R0_M = 6356766.0

#: Sea-level constants.
G0 = 9.80665          # m/s^2, standard gravity
R_SPECIFIC = 287.053  # J/(kg K), specific gas constant for dry air
T0_K = 288.15
P0_PA = 101325.0
RHO0_KG_M3 = 1.225

#: Upper bound of this implementation, geometric metres.
MAX_ALTITUDE_M = 86000.0

#: Layer base geopotential altitude (m), base temperature (K), lapse rate (K/m),
#: base pressure (Pa). Standard 1976 values.
_LAYERS: tuple[tuple[float, float, float, float], ...] = (
    (0.0, 288.15, -0.0065, 101325.0),
    (11000.0, 216.65, 0.0, 22632.06),
    (20000.0, 216.65, 0.001, 5474.889),
    (32000.0, 228.65, 0.0028, 868.0187),
    (47000.0, 270.65, 0.0, 110.9063),
    (51000.0, 270.65, -0.0028, 66.93887),
    (71000.0, 214.65, -0.002, 3.956420),
)


class AltitudeRangeError(ValueError):
    """Altitude outside the range this implementation is valid for."""


def geometric_to_geopotential(z_m: float | np.ndarray) -> np.ndarray:
    """Geometric altitude → geopotential altitude, metres."""
    z = np.asarray(z_m, dtype=float)
    return R0_M * z / (R0_M + z)


def geopotential_to_geometric(h_m: float | np.ndarray) -> np.ndarray:
    """Geopotential altitude → geometric altitude, metres."""
    h = np.asarray(h_m, dtype=float)
    return R0_M * h / (R0_M - h)


def properties(
    altitude_m: float | np.ndarray, *, geopotential: bool = False
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Temperature (K), pressure (Pa) and density (kg/m³).

    ``altitude_m`` is geometric unless ``geopotential=True``.
    """
    alt = np.asarray(altitude_m, dtype=float)
    h = alt if geopotential else geometric_to_geopotential(alt)

    geometric_max = MAX_ALTITUDE_M
    check = alt if not geopotential else geopotential_to_geometric(alt)
    if np.any(check < -5000.0) or np.any(check > geometric_max):
        raise AltitudeRangeError(
            f"altitude outside [-5, {geometric_max / 1000:.0f}] km geometric; "
            "the 1976 model changes form above 86 km and this implementation does not "
            "extrapolate"
        )

    scalar = h.ndim == 0
    h1 = np.atleast_1d(h)
    temperature = np.empty_like(h1)
    pressure = np.empty_like(h1)

    # Each point is handled by exactly the layer it falls inside, the topmost layer
    # extending upward. Masking on `h >= base` alone would also evaluate every lower
    # layer's formula far outside its range, where a negative-lapse layer drives the
    # temperature below zero and the pressure power returns NaN — discarded afterwards,
    # but only after warning and doing the work.
    for i, (base_h, base_t, lapse, base_p) in enumerate(_LAYERS):
        top_h = _LAYERS[i + 1][0] if i + 1 < len(_LAYERS) else np.inf
        mask = (h1 >= base_h) & (h1 < top_h)
        if not np.any(mask):
            continue
        dh = h1[mask] - base_h
        if lapse == 0.0:
            temperature[mask] = base_t
            pressure[mask] = base_p * np.exp(-G0 * dh / (R_SPECIFIC * base_t))
        else:
            t = base_t + lapse * dh
            temperature[mask] = t
            pressure[mask] = base_p * (t / base_t) ** (-G0 / (R_SPECIFIC * lapse))

    # Below the first layer base (negative altitudes) extrapolate the troposphere.
    below = h1 < _LAYERS[0][0]
    if np.any(below):
        base_h, base_t, lapse, base_p = _LAYERS[0]
        t = base_t + lapse * (h1[below] - base_h)
        temperature[below] = t
        pressure[below] = base_p * (t / base_t) ** (-G0 / (R_SPECIFIC * lapse))

    density = pressure / (R_SPECIFIC * temperature)
    if scalar:
        return temperature[0], pressure[0], density[0]
    return temperature, pressure, density


def density(altitude_m: float | np.ndarray, *, geopotential: bool = False) -> np.ndarray:
    """Atmospheric density, kg/m³. The quantity the trajectory model actually needs."""
    return properties(altitude_m, geopotential=geopotential)[2]


def temperature(altitude_m: float | np.ndarray, *, geopotential: bool = False) -> np.ndarray:
    """Atmospheric temperature, K."""
    return properties(altitude_m, geopotential=geopotential)[0]


def pressure(altitude_m: float | np.ndarray, *, geopotential: bool = False) -> np.ndarray:
    """Atmospheric pressure, Pa."""
    return properties(altitude_m, geopotential=geopotential)[1]


def altitude_for_density(
    target_density: float, *, geopotential: bool = False, tol: float = 1e-6
) -> float:
    """Invert the density profile: the altitude at which density equals a target, metres.

    Needed because published analyses state their flight conditions either way round —
    Candler gives ρ = 4.17×10⁻⁴ kg/m³ and says it corresponds to ~57.1 km, which is only
    checkable by inverting. Density falls monotonically through this range, so a bisection
    is safe and needs no derivative.
    """
    if target_density <= 0.0:
        raise ValueError("density must be positive")

    lo, hi = 0.0, MAX_ALTITUDE_M
    if not (density(hi) <= target_density <= density(lo)):
        raise AltitudeRangeError(
            f"density {target_density:g} kg/m^3 is outside the model's range "
            f"[{float(density(hi)):.3g}, {float(density(lo)):.3g}]"
        )

    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if float(density(mid, geopotential=geopotential)) > target_density:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


def scale_height_m(altitude_m: float, *, geopotential: bool = False) -> float:
    """Local density scale height, metres.

    Useful as a sanity number rather than a model input: roughly 7–8 km in the
    troposphere and stratosphere. A detection model that assumes an exponential
    atmosphere is implicitly assuming this is constant, which it is not.
    """
    t = float(temperature(altitude_m, geopotential=geopotential))
    return R_SPECIFIC * t / G0
