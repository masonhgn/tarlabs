"""Earth-limb geometry and slant atmospheric path (task D-17)."""

from __future__ import annotations

import numpy as np
import pytest

from mwsim import limb_geometry as lg


class TestZenithFromOffNadir:
    def test_nadir_maps_to_zenith_zero(self) -> None:
        assert float(lg.target_zenith_from_off_nadir_deg(0.0)) == pytest.approx(0.0)

    def test_zenith_always_exceeds_off_nadir(self) -> None:
        """r_sat > r_target, so the angle is always amplified."""
        for e in (10.0, 30.0, 50.0):
            assert float(lg.target_zenith_from_off_nadir_deg(e)) > e

    def test_amplification_accelerates_toward_the_limb(self) -> None:
        """The step that turns a modest pointing angle into a near-horizontal view.

        The zenith/off-nadir ratio rises slowly at first (1.149 at 5 deg, 1.168 at 30 deg)
        and then sharply (1.403 at 60 deg). Asserting the *acceleration* captures the
        behaviour that matters; asserting a single large ratio does not, because the
        overall rise is only ~22%.
        """
        ratio = lambda e: float(lg.target_zenith_from_off_nadir_deg(e)) / e
        early = ratio(30.0) - ratio(5.0)
        late = ratio(60.0) - ratio(30.0)
        assert late > 5.0 * early, f"early {early:.4f}, late {late:.4f}"

    def test_120_degree_for_gives_a_near_horizontal_view(self) -> None:
        """CSIS's coverage-required 120 deg FOR is 60 deg off-nadir."""
        z = float(lg.target_zenith_from_off_nadir_deg(60.0, target_altitude_km=45.0))
        assert 80.0 < z < 88.0, f"got {z:.1f} deg"


class TestGeometricLimit:
    def test_reproduces_the_csis_curvature_limit(self) -> None:
        """Independent check of a published qualitative claim.

        CSIS states Earth curvature limits useful field of regard beyond about 120
        degrees. Pure geometry gives 121 degrees for a 45 km target from 1,000 km.
        """
        assert 2.0 * lg.max_off_nadir_deg(target_altitude_km=45.0) == pytest.approx(
            121.0, abs=1.5
        )

    def test_higher_satellites_have_a_narrower_limit(self) -> None:
        low = lg.max_off_nadir_deg(satellite_altitude_km=1000.0)
        high = lg.max_off_nadir_deg(satellite_altitude_km=10000.0)
        assert high < low


class TestSlantColumn:
    def test_vertical_column_falls_with_altitude(self) -> None:
        a = lg.slant_column_kg_m2(38.0, 0.0)
        b = lg.slant_column_kg_m2(57.0, 0.0)
        assert a > b > 0

    def test_altitude_sweep_spans_an_order_of_magnitude(self) -> None:
        """DEC-17's 38-57 km sweep is not a minor perturbation for radiometry."""
        ratio = lg.slant_column_kg_m2(38.0, 0.0) / lg.slant_column_kg_m2(57.0, 0.0)
        assert ratio > 8.0, f"only {ratio:.1f}x across the sweep"

    def test_follows_secant_law_away_from_the_limb(self) -> None:
        for z in (30.0, 60.0):
            expected = 1.0 / np.cos(np.radians(z))
            assert lg.airmass_ratio(45.0, z) == pytest.approx(expected, rel=0.05)

    def test_exceeds_secant_law_near_the_limb(self) -> None:
        """Curvature takes over where the flat-atmosphere approximation dies."""
        assert lg.airmass_ratio(45.0, 89.0) < 1.0 / np.cos(np.radians(89.0))
        assert lg.airmass_ratio(45.0, 89.0) > 15.0

    def test_vertical_ratio_is_unity(self) -> None:
        assert lg.airmass_ratio(45.0, 0.0) == pytest.approx(1.0)


class TestAttenuationAssumption:
    def test_holds_for_a_near_overhead_observer(self) -> None:
        """The geometry Tracy & Wright actually justified it for."""
        assert lg.attenuation_assumption_holds(target_altitude_km=45.0, off_nadir_deg=0.0)
        assert lg.attenuation_assumption_holds(target_altitude_km=45.0, off_nadir_deg=30.0)

    @pytest.mark.parametrize("altitude", [38.0, 45.0, 57.0])
    def test_fails_at_the_coverage_required_field_of_regard(self, altitude: float) -> None:
        """The finding: 120 deg FOR is needed for coverage and breaks the assumption.

        Holds across the whole glide-altitude sweep, so it is a property of the geometry
        rather than of one altitude choice.
        """
        assert not lg.attenuation_assumption_holds(
            target_altitude_km=altitude, off_nadir_deg=60.0
        )
        assert lg.airmass_ratio(
            altitude, float(lg.target_zenith_from_off_nadir_deg(60.0, target_altitude_km=altitude))
        ) > 5.0

    def test_the_transition_sits_between_80_and_100_degree_for(self) -> None:
        assert lg.attenuation_assumption_holds(target_altitude_km=45.0, off_nadir_deg=40.0)
        assert not lg.attenuation_assumption_holds(target_altitude_km=45.0, off_nadir_deg=50.0)


class TestTangentAltitude:
    def test_upward_rays_do_not_descend(self) -> None:
        assert lg.tangent_altitude_km(45.0, 45.0) == pytest.approx(45.0)

    def test_downward_rays_turn_below_the_origin(self) -> None:
        assert lg.tangent_altitude_km(45.0, 120.0) < 45.0
