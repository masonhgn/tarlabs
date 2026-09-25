"""Line-by-line atmospheric transmission along a slant path (task D-19).

**Required, not optional.** D-17 showed that the 120° field of regard which CSIS finds
necessary for persistent global coverage puts the target at 84° zenith, carrying 8.9× the
vertical air mass. Tracy & Wright's decision to neglect atmospheric attenuation was
justified for an observer directly overhead and does not transfer to that geometry
(DEC-31). This module replaces the assumption with a computation.

## Approach and its justification

Line-by-line via **HITRAN/HAPI** (MIT licence, free, no API key). The path is divided into
altitude layers; each layer contributes an optical depth from its own pressure,
temperature and absorber column; total transmittance is ``exp(-Σ τ)``.

**Only CO₂ is modelled, and that is a defensible simplification here rather than a
shortcut.** Our targets sit at 38–57 km. Water vapour — the dominant infrared absorber in
the lower atmosphere — is essentially absent above the tropopause, falling by three to four
orders of magnitude by 20 km. Above 38 km the infrared opacity in the bands we care about
is CO₂, which is well mixed at roughly 420 ppm and therefore predictable in a way water
vapour never is. Ozone matters near 9.6 µm, outside our bands.

That simplification **would not hold** for a ground-based sensor or a target in the
troposphere, and the limitation is stated rather than buried.

## What this is not

Not MODTRAN. No aerosols, no scattering, no atmospheric self-emission, no refraction, no
continuum absorption. It answers one question — how much of the target's band radiance
survives the path to the sensor — and answers it from published line data rather than from
an assumption.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import atmosphere as atm
from . import limb_geometry as lg

_DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
HITRAN_DIR = _DATA_ROOT / "raw" / "hitran"
HITRAN_DB = "hitran_db"

#: Avogadro constant, per mole.
N_A = 6.02214076e23
#: Mean molar mass of dry air, kg/mol.
M_AIR = 28.9647e-3
#: CO2 volume mixing ratio. Well mixed through the middle atmosphere.
CO2_VMR = 420e-6

#: Bands of interest, in wavenumber (cm-1). Named by the sensor context they belong to.
BANDS_CM1 = {
    "dsp_2.69_2.95um": (1e4 / 2.95, 1e4 / 2.69),
    "sbirs_swir_1.4_3.0um": (1e4 / 3.0, 1e4 / 1.4),
    "mwir_3_5um": (1e4 / 5.0, 1e4 / 3.0),
    "co2_4.3um": (2280.0, 2400.0),
    "goes_band7_3.9um": (2500.0, 2630.0),
}


@dataclass(frozen=True)
class TransmissionResult:
    """Band transmittance along one slant path."""

    band: str
    origin_altitude_km: float
    zenith_deg: float
    co2_column_molec_cm2: float
    mean_transmittance: float
    min_transmittance: float
    max_transmittance: float
    n_layers: int

    @property
    def mean_optical_depth(self) -> float:
        t = self.mean_transmittance
        return float(-np.log(t)) if t > 0 else float("inf")

    @property
    def attenuation_db(self) -> float:
        t = self.mean_transmittance
        return float(-10.0 * np.log10(t)) if t > 0 else float("inf")


def _path_layers(
    origin_altitude_km: float,
    zenith_deg: float,
    *,
    top_km: float = lg.ATMOSPHERE_TOP_KM,
    n_layers: int = 40,
    max_path_km: float = 3000.0,
    samples: int = 8000,
) -> list[tuple[float, float, float]]:
    """Split a slant path into layers: (mean pressure atm, mean temperature K, CO2 column).

    Column is in molecules/cm². Layers are equal-length path segments rather than equal
    altitude steps, which keeps the sampling sensible for near-horizontal rays where a
    short altitude change spans a long path.
    """
    r0 = atm.R0_M / 1000.0 + 0.0  # unused; kept explicit that geometry is in limb_geometry
    RE = lg.RE_KM
    z = np.radians(zenith_deg)
    rr = RE + origin_altitude_km

    s = np.linspace(0.0, max_path_km, samples)
    r = np.sqrt(rr**2 + s**2 + 2.0 * rr * s * np.cos(z))
    altitude = r - RE
    inside = (altitude <= top_km) & (altitude >= 0.0)
    if not np.any(inside):
        return []

    s_in = s[inside]
    alt_in = altitude[inside]
    edges = np.linspace(s_in[0], s_in[-1], n_layers + 1)

    layers: list[tuple[float, float, float]] = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        seg = (s_in >= lo) & (s_in <= hi)
        if not np.any(seg):
            continue
        a = alt_in[seg]
        t, p, rho = atm.properties(np.clip(a, 0.0, top_km) * 1000.0)
        # Path-weighted mean conditions for the layer.
        t_mean = float(np.mean(t))
        p_mean_atm = float(np.mean(p)) / 101325.0
        # Air column through the segment, kg/m^2 -> CO2 molecules/cm^2.
        air_col = float(np.trapezoid(rho, s_in[seg] * 1000.0))
        co2 = air_col / M_AIR * N_A * CO2_VMR / 1e4
        if co2 > 0:
            layers.append((p_mean_atm, t_mean, co2))
    return layers


def _ensure_lines(band: str, *, force: bool = False) -> str:
    """Fetch HITRAN CO2 line data for a band if not already cached. Returns the table name."""
    import hapi

    lo, hi = BANDS_CM1[band]
    table = f"CO2_{band.replace('.', '_')}"
    HITRAN_DIR.mkdir(parents=True, exist_ok=True)
    cwd = os.getcwd()
    try:
        os.chdir(HITRAN_DIR)
        hapi.db_begin(HITRAN_DB)
        if force or table not in hapi.tableList():
            hapi.fetch(table, 2, 1, lo, hi)
    finally:
        os.chdir(cwd)
    return table


def band_transmittance(
    band: str,
    origin_altitude_km: float,
    zenith_deg: float,
    *,
    n_layers: int = 24,
    wavenumber_step: float = 0.05,
) -> TransmissionResult:
    """Band-mean transmittance along a slant path from a target up through the atmosphere.

    Transmittance is computed per wavenumber and averaged across the band. The **mean** is
    reported alongside min and max because a band can be optically thick in its line cores
    and nearly clear between them — a single number hides that structure, and a detector
    integrating across the band sees the mean while a narrow-band one might see either
    extreme.
    """
    import hapi

    if band not in BANDS_CM1:
        raise KeyError(f"unknown band {band!r}; known: {sorted(BANDS_CM1)}")

    table = _ensure_lines(band)
    layers = _path_layers(origin_altitude_km, zenith_deg, n_layers=n_layers)
    if not layers:
        raise ValueError("path does not intersect the atmosphere")

    lo, hi = BANDS_CM1[band]
    cwd = os.getcwd()
    try:
        os.chdir(HITRAN_DIR)
        hapi.db_begin(HITRAN_DB)

        grid = None
        optical_depth = None
        for p_atm, t_k, co2_col in layers:
            nu, coef = hapi.absorptionCoefficient_Lorentz(
                SourceTables=table,
                Environment={"p": p_atm, "T": t_k},
                WavenumberRange=(lo, hi),
                WavenumberStep=wavenumber_step,
                HITRAN_units=True,   # cm^2/molecule
                Diluent={"air": 1.0},
            )
            tau = np.asarray(coef) * co2_col
            if optical_depth is None:
                grid, optical_depth = np.asarray(nu), tau
            else:
                optical_depth = optical_depth + tau
    finally:
        os.chdir(cwd)

    transmittance = np.exp(-np.clip(optical_depth, 0.0, 700.0))
    total_co2 = float(sum(c for _, _, c in layers))
    return TransmissionResult(
        band=band,
        origin_altitude_km=origin_altitude_km,
        zenith_deg=zenith_deg,
        co2_column_molec_cm2=total_co2,
        mean_transmittance=float(np.mean(transmittance)),
        min_transmittance=float(np.min(transmittance)),
        max_transmittance=float(np.max(transmittance)),
        n_layers=len(layers),
    )
