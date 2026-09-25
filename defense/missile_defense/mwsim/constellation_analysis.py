"""Measure real constellation plane structure from catalogue elements (task D-02).

Published fact sheets describe architectures in round numbers — "two orbital planes",
"approximately 1000 km", "80 degrees". The catalogue holds what was actually flown. This
module recovers plane membership, plane spacing and insertion geometry from the elements
themselves, so the Walker generator (S-04) can be seeded from measurement rather than from
a press release.

It also provides the J2 nodal-regression rate, which is what explains why satellites that
changed altitude drift out of the plane they launched into. That drift is an independent
observable for the manoeuvre finding in D-14: altitude and RAAN are different measurements,
and both have to agree.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

#: WGS-84 / standard gravitational constants.
J2 = 1.08263e-3
RE_KM = 6378.137
MU_KM3_S2 = 398600.4418


def nodal_regression_deg_per_day(
    semi_major_km: float | np.ndarray,
    inclination_deg: float | np.ndarray,
    eccentricity: float | np.ndarray = 0.0,
) -> float | np.ndarray:
    """Secular J2 regression of the right ascension of the ascending node, deg/day.

        dΩ/dt = −(3/2) · n · J2 · (Rₑ/a)² · cos i / (1−e²)²

    Negative for prograde orbits: the node regresses westward. The rate depends on
    altitude, so two satellites that share a plane will separate in RAAN if one of them
    changes its semi-major axis — which is exactly what makes this a useful independent
    check on a manoeuvre hypothesis.
    """
    a = np.asarray(semi_major_km, dtype=float)
    n_deg_per_day = np.sqrt(MU_KM3_S2 / a**3) * 86400.0 * 180.0 / np.pi
    return (
        -1.5
        * n_deg_per_day
        * J2
        * (RE_KM / a) ** 2
        * np.cos(np.radians(inclination_deg))
        / (1.0 - np.asarray(eccentricity, dtype=float) ** 2) ** 2
    )


@dataclass
class OrbitalPlane:
    """A cluster of satellites sharing an ascending node and inclination."""

    raan_deg: float
    inclination_deg: float
    members: list[str] = field(default_factory=list)
    altitudes_km: list[float] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.members)

    @property
    def mean_altitude_km(self) -> float:
        return float(np.mean(self.altitudes_km)) if self.altitudes_km else float("nan")

    @property
    def raan_spread_deg(self) -> float:
        return float(np.ptp(self._raans)) if len(self._raans) > 1 else 0.0

    _raans: list[float] = field(default_factory=list, repr=False)


def cluster_planes(
    satellites: list[tuple[str, float, float, float]],
    *,
    raan_tolerance_deg: float = 10.0,
    inclination_tolerance_deg: float = 3.0,
) -> list[OrbitalPlane]:
    """Group satellites into orbital planes by RAAN and inclination.

    ``satellites`` is a list of ``(name, raan_deg, inclination_deg, altitude_km)``.

    Clustering is on RAAN modulo 360 with wrap handled, and requires matching inclination:
    two groups can share an ascending node while flying completely different orbits, and
    merging them would invent a plane that does not exist. Satellites that match no cluster
    become single-member planes rather than being dropped — an outlier is a finding, not
    noise, as the Tranche 0 tracking satellites demonstrate.
    """
    planes: list[OrbitalPlane] = []

    for name, raan, inc, alt in sorted(satellites, key=lambda s: s[1]):
        placed = False
        for plane in planes:
            dr = abs((raan - plane.raan_deg + 180.0) % 360.0 - 180.0)
            di = abs(inc - plane.inclination_deg)
            if dr <= raan_tolerance_deg and di <= inclination_tolerance_deg:
                plane._raans.append(raan)
                # Circular mean keeps the centre correct across the 0/360 wrap.
                ang = np.radians(plane._raans)
                plane.raan_deg = float(
                    np.degrees(np.arctan2(np.sin(ang).mean(), np.cos(ang).mean())) % 360.0
                )
                plane.inclination_deg = float(
                    np.mean([plane.inclination_deg] * (plane.count) + [inc])
                )
                plane.members.append(name)
                plane.altitudes_km.append(alt)
                placed = True
                break
        if not placed:
            planes.append(
                OrbitalPlane(
                    raan_deg=raan,
                    inclination_deg=inc,
                    members=[name],
                    altitudes_km=[alt],
                    _raans=[raan],
                )
            )

    return sorted(planes, key=lambda p: (-p.count, p.raan_deg))


def predicted_raan_separation(
    epochs: np.ndarray,
    semi_major_km: np.ndarray,
    inclination_deg: np.ndarray,
    eccentricity: np.ndarray,
    ref_epochs: np.ndarray,
    ref_semi_major_km: np.ndarray,
    ref_inclination_deg: np.ndarray,
    ref_eccentricity: np.ndarray,
) -> np.ndarray:
    """Cumulative RAAN separation predicted by differential J2 regression, degrees.

    Integrates the difference in nodal-regression rate between a satellite and a reference
    satellite over the satellite's own altitude history. If a satellite left its plane
    purely because it changed altitude, this reproduces the observed separation; a residual
    would mean something else moved it.
    """
    days = ((epochs - epochs[0]) / np.timedelta64(1, "D")).astype(float)
    ref_days = ((ref_epochs - epochs[0]) / np.timedelta64(1, "D")).astype(float)

    rate = nodal_regression_deg_per_day(semi_major_km, inclination_deg, eccentricity)
    ref_rate = np.interp(
        days,
        ref_days,
        nodal_regression_deg_per_day(
            ref_semi_major_km, ref_inclination_deg, ref_eccentricity
        ),
    )
    return np.cumsum(np.diff(days, prepend=days[0]) * (rate - ref_rate))
