"""Earth-limb geometry and slant atmospheric path (task D-17).

D-08 answered the *geometric* visibility question — is the Earth in the way. This module
answers the radiometric one: **how much atmosphere does the line of sight actually cross**,
and therefore whether Tracy & Wright's decision to neglect atmospheric attenuation
(D-04, open item D-04-c) survives contact with our geometry.

It does not, in general. The short version:

* Their justification assumes an observer **directly overhead**.
* A wide field of regard — which CSIS shows is *required* for persistent global coverage —
  puts most of the constellation at large off-nadir angles.
* At those angles the slant path carries an order of magnitude more air mass than the
  vertical one.

So the coverage-optimal architecture is precisely the one where the neglect-attenuation
assumption is weakest. That is a coupling between coverage geometry and radiometry that
neither the CSIS coverage study nor the Tracy & Wright signature work had reason to
examine, because neither was doing the other's problem.
"""

from __future__ import annotations

import numpy as np

from . import atmosphere as atm

#: Earth mean equatorial radius, km.
RE_KM = 6378.137

#: Above this altitude the 1976 model stops and the remaining column is negligible anyway.
ATMOSPHERE_TOP_KM = 86.0


def target_zenith_from_off_nadir_deg(
    off_nadir_deg: float | np.ndarray,
    *,
    satellite_altitude_km: float = 1000.0,
    target_altitude_km: float = 45.0,
) -> np.ndarray:
    """Zenith angle at the target, given the sensor's off-nadir pointing angle.

    Law of sines on the triangle (Earth centre, satellite, target):

        sin(zenith) = (r_sat / r_target) · sin(off_nadir)

    Since ``r_sat > r_target`` the zenith angle is always **larger** than the off-nadir
    angle, and the amplification grows sharply near the limb. This is the step that turns
    a modest-sounding sensor pointing angle into a near-horizontal view through the
    atmosphere.
    """
    r_s = RE_KM + satellite_altitude_km
    r_t = RE_KM + target_altitude_km
    s = (r_s / r_t) * np.sin(np.radians(np.asarray(off_nadir_deg, dtype=float)))
    return np.degrees(np.arcsin(np.clip(s, -1.0, 1.0)))


def max_off_nadir_deg(
    *, satellite_altitude_km: float = 1000.0, target_altitude_km: float = 45.0
) -> float:
    """Largest off-nadir angle that can still reach a target at the given altitude.

    Beyond this the line of sight is tangent to the target's shell and never reaches it.
    For a 45 km target seen from 1,000 km this is 60.5°, i.e. a full field of regard of
    121° — which independently reproduces CSIS's statement that Earth curvature limits
    useful field of regard beyond about 120 degrees.
    """
    r_s = RE_KM + satellite_altitude_km
    r_t = RE_KM + target_altitude_km
    return float(np.degrees(np.arcsin(min(1.0, r_t / r_s))))


def tangent_altitude_km(
    origin_altitude_km: float, zenith_deg: float
) -> float:
    """Lowest altitude a straight ray reaches, km.

    For zenith angles below 90° the ray climbs immediately and the tangent altitude is the
    origin altitude. Above 90° it descends first, and the tangent altitude is where it
    turns — which is what decides whether a grazing path is an atmospheric path or an
    occultation.
    """
    r0 = RE_KM + origin_altitude_km
    z = np.radians(zenith_deg)
    if zenith_deg <= 90.0:
        return float(origin_altitude_km)
    return float(r0 * np.sin(np.pi - z) - RE_KM)


def slant_column_kg_m2(
    origin_altitude_km: float,
    zenith_deg: float,
    *,
    top_km: float = ATMOSPHERE_TOP_KM,
    samples: int = 4000,
    max_path_km: float = 3000.0,
) -> float:
    """Integrated air mass along a straight ray leaving the target, kg/m².

    This is the quantity attenuation scales with. A straight ray is assumed — refraction
    is neglected, which matters only within a degree or so of the horizon and is noted
    rather than modelled.
    """
    r0 = RE_KM + origin_altitude_km
    z = np.radians(zenith_deg)
    s = np.linspace(0.0, max_path_km, samples)
    r = np.sqrt(r0**2 + s**2 + 2.0 * r0 * s * np.cos(z))
    altitude = r - RE_KM

    inside = (altitude <= top_km) & (altitude >= -0.5)
    if not np.any(inside):
        return 0.0
    rho = atm.density(np.clip(altitude[inside], 0.0, top_km) * 1000.0)
    return float(np.trapezoid(rho, s[inside] * 1000.0))


def airmass_ratio(origin_altitude_km: float, zenith_deg: float) -> float:
    """Slant column divided by the vertical column from the same altitude.

    Approximately ``sec(z)`` until curvature takes over near the limb. Reporting the ratio
    rather than the absolute column makes it directly comparable to the "overhead
    observer" assumption it tests.
    """
    vertical = slant_column_kg_m2(origin_altitude_km, 0.0)
    if vertical <= 0:
        return float("nan")
    return slant_column_kg_m2(origin_altitude_km, zenith_deg) / vertical


def attenuation_assumption_holds(
    *,
    target_altitude_km: float,
    off_nadir_deg: float,
    satellite_altitude_km: float = 1000.0,
    tolerance_ratio: float = 2.0,
) -> bool:
    """Whether "neglect atmospheric attenuation" is defensible for this geometry.

    Tracy & Wright justify neglecting attenuation for an observer directly overhead at
    typical glide altitudes. We accept that justification only where the slant column
    stays within ``tolerance_ratio`` of the vertical one; beyond that the geometry differs
    from the one the justification was made for, and the assumption has to be re-earned
    rather than inherited.
    """
    z = float(
        target_zenith_from_off_nadir_deg(
            off_nadir_deg,
            satellite_altitude_km=satellite_altitude_km,
            target_altitude_km=target_altitude_km,
        )
    )
    return airmass_ratio(target_altitude_km, z) <= tolerance_ratio
