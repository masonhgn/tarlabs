"""Tests for plane clustering and J2 nodal regression (task D-02)."""

from __future__ import annotations

import json

import numpy as np
import pytest

from mwsim import constellation_analysis as ca
from mwsim import orbit_history as oh


class TestNodalRegression:
    def test_sun_synchronous_orbit_precesses_one_degree_per_day(self) -> None:
        """The textbook anchor: a sun-synchronous orbit tracks the mean sun.

        That is +0.9856 deg/day eastward, and it is the one case where the right answer
        is known independently of our own arithmetic.
        """
        # 800 km altitude sun-synchronous orbit is inclined about 98.6 deg.
        rate = ca.nodal_regression_deg_per_day(6378.137 + 800.0, 98.6)
        assert rate == pytest.approx(0.9856, abs=0.02), (
            f"sun-synchronous precession came out at {rate:.4f} deg/day"
        )

    def test_prograde_orbits_regress_westward(self) -> None:
        assert ca.nodal_regression_deg_per_day(7000.0, 45.0) < 0

    def test_retrograde_orbits_precess_eastward(self) -> None:
        assert ca.nodal_regression_deg_per_day(7000.0, 120.0) > 0

    def test_polar_orbit_barely_precesses(self) -> None:
        assert abs(ca.nodal_regression_deg_per_day(7000.0, 90.0)) < 1e-9

    def test_lower_orbits_precess_faster(self) -> None:
        """The mechanism behind the whole D-02 drift finding."""
        low = ca.nodal_regression_deg_per_day(6378.137 + 600.0, 81.0)
        high = ca.nodal_regression_deg_per_day(6378.137 + 940.0, 81.0)
        assert abs(low) > abs(high)


class TestPlaneClustering:
    def test_separates_two_clean_planes(self) -> None:
        sats = [(f"a{i}", 30.0 + i * 0.4, 81.0, 950.0) for i in range(5)]
        sats += [(f"b{i}", 150.0 + i * 0.4, 81.0, 950.0) for i in range(5)]
        planes = ca.cluster_planes(sats)
        assert len(planes) == 2
        assert {p.count for p in planes} == {5}

    def test_does_not_merge_across_inclination(self) -> None:
        """Two groups can share an ascending node and be in completely different orbits."""
        sats = [(f"p{i}", 100.0 + i * 0.2, 81.0, 950.0) for i in range(4)]
        sats += [(f"q{i}", 100.0 + i * 0.2, 40.0, 998.0) for i in range(4)]
        planes = ca.cluster_planes(sats)
        assert len(planes) == 2
        assert {round(p.inclination_deg) for p in planes} == {81, 40}

    def test_handles_the_raan_wrap(self) -> None:
        sats = [("a", 359.0, 81.0, 950.0), ("b", 1.0, 81.0, 950.0), ("c", 3.0, 81.0, 950.0)]
        planes = ca.cluster_planes(sats)
        assert len(planes) == 1
        assert planes[0].count == 3

    def test_outliers_survive_as_single_member_planes(self) -> None:
        """An outlier is a finding, not noise -- BB 3 and BB 4 are the real case."""
        sats = [(f"a{i}", 30.0 + i * 0.3, 81.0, 950.0) for i in range(6)]
        sats.append(("stray", 200.0, 81.0, 620.0))
        planes = ca.cluster_planes(sats)
        assert any(p.count == 1 and p.members == ["stray"] for p in planes)


def _history(norad_id: int):
    path = oh.HISTORY_CACHE / f"gp_history_{norad_id}.json"
    if not path.exists():
        return None
    rows = []
    for r in json.loads(path.read_text(encoding="utf-8"))["records"]:
        try:
            rows.append(
                (
                    np.datetime64(r["EPOCH"][:19], "s"),
                    float(r["RA_OF_ASC_NODE"]),
                    float(r["SEMIMAJOR_AXIS"]),
                    float(r["INCLINATION"]),
                    float(r["ECCENTRICITY"]),
                )
            )
        except (KeyError, TypeError, ValueError):
            continue
    rows.sort()
    return [np.array(c) for c in zip(*rows)] if rows else None


requires_history = pytest.mark.skipif(
    _history(57758) is None, reason="no cached histories; run scripts/fetch_orbit_history.py"
)


@requires_history
class TestRealDrift:
    """Pin the D-02 finding: the off-plane drift is J2, with no residual."""

    @pytest.mark.parametrize("norad_id,name", [(57760, "BB 3"), (57757, "BB 4")])
    def test_j2_predicts_the_observed_drift(self, norad_id: int, name: str) -> None:
        sat, ref = _history(norad_id), _history(57758)
        if sat is None or ref is None:
            pytest.skip("missing history")

        ep, raan, a, inc, ecc = sat
        r_ep, r_raan, r_a, r_i, r_e = ref

        predicted = ca.predicted_raan_separation(ep, a, inc, ecc, r_ep, r_a, r_i, r_e)
        days = ((ep - ep[0]) / np.timedelta64(1, "D")).astype(float)
        ref_days = ((r_ep - ep[0]) / np.timedelta64(1, "D")).astype(float)
        observed = np.unwrap(raan, period=360) - np.interp(
            days, ref_days, np.unwrap(r_raan, period=360)
        )
        observed = observed - observed[0]

        k = int(np.argmin(np.abs(days - 1100)))
        assert abs(observed[k]) > 10.0, f"{name} has not drifted off-plane"
        residual = abs(predicted[k] - observed[k])
        assert residual < 2.0, (
            f"{name}: J2 predicts {predicted[k]:+.2f} deg but {observed[k]:+.2f} deg was "
            f"observed, a {residual:.2f} deg residual. Something other than the altitude "
            "change is moving this satellite -- re-check decision DEC-14."
        )

    def test_they_held_plane_before_the_manoeuvres(self) -> None:
        """Co-planar to a fraction of a degree for the first 347 days.

        This is what makes the later divergence meaningful: they did not launch apart.
        """
        for norad_id in (57760, 57757):
            sat, ref = _history(norad_id), _history(57758)
            if sat is None or ref is None:
                pytest.skip("missing history")
            ep, raan, *_ = sat
            r_ep, r_raan, *_ = ref
            days = ((ep - ep[0]) / np.timedelta64(1, "D")).astype(float)
            ref_days = ((r_ep - ep[0]) / np.timedelta64(1, "D")).astype(float)
            observed = np.unwrap(raan, period=360) - np.interp(
                days, ref_days, np.unwrap(r_raan, period=360)
            )
            observed = observed - observed[0]
            early = observed[days < 340]
            assert np.max(np.abs(early)) < 1.0, (
                f"NORAD {norad_id} was already {np.max(np.abs(early)):.2f} deg off-plane "
                "before the manoeuvres began"
            )
