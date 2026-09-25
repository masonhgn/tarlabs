"""Walker constellation generation (task S-04, DEC-19)."""

from __future__ import annotations

import numpy as np
import pytest

from mwsim import constellation as con


class TestWalkerPattern:
    def test_distributes_satellites_evenly(self) -> None:
        c = con.walker(name="t", total=28, planes=4, phasing=1,
                       altitude_km=1000.0, inclination_deg=81.0)
        assert len(c) == 28
        assert c.n_planes == 4
        per_plane = [sum(1 for s in c.satellites if s.plane == p) for p in range(4)]
        assert per_plane == [7, 7, 7, 7]

    def test_reproduces_published_tranche1_tracking_geometry(self) -> None:
        """SDA states 28 Tracking satellites in 4 planes, 7 per plane."""
        c = con.walker(name="T1", total=28, planes=4, phasing=1,
                       altitude_km=1000.0, inclination_deg=81.0, pattern="star")
        assert len(c) == 28 and c.n_planes == 4
        raans = sorted({round(s.raan_deg, 1) for s in c.satellites})
        # Star pattern spreads 4 planes across 180 degrees.
        assert raans == [0.0, 45.0, 90.0, 135.0]

    def test_delta_and_star_spread_differently(self) -> None:
        """The distinction that halves effective plane count if got wrong."""
        kw = dict(name="t", total=8, planes=4, phasing=0,
                  altitude_km=1000.0, inclination_deg=80.0)
        delta = sorted({round(s.raan_deg) for s in con.walker(pattern="delta", **kw).satellites})
        star = sorted({round(s.raan_deg) for s in con.walker(pattern="star", **kw).satellites})
        assert delta == [0, 90, 180, 270]
        assert star == [0, 45, 90, 135]

    def test_measured_plane_separation_overrides_the_pattern(self) -> None:
        """DEC-19: seed from the measured 65 degrees, not an assumed-even spread."""
        c = con.walker(name="t", total=4, planes=2, phasing=0,
                       altitude_km=943.0, inclination_deg=81.0, raan_spread_deg=130.0)
        raans = sorted({round(s.raan_deg) for s in c.satellites})
        assert raans == [0, 65]

    def test_phasing_offsets_adjacent_planes(self) -> None:
        kw = dict(name="t", total=8, planes=4, altitude_km=1000.0, inclination_deg=80.0)
        unphased = con.walker(phasing=0, **kw)
        phased = con.walker(phasing=1, **kw)
        m0 = [s.mean_anomaly_deg for s in unphased.satellites if s.plane == 1]
        m1 = [s.mean_anomaly_deg for s in phased.satellites if s.plane == 1]
        assert m0 != m1

    def test_rejects_uneven_division(self) -> None:
        with pytest.raises(ValueError, match="divide evenly"):
            con.walker(name="t", total=10, planes=3, phasing=0,
                       altitude_km=1000.0, inclination_deg=80.0)

    def test_rejects_out_of_range_phasing(self) -> None:
        with pytest.raises(ValueError, match="phasing"):
            con.walker(name="t", total=8, planes=4, phasing=4,
                       altitude_km=1000.0, inclination_deg=80.0)


class TestOrbitalMechanics:
    def test_period_matches_the_measured_tranche0_mean_motion(self) -> None:
        """943 km should give ~13.86 rev/day.

        The catalogued CHECKMATE and WILDFIRE satellites run 13.848-13.895 rev/day, so a
        generator seeded at the measured altitude must land inside that band.
        """
        c = con.tranche0_tracking_measured()
        polar = [s for s in c.satellites if s.inclination_deg > 70]
        for s in polar:
            assert 13.84 < s.mean_motion_rev_per_day < 13.90, (
                f"{s.name}: {s.mean_motion_rev_per_day:.4f} rev/day is outside the "
                "measured Tranche 0 band"
            )

    def test_j2_precession_matches_the_measured_value(self) -> None:
        """D-02 measured about -0.95 deg/day for the transport plane at 81 deg."""
        rate = con.nodal_precession_deg_per_day(con.RE_KM + 943.0, 81.0)
        assert -1.05 < rate < -0.90, f"{rate:.3f} deg/day"

    def test_higher_orbits_have_longer_periods(self) -> None:
        low = con.walker(name="l", total=1, planes=1, phasing=0,
                         altitude_km=1000.0, inclination_deg=80.0).satellites[0]
        high = con.walker(name="h", total=1, planes=1, phasing=0,
                          altitude_km=10000.0, inclination_deg=80.0).satellites[0]
        assert high.period_s > low.period_s

    def test_geostationary_altitude_gives_a_sidereal_day(self) -> None:
        """An independent anchor: 35,786 km must give one revolution per sidereal day."""
        geo = con.walker(name="g", total=1, planes=1, phasing=0,
                         altitude_km=35786.0, inclination_deg=0.0).satellites[0]
        assert geo.period_s == pytest.approx(86164.0, rel=2e-3)


class TestPropagation:
    def test_circular_orbits_hold_their_radius(self) -> None:
        c = con.walker(name="t", total=6, planes=3, phasing=1,
                       altitude_km=1000.0, inclination_deg=80.0)
        pos = con.propagate_kepler(c, np.linspace(0, 6000, 40))
        r = np.linalg.norm(pos, axis=-1)
        assert np.allclose(r, con.RE_KM + 1000.0, rtol=1e-9)

    def test_satellites_complete_one_orbit_per_period(self) -> None:
        c = con.walker(name="t", total=1, planes=1, phasing=0,
                       altitude_km=1000.0, inclination_deg=0.0)
        period = c.satellites[0].period_s
        pos = con.propagate_kepler(c, np.array([0.0, period]), apply_j2=False)
        assert np.allclose(pos[0, 0], pos[0, 1], atol=1e-6)

    def test_inclination_bounds_the_latitude_reached(self) -> None:
        for inc in (30.0, 60.0, 81.0):
            c = con.walker(name="t", total=1, planes=1, phasing=0,
                           altitude_km=1000.0, inclination_deg=inc)
            pos = con.propagate_kepler(c, np.linspace(0, 7000, 200), apply_j2=False)
            r = np.linalg.norm(pos, axis=-1)
            lat = np.degrees(np.arcsin(pos[..., 2] / r))
            assert np.max(np.abs(lat)) == pytest.approx(inc, abs=1.0)

    def test_j2_moves_the_node(self) -> None:
        c = con.walker(name="t", total=1, planes=1, phasing=0,
                       altitude_km=1000.0, inclination_deg=60.0)
        t = np.array([0.0, 30 * 86400.0])
        with_j2 = con.propagate_kepler(c, t, apply_j2=True)
        without = con.propagate_kepler(c, t, apply_j2=False)
        assert not np.allclose(with_j2[0, 1], without[0, 1], atol=1.0)


class TestProvenance:
    def test_generated_constellations_are_flagged_notional(self) -> None:
        """DEC-11: a design is not an observation, and must not be mistaken for one."""
        c = con.csis_architecture("csis_91_leo")
        assert c.notional
        assert "NOTIONAL" in c.describe()

    def test_csis_provenance_states_what_is_ours(self) -> None:
        """CSIS publishes totals and altitudes, not Walker parameters."""
        c = con.csis_architecture("csis_135_leo")
        assert "plane count and phasing are ours" in c.provenance

    def test_measured_tranche0_uses_the_measured_separation(self) -> None:
        c = con.tranche0_tracking_measured()
        polar = sorted({round(s.raan_deg) for s in c.satellites if s.inclination_deg > 70})
        assert polar == [0, 65], f"expected the measured 65 deg separation, got {polar}"

    def test_merge_keeps_planes_distinct(self) -> None:
        a = con.walker(name="a", total=4, planes=2, phasing=0,
                       altitude_km=1000.0, inclination_deg=80.0)
        b = con.walker(name="b", total=6, planes=3, phasing=0,
                       altitude_km=10000.0, inclination_deg=45.0)
        m = a.merge(b)
        assert len(m) == 10
        assert m.n_planes == 5

    def test_unknown_architecture_rejected(self) -> None:
        with pytest.raises(KeyError):
            con.csis_architecture("not_a_thing")
