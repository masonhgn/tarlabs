"""GOES-R ABI Level-1b ingest, calibration and background characterisation (task D-05).

GOES ABI is the only **real, measured** infrared background data available to this study.
Every other radiometric number we have is a model output or an assumption. It is not a
missile-warning sensor and must never be presented as one — but the background it sees is
the real Earth, and the background *statistics* are what our detection model needs.

Two conventions bite immediately and are worth stating rather than discovering:

*   **Radiance is per wavenumber**, in mW m⁻² sr⁻¹ (cm⁻¹)⁻¹, not per wavelength. Converting
    to the per-micron units the rest of our IR work uses requires multiplying by ν̃², and
    getting that wrong is a factor of ~6.6 million at 3.9 µm — an error large enough to be
    obvious, which is the only reason it is safe.
*   **Band 7 is 3.89 µm**, not a solar-blind missile-warning band. DSP's 2.69–2.95 µm band
    is chosen *because* atmospheric absorption suppresses surface background there. GOES has
    no equivalent, so background measured here **overstates** what a real missile-warning
    sensor would face. Our numbers are conservative, and should be described that way.

Data are public domain via NOAA Open Data Dissemination; no credentials are needed.
"""

from __future__ import annotations

import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import numpy as np

_S3_NS = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}

#: GOES-16 stopped producing ABI data before 2026; the operational pair is 18 (West) and
#: 19 (East). Verified against the bucket listings 2026-09-23.
OPERATIONAL_BUCKETS = ("noaa-goes18", "noaa-goes19")

_DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
GOES_CACHE = _DATA_ROOT / "raw" / "goes"

#: ABI instantaneous field of view, radians per pixel. Gives 2.004 km at nadir against the
#: 35,786,023 m perspective point height in the files — matching their "2km at nadir".
ABI_IFOV_RAD = 5.6e-5
GEO_RANGE_M = 35786023.0

#: Nominal spectral width of ABI band 7, micrometres. NOT carried in the L1b file; taken
#: from the published ABI band definition (~3.80-4.00 um) and treated as an assumption.
BAND7_WIDTH_UM = 0.2


@dataclass(frozen=True)
class AbiScene:
    """One calibrated ABI band image."""

    band_id: int
    wavelength_um: float
    radiance: np.ndarray          # mW m-2 sr-1 (cm-1)-1, as stored
    brightness_temp_k: np.ndarray
    time_coverage_start: str
    platform: str
    scene_id: str
    resolution: str

    @property
    def wavenumber_cm1(self) -> float:
        return 1.0e4 / self.wavelength_um

    def spectral_radiance_per_um(self) -> np.ndarray:
        """Convert to W m⁻² sr⁻¹ µm⁻¹.

        L_λ = L_ν̃ · ν̃², with the 1e-4 folding cm⁻¹→µm⁻¹ and the 1e-3 folding mW→W.
        """
        return self.radiance * self.wavenumber_cm1**2 * 1.0e-4 * 1.0e-3


def radiant_intensity_per_radiance(
    *,
    ifov_rad: float = ABI_IFOV_RAD,
    range_m: float = GEO_RANGE_M,
    band_width_um: float = BAND7_WIDTH_UM,
) -> float:
    """Apparent spectral radiance produced by a point target of 1 W/sr, per pixel.

    A point source of radiant intensity ``I`` at range ``R`` delivers irradiance ``I/R²`` at
    the aperture. The instrument reports that spread over one pixel's solid angle and the
    band width, so the apparent radiance increment is ``I / (R² · Ω · Δλ)``.

    Dividing a measured background radiance by this number answers the question the
    detection model actually needs: *how bright must a target be to matter here?*
    """
    solid_angle_sr = ifov_rad**2
    return 1.0 / (range_m**2 * solid_angle_sr * band_width_um)


def load_scene(path: Path) -> AbiScene:
    """Read one ABI L1b NetCDF file and apply the Planck brightness-temperature calibration.

    The scale factor and offset are applied by the netCDF4 library on read.
    """
    import netCDF4  # imported lazily: only the GOES path needs it

    ds = netCDF4.Dataset(path)
    try:
        rad = ds.variables["Rad"][:].astype(float)
        fk1 = float(ds.variables["planck_fk1"][:])
        fk2 = float(ds.variables["planck_fk2"][:])
        bc1 = float(ds.variables["planck_bc1"][:])
        bc2 = float(ds.variables["planck_bc2"][:])
        # The standard GOES-R inverse-Planck form. Radiance is strictly positive in valid
        # data, but clip anyway: a single zero would otherwise propagate a warning and a
        # NaN through every statistic computed downstream.
        safe = np.clip(rad, 1e-8, None)
        tb = (fk2 / np.log(fk1 / safe + 1.0) - bc1) / bc2
        return AbiScene(
            band_id=int(ds.variables["band_id"][:][0]),
            wavelength_um=float(ds.variables["band_wavelength"][:][0]),
            radiance=rad,
            brightness_temp_k=tb,
            time_coverage_start=str(getattr(ds, "time_coverage_start", "")),
            platform=str(getattr(ds, "platform_ID", "")),
            scene_id=str(getattr(ds, "scene_id", "")),
            resolution=str(getattr(ds, "spatial_resolution", "")),
        )
    finally:
        ds.close()


def list_keys(bucket: str, prefix: str, *, max_keys: int = 100) -> list[tuple[str, int]]:
    """List object keys and sizes under a prefix.

    The mesoscale product writes roughly 1,900 files per hour, so a listing without a
    band-specific prefix truncates long before it reaches the higher channel numbers.
    Always include the band in the prefix.
    """
    url = (
        f"https://{bucket}.s3.amazonaws.com/?list-type=2"
        f"&prefix={prefix}&max-keys={max_keys}"
    )
    root = ET.fromstring(urllib.request.urlopen(url, timeout=90).read())
    return [
        (c.find("s3:Key", _S3_NS).text, int(c.find("s3:Size", _S3_NS).text))
        for c in root.findall("s3:Contents", _S3_NS)
    ]


def fetch(bucket: str, key: str, *, cache_dir: Path = GOES_CACHE) -> Path:
    """Download one object to the cache, skipping if already present."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    out = cache_dir / key.split("/")[-1]
    if not out.exists():
        urllib.request.urlretrieve(f"https://{bucket}.s3.amazonaws.com/{key}", out)
    return out


def background_statistics(scene: AbiScene) -> dict[str, float]:
    """Characterise a scene as a detection background."""
    lam = scene.spectral_radiance_per_um()
    per_w_sr = radiant_intensity_per_radiance()
    tb = np.asarray(scene.brightness_temp_k)
    return {
        "mean_radiance_W_m2_sr_um": float(np.mean(lam)),
        "std_over_mean": float(np.std(lam) / np.mean(lam)),
        "tb_min_k": float(np.min(tb)),
        "tb_mean_k": float(np.mean(tb)),
        "tb_max_k": float(np.max(tb)),
        "tb_std_k": float(np.std(tb)),
        # The number the detection model wants: a target this bright merely equals the
        # background already in the pixel.
        "background_equivalent_intensity_kW_sr": float(
            np.mean(lam) / per_w_sr / 1e3
        ),
    }


def differencing_floor(
    scenes: list[AbiScene], *, sigma: float = 5.0, robust: bool = True
) -> dict[str, float]:
    """Detection floor achievable by differencing consecutive frames.

    Static background cancels under subtraction; what survives is scene *change* — cloud
    motion, illumination drift, instrument noise. That residual, not the background level,
    is what a transient target has to beat.

    ``robust`` uses a median-absolute-deviation estimate, which ignores the minority of
    pixels containing genuine scene change. That is the right estimator for a detection
    floor but it is optimistic as a description of the whole frame, so both are reported.
    """
    if len(scenes) < 2:
        raise ValueError("need at least two scenes to difference")

    per_w_sr = radiant_intensity_per_radiance()
    plain, robust_vals = [], []
    for a, b in zip(scenes, scenes[1:]):
        d = b.spectral_radiance_per_um() - a.spectral_radiance_per_um()
        d = np.asarray(d)
        plain.append(float(np.std(d)))
        robust_vals.append(float(1.4826 * np.median(np.abs(d - np.median(d)))))

    s_plain = float(np.mean(plain))
    s_robust = float(np.mean(robust_vals))
    return {
        "n_differences": len(plain),
        "sigma_plain_W_m2_sr_um": s_plain,
        "sigma_robust_W_m2_sr_um": s_robust,
        "floor_plain_kW_sr": sigma * s_plain / per_w_sr / 1e3,
        "floor_robust_kW_sr": sigma * s_robust / per_w_sr / 1e3,
        "sigma_multiple": sigma,
    }
