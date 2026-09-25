"""U.S. Standard Atmosphere 1976 validation (task D-07).

Checked against the published table rather than against our own earlier inline copies of
this model -- of which there were three, in ad-hoc scripts, which is exactly how a shared
assumption quietly diverges.

Published values are indexed by GEOPOTENTIAL altitude, so the table tests pass
``geopotential=True``. The trajectory model works in geometric altitude; the distinction
is 0.5 km at 57 km and is tested separately.
"""

from __future__ import annotations

import numpy as np
import pytest

from mwsim import atmosphere as atm

#: (geopotential altitude m, T K, P Pa, rho kg/m3) from the 1976 standard, at the layer
#: boundaries where the published values are exact.
PUBLISHED = [
    (0.0, 288.150, 101325.0, 1.2250),
    (11000.0, 216.650, 22632.1, 0.363918),
    (20000.0, 216.650, 5474.89, 0.0880349),
    (32000.0, 228.650, 868.019, 0.0132250),
    (47000.0, 270.650, 110.906, 0.00142753),
    (51000.0, 270.650, 66.9389, 0.000861600),
    (71000.0, 214.650, 3.95642, 0.0000642110),
]


class TestPublishedTable:
    @pytest.mark.parametrize("h,t_pub,p_pub,rho_pub", PUBLISHED)
    def test_layer_boundaries(self, h: float, t_pub: float, p_pub: float, rho_pub: float) -> None:
        t, p, rho = atm.properties(h, geopotential=True)
        assert float(t) == pytest.approx(t_pub, rel=1e-4), f"T at {h/1000:.0f} km"
        assert float(p) == pytest.approx(p_pub, rel=1e-3), f"P at {h/1000:.0f} km"
        assert float(rho) == pytest.approx(rho_pub, rel=1e-3), f"rho at {h/1000:.0f} km"

    def test_sea_level_constants(self) -> None:
        t, p, rho = atm.properties(0.0, geopotential=True)
        assert float(t) == pytest.approx(atm.T0_K)
        assert float(p) == pytest.approx(atm.P0_PA)
        assert float(rho) == pytest.approx(atm.RHO0_KG_M3, rel=1e-3)

    def test_density_falls_monotonically(self) -> None:
        h = np.linspace(0.0, 85000.0, 400)
        rho = atm.density(h)
        assert np.all(np.diff(rho) < 0.0)

    def test_temperature_inversion_in_the_stratosphere(self) -> None:
        """Temperature rises from 20 to 47 km. A model that misses this is not 1976."""
        assert float(atm.temperature(20000.0, geopotential=True)) < float(
            atm.temperature(47000.0, geopotential=True)
        )


class TestAltitudeConventions:
    def test_geopotential_is_below_geometric(self) -> None:
        assert float(atm.geometric_to_geopotential(57000.0)) < 57000.0

    def test_the_difference_matters_at_glide_altitudes(self) -> None:
        """0.5 km at 57 km -- small, but the glide sweep is only 19 km wide."""
        diff = 57000.0 - float(atm.geometric_to_geopotential(57000.0))
        assert 400.0 < diff < 600.0, f"conversion differs by {diff:.0f} m"

    def test_round_trip(self) -> None:
        for z in (0.0, 10000.0, 40000.0, 57000.0, 80000.0):
            h = atm.geometric_to_geopotential(z)
            assert float(atm.geopotential_to_geometric(h)) == pytest.approx(z, abs=1e-6)

    def test_rejects_altitudes_beyond_the_model(self) -> None:
        with pytest.raises(atm.AltitudeRangeError):
            atm.density(120000.0)


class TestDensityInversion:
    def test_round_trips_against_the_forward_model(self) -> None:
        for z in (20000.0, 40000.0, 57000.0, 70000.0):
            rho = float(atm.density(z))
            assert atm.altitude_for_density(rho) == pytest.approx(z, abs=1.0)

    def test_reproduces_candlers_published_flight_condition(self) -> None:
        """Candler & Leyva: rho = 4.17e-4 kg/m3 is 'approximately 57.1 km geopotential'.

        An independent published anchor -- a third party stating both a density and its
        altitude -- so this validates the model against something other than itself.
        """
        h = atm.altitude_for_density(4.17e-4, geopotential=True)
        assert h / 1000.0 == pytest.approx(57.1, abs=0.2), (
            f"got {h/1000:.2f} km geopotential, Candler states ~57.1 km"
        )


class TestScaleHeight:
    def test_is_seven_to_nine_km_through_the_glide_regime(self) -> None:
        for z in (20000.0, 40000.0, 57000.0):
            assert 6000.0 < atm.scale_height_m(z) < 9000.0
