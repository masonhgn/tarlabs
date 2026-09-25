"""Atmospheric transmission validation (task D-19).

The decisive test is `test_band_is_opaque_through_the_full_atmosphere`: the 4.3 um CO2
band is used for satellite temperature sounding precisely because it is optically thick
from the surface. A model that does not reproduce that is wrong, and every conclusion
drawn from it would be wrong in the same direction.
"""

from __future__ import annotations

import pytest

from mwsim import transmission as tr

pytest.importorskip("hapi", reason="HITRAN HAPI not installed")

#: Line-by-line runs are slow; keep the test grid coarse but still physically meaningful.
_KW = {"n_layers": 8, "wavenumber_step": 0.2}


@pytest.fixture(scope="module")
def surface():
    return tr.band_transmittance("co2_4.3um", 0.0, 0.0, **_KW)


@pytest.fixture(scope="module")
def glide_low():
    return tr.band_transmittance("co2_4.3um", 38.0, 0.0, **_KW)


@pytest.fixture(scope="module")
def glide_high():
    return tr.band_transmittance("co2_4.3um", 57.0, 0.0, **_KW)


class TestValidation:
    def test_band_is_opaque_through_the_full_atmosphere(self, surface) -> None:
        """The anchor. 4.3 um CO2 sounds temperature because it is thick from the ground."""
        assert surface.mean_transmittance < 0.25, (
            f"full-column transmittance {surface.mean_transmittance:.3f} is far too high; "
            "the 4.3 um CO2 band must be optically thick from the surface"
        )
        assert surface.attenuation_db > 5.0

    def test_full_column_matches_the_textbook_magnitude(self, surface) -> None:
        """~7e21 CO2 molecules/cm2 is the standard vertical column figure."""
        assert 5e21 < surface.co2_column_molec_cm2 < 1.5e22

    def test_transmittance_rises_monotonically_with_altitude(
        self, surface, glide_low, glide_high
    ) -> None:
        assert surface.mean_transmittance < glide_low.mean_transmittance
        assert glide_low.mean_transmittance < glide_high.mean_transmittance

    def test_column_falls_monotonically_with_altitude(
        self, surface, glide_low, glide_high
    ) -> None:
        assert (
            surface.co2_column_molec_cm2
            > glide_low.co2_column_molec_cm2
            > glide_high.co2_column_molec_cm2
        )


class TestGlideRegime:
    def test_attenuation_is_small_at_glide_altitudes(self, glide_low, glide_high) -> None:
        """The finding that corrected DEC-31.

        At 38-57 km the target sits above ~99.5% of the atmosphere, so even a large
        multiple of a very small remaining column stays optically thin in the band mean.
        """
        assert glide_low.attenuation_db < 1.0
        assert glide_high.attenuation_db < 0.5

    def test_slant_geometry_does_not_break_it(self) -> None:
        """84 deg zenith is the 120 deg field-of-regard case from D-17."""
        slant = tr.band_transmittance("co2_4.3um", 38.0, 84.0, **_KW)
        assert slant.attenuation_db < 2.0, (
            f"{slant.attenuation_db:.2f} dB at the wide-FOR geometry; "
            "if this ever exceeds 2 dB, DEC-31's correction needs revisiting"
        )

    def test_air_mass_ratio_overstates_the_attenuation_effect(self) -> None:
        """Pins the reasoning error the correction was about.

        D-17 measured ~9x more air mass at 84 deg and concluded the neglect-attenuation
        assumption failed. Optical depth is what attenuates, and 9x a very small optical
        depth is still small. The dB penalty must stay far below the 9x the air-mass
        ratio would suggest.
        """
        nadir = tr.band_transmittance("co2_4.3um", 38.0, 0.0, **_KW)
        slant = tr.band_transmittance("co2_4.3um", 38.0, 84.0, **_KW)
        assert slant.attenuation_db - nadir.attenuation_db < 1.0


class TestBandStructure:
    def test_line_cores_are_opaque_even_when_the_band_mean_is_clear(
        self, glide_low
    ) -> None:
        """Why the mean alone is not enough.

        A band can be nearly transparent on average while individual line cores are
        black. A wide-band detector sees the mean; a narrow-band one might see either
        extreme.
        """
        assert glide_low.mean_transmittance > 0.9
        assert glide_low.min_transmittance < 0.01

    def test_known_bands_are_registered(self) -> None:
        for band in ("dsp_2.69_2.95um", "sbirs_swir_1.4_3.0um", "mwir_3_5um"):
            lo, hi = tr.BANDS_CM1[band]
            assert lo < hi

    def test_rejects_unknown_band(self) -> None:
        with pytest.raises(KeyError):
            tr.band_transmittance("not_a_band", 45.0, 0.0)
