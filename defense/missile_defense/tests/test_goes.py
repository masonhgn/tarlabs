"""Tests for GOES ABI ingest and background characterisation (task D-05)."""

from __future__ import annotations

import glob
from pathlib import Path

import numpy as np
import pytest

from mwsim import goes


class TestRadiantIntensityConversion:
    def test_geometry_gives_two_km_pixels_at_nadir(self) -> None:
        """56 urad at geostationary range must give the stated 2 km at nadir."""
        km = goes.ABI_IFOV_RAD * goes.GEO_RANGE_M / 1000.0
        assert km == pytest.approx(2.0, abs=0.01)

    def test_conversion_scales_as_inverse_range_squared(self) -> None:
        near = goes.radiant_intensity_per_radiance(range_m=1.0e7)
        far = goes.radiant_intensity_per_radiance(range_m=2.0e7)
        assert near / far == pytest.approx(4.0, rel=1e-9)

    def test_background_equivalent_intensity_is_order_100_kW_sr(self) -> None:
        """Guards the unit chain end to end.

        A per-wavenumber/per-wavelength slip is a factor of millions, and a solid-angle or
        range slip is orders of magnitude. Either would blow this bound immediately.
        """
        per_w_sr = goes.radiant_intensity_per_radiance()
        background = 0.198  # W m-2 sr-1 um-1, measured
        kW_sr = background / per_w_sr / 1e3
        assert 50.0 < kW_sr < 500.0, f"background-equivalent came out at {kW_sr:.1f} kW/sr"


def _cached(band: str = "07") -> list[Path]:
    return [Path(p) for p in sorted(glob.glob(str(goes.GOES_CACHE / f"*C{band}*.nc")))]


requires_scenes = pytest.mark.skipif(
    not _cached(), reason="no cached GOES scenes; run scripts/analyze_goes_background.py --fetch"
)


@requires_scenes
class TestRealScenes:
    def test_band7_is_the_mwir_window_band(self) -> None:
        s = goes.load_scene(_cached()[0])
        assert s.band_id == 7
        assert s.wavelength_um == pytest.approx(3.89, abs=0.05)

    def test_brightness_temperatures_are_physically_plausible(self) -> None:
        """Earth scenes run cold cloud tops to warm surface: roughly 180-330 K.

        Outside that band means the Planck calibration is wrong, which would silently
        corrupt every background number downstream.
        """
        for path in _cached():
            s = goes.load_scene(path)
            tb = np.asarray(s.brightness_temp_k)
            assert 180.0 < float(np.min(tb)) < 330.0, f"{path.name}: min Tb {np.min(tb):.1f} K"
            assert 180.0 < float(np.max(tb)) < 330.0, f"{path.name}: max Tb {np.max(tb):.1f} K"

    def test_longwave_bands_agree_with_band7_on_temperature(self) -> None:
        """Cross-band agreement is what validates the calibration independently."""
        if not _cached("13"):
            pytest.skip("no band 13 scene cached")
        mwir = goes.load_scene(_cached("07")[0])
        lwir = goes.load_scene(_cached("13")[0])
        a = float(np.mean(mwir.brightness_temp_k))
        b = float(np.mean(lwir.brightness_temp_k))
        assert abs(a - b) < 25.0, f"band 7 mean {a:.1f} K vs band 13 mean {b:.1f} K"

    def test_differencing_beats_the_single_frame_background(self) -> None:
        """The D-05 finding, pinned.

        If differencing ever stops helping by a large factor, either the frames are no
        longer consecutive or the conversion has broken.
        """
        scenes = [goes.load_scene(p) for p in _cached()]
        if len(scenes) < 2:
            pytest.skip("need at least two frames")
        background = goes.background_statistics(scenes[0])
        floor = goes.differencing_floor(scenes)
        gain = (
            background["background_equivalent_intensity_kW_sr"]
            / floor["floor_robust_kW_sr"]
        )
        assert gain > 3.0, f"differencing gain is only {gain:.1f}x"
        assert floor["floor_robust_kW_sr"] < floor["floor_plain_kW_sr"], (
            "the robust sigma should be no larger than the plain one"
        )

    def test_per_wavenumber_to_per_micron_conversion(self) -> None:
        """L_lambda = L_nu * nu^2, a factor of ~6.6e6 at 3.89 um."""
        s = goes.load_scene(_cached()[0])
        ratio = float(np.mean(s.spectral_radiance_per_um()) / np.mean(s.radiance))
        expected = s.wavenumber_cm1**2 * 1e-4 * 1e-3
        assert ratio == pytest.approx(expected, rel=1e-6)
