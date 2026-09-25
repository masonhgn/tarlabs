"""Walker constellation generation (task S-04).

Builds the notional constellations the trade study compares. Two rules govern it, both
earned during Phase D rather than assumed:

**Seed from measurement, not from press releases (DEC-19).** SDA publishes "approximately
1000 km" and "80 degrees". The catalogue says the Tranche 0 vehicles were inserted at
**943 km** and **81.00°**, and that the two polar planes are **65°** apart in right
ascension — not the 90° an even two-plane Walker would use. A generator seeded from the
fact sheet produces a different constellation from the real one, and coverage is exactly
what that error corrupts.

**Label notional as notional (DEC-11).** Architecture documents and catalogue geometry
answer different questions. Anything generated here is a design, not an observation, and
carries a flag saying so.

## Walker notation

A Walker pattern is written ``i: T/P/F``:

* ``T`` total satellites, ``P`` planes, ``T/P`` satellites per plane
* ``F`` the phasing parameter, 0 ≤ F ≤ P−1, which sets how far the satellites in one plane
  are offset from those in the next

Two spreads exist and the difference matters for polar work:

* **Delta** — planes spread over a full 360° of right ascension. Standard for
  mid-inclination constellations.
* **Star** — planes spread over 180°. Used for near-polar constellations, because a plane
  at RAAN Ω and one at Ω+180° trace the *same* ground track in opposite directions; a delta
  pattern at high inclination therefore wastes half its planes. SDA's near-polar tracking
  layer is a star-type arrangement.

Getting that wrong halves the effective plane count, which is not a subtle coverage error.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

MU_KM3_S2 = 398600.4418
RE_KM = 6378.137
J2 = 1.08263e-3

#: Measured Tranche 0 insertion geometry (D-02). Use these, not the published round numbers.
T0_MEASURED_ALTITUDE_KM = 943.0
T0_MEASURED_INCLINATION_DEG = 81.00
T0_MEASURED_PLANE_SEPARATION_DEG = 65.0


@dataclass(frozen=True)
class Satellite:
    """One notional satellite, by its Keplerian elements."""

    name: str
    semi_major_axis_km: float
    inclination_deg: float
    raan_deg: float
    mean_anomaly_deg: float
    plane: int
    slot: int
    eccentricity: float = 0.0
    arg_perigee_deg: float = 0.0

    @property
    def altitude_km(self) -> float:
        return self.semi_major_axis_km - RE_KM

    @property
    def period_s(self) -> float:
        return 2.0 * np.pi * np.sqrt(self.semi_major_axis_km**3 / MU_KM3_S2)

    @property
    def mean_motion_rev_per_day(self) -> float:
        return 86400.0 / self.period_s


@dataclass
class Constellation:
    """A set of satellites, real or notional, with its provenance attached."""

    name: str
    satellites: list[Satellite] = field(default_factory=list)
    #: False only for constellations seeded entirely from catalogued elements.
    notional: bool = True
    provenance: str = ""

    def __len__(self) -> int:
        return len(self.satellites)

    @property
    def n_planes(self) -> int:
        return len({s.plane for s in self.satellites})

    @property
    def altitudes_km(self) -> np.ndarray:
        return np.array([s.altitude_km for s in self.satellites])

    def describe(self) -> str:
        tag = "NOTIONAL" if self.notional else "measured"
        alt = self.altitudes_km
        inc = {round(s.inclination_deg, 1) for s in self.satellites}
        return (
            f"{self.name}: {len(self)} sats, {self.n_planes} planes, "
            f"{alt.min():.0f}-{alt.max():.0f} km, incl {sorted(inc)} [{tag}]"
        )

    def merge(self, other: "Constellation", name: str | None = None) -> "Constellation":
        """Combine two layers into one multi-orbit constellation."""
        offset = max((s.plane for s in self.satellites), default=-1) + 1
        shifted = [
            Satellite(
                s.name, s.semi_major_axis_km, s.inclination_deg, s.raan_deg,
                s.mean_anomaly_deg, s.plane + offset, s.slot, s.eccentricity,
                s.arg_perigee_deg,
            )
            for s in other.satellites
        ]
        return Constellation(
            name=name or f"{self.name} + {other.name}",
            satellites=self.satellites + shifted,
            notional=self.notional or other.notional,
            provenance=f"({self.provenance}) + ({other.provenance})",
        )


def walker(
    *,
    name: str,
    total: int,
    planes: int,
    phasing: int,
    altitude_km: float,
    inclination_deg: float,
    pattern: str = "delta",
    raan_offset_deg: float = 0.0,
    raan_spread_deg: float | None = None,
    provenance: str = "",
) -> Constellation:
    """Generate a Walker constellation, ``i: T/P/F``.

    ``raan_spread_deg`` overrides the pattern's default spread. That is how a *measured*
    plane separation gets used instead of an assumed-even one: Tranche 0's two polar planes
    sit 65° apart, and passing ``raan_spread_deg=130`` for two planes reproduces that
    rather than the 180° a star pattern would impose.
    """
    if total <= 0 or planes <= 0:
        raise ValueError("total and planes must be positive")
    if total % planes:
        raise ValueError(f"{total} satellites do not divide evenly into {planes} planes")
    if not 0 <= phasing <= planes - 1:
        raise ValueError(f"phasing must be within 0..{planes - 1}, got {phasing}")

    if raan_spread_deg is None:
        if pattern == "delta":
            raan_spread_deg = 360.0
        elif pattern == "star":
            raan_spread_deg = 180.0
        else:
            raise ValueError(f"pattern must be 'delta' or 'star', got {pattern!r}")

    per_plane = total // planes
    a = RE_KM + altitude_km
    sats: list[Satellite] = []

    for p in range(planes):
        raan = (raan_offset_deg + p * raan_spread_deg / planes) % 360.0
        for s in range(per_plane):
            # In-plane spacing, plus the inter-plane phase offset that F controls.
            mean_anomaly = (
                s * 360.0 / per_plane + p * phasing * 360.0 / total
            ) % 360.0
            sats.append(
                Satellite(
                    name=f"{name}-P{p + 1}S{s + 1}",
                    semi_major_axis_km=a,
                    inclination_deg=inclination_deg,
                    raan_deg=raan,
                    mean_anomaly_deg=mean_anomaly,
                    plane=p,
                    slot=s,
                )
            )

    return Constellation(
        name=f"{name} ({inclination_deg:.0f}deg: {total}/{planes}/{phasing})",
        satellites=sats,
        notional=True,
        provenance=provenance or f"Walker {pattern}, {altitude_km:.0f} km",
    )


def nodal_precession_deg_per_day(
    semi_major_axis_km: float, inclination_deg: float, eccentricity: float = 0.0
) -> float:
    """J2 secular RAAN drift. Shared with `constellation_analysis` for consistency."""
    n = np.sqrt(MU_KM3_S2 / semi_major_axis_km**3) * 86400.0 * 180.0 / np.pi
    return (
        -1.5 * n * J2 * (RE_KM / semi_major_axis_km) ** 2
        * np.cos(np.radians(inclination_deg)) / (1.0 - eccentricity**2) ** 2
    )


def propagate_kepler(
    constellation: Constellation, seconds: np.ndarray, *, apply_j2: bool = True
) -> np.ndarray:
    """Positions in an Earth-centred inertial frame, ``(n_sat, n_time, 3)`` km.

    Two-body motion with optional J2 nodal precession. **Deliberately not SGP4**: these are
    notional designs, not catalogued objects, and SGP4's value is in reproducing the
    drag-and-perturbation model fitted to a real element set. For a design there is no
    element set to reproduce, and circular two-body plus J2 is both sufficient and easier
    to defend.

    Circular orbits only — every constellation we generate is circular, and pretending
    otherwise would invite a question we have no answer for.
    """
    t = np.atleast_1d(np.asarray(seconds, dtype=float))
    out = np.empty((len(constellation), len(t), 3))

    for i, sat in enumerate(constellation.satellites):
        a = sat.semi_major_axis_km
        n = np.sqrt(MU_KM3_S2 / a**3)                      # rad/s
        m = np.radians(sat.mean_anomaly_deg) + n * t       # circular: M = true anomaly

        raan = np.radians(sat.raan_deg)
        if apply_j2:
            rate = np.radians(
                nodal_precession_deg_per_day(a, sat.inclination_deg, sat.eccentricity)
            )
            raan = raan + rate * t / 86400.0

        inc = np.radians(sat.inclination_deg)
        # Perifocal position, then rotate by argument of latitude, inclination, RAAN.
        x_p, y_p = a * np.cos(m), a * np.sin(m)
        cos_r, sin_r = np.cos(raan), np.sin(raan)
        cos_i, sin_i = np.cos(inc), np.sin(inc)

        out[i, :, 0] = x_p * cos_r - y_p * cos_i * sin_r
        out[i, :, 1] = x_p * sin_r + y_p * cos_i * cos_r
        out[i, :, 2] = y_p * sin_i

    return out


# -- reference architectures -------------------------------------------------


def tranche0_tracking_measured() -> Constellation:
    """Tranche 0 Tracking as *measured*, not as published (DEC-19).

    Two near-polar planes 65° apart at 943 km and 81.00°, plus the mid-inclination group
    at ~40°. This is what was actually flown, and it is the seed the trade study starts
    from rather than the fact sheet's round numbers.
    """
    polar = walker(
        name="T0-polar",
        total=4, planes=2, phasing=0,
        altitude_km=T0_MEASURED_ALTITUDE_KM,
        inclination_deg=T0_MEASURED_INCLINATION_DEG,
        raan_spread_deg=2 * T0_MEASURED_PLANE_SEPARATION_DEG,
        provenance="measured insertion geometry, D-02",
    )
    mid = walker(
        name="T0-mid",
        total=4, planes=1, phasing=0,
        altitude_km=998.0, inclination_deg=40.0,
        provenance="measured, D-02; no public explanation for the inclination",
    )
    merged = polar.merge(mid, name="Tranche 0 Tracking (measured geometry)")
    merged.provenance = "seeded from catalogued elements, D-02; DEC-19"
    return merged


#: CSIS *Getting on Track* notional architectures (D-09). Public analytical proxies —
#: cite as such, never as agency specifications.
CSIS_ARCHITECTURES = {
    "csis_91_leo": dict(total=91, planes=7, phasing=1, altitude_km=1000.0,
                        inclination_deg=80.0, pattern="star",
                        note="persistent global stereo at 120 deg FOR; FAILS at 110 or 100"),
    "csis_135_leo": dict(total=135, planes=9, phasing=1, altitude_km=1000.0,
                         inclination_deg=80.0, pattern="star",
                         note="sized for persistent global coverage, 120 deg FOR"),
    "csis_312_leo": dict(total=312, planes=12, phasing=1, altitude_km=1000.0,
                         inclination_deg=80.0, pattern="star",
                         note="the cost of a 110 deg sensor instead of 120"),
    "csis_15_meo": dict(total=15, planes=3, phasing=1, altitude_km=10000.0,
                        inclination_deg=45.0, pattern="delta",
                        note="MEO layer, stereo through 8-fold coverage"),
    "csis_8_meo_equatorial": dict(total=8, planes=1, phasing=0, altitude_km=10000.0,
                                  inclination_deg=0.0, pattern="delta",
                                  note="single equatorial MEO plane for mid-latitudes"),
}


def csis_architecture(key: str) -> Constellation:
    """Build one of the CSIS notional architectures.

    **Plane counts and phasing are ours.** CSIS publishes satellite totals, altitudes and
    fields of regard; it does not publish Walker parameters. The plane counts here are a
    reasonable factorisation, not a transcription, and that distinction belongs in any
    citation of these results.
    """
    if key not in CSIS_ARCHITECTURES:
        raise KeyError(f"unknown architecture {key!r}; known: {sorted(CSIS_ARCHITECTURES)}")
    spec = dict(CSIS_ARCHITECTURES[key])
    note = spec.pop("note")
    c = walker(
        name=key,
        provenance=f"CSIS Getting on Track (D-09): {note}. "
                   "Totals and altitude are CSIS; plane count and phasing are ours.",
        **spec,
    )
    return c
