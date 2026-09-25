"""Warn-to-decision latency model (task D-20)."""

from __future__ import annotations

import numpy as np
import pytest

from mwsim import latency as lat


class TestPropagation:
    def test_geo_nadir_is_about_119_ms(self) -> None:
        """The standard textbook figure; anchors the whole light-time chain."""
        assert float(lat.propagation_delay_s(35786.0)) == pytest.approx(0.1194, abs=0.0005)

    def test_leo_downlink_is_milliseconds(self) -> None:
        assert float(lat.propagation_delay_s(lat.max_slant_range_km(1000.0))) < 0.02

    def test_slant_range_exceeds_altitude(self) -> None:
        for alt in (500.0, 1000.0, 10000.0):
            assert lat.max_slant_range_km(alt) > alt

    def test_crosslink_is_twice_the_slant_range(self) -> None:
        """Two satellites each seeing the same horizon point."""
        for alt in (1000.0, 10000.0):
            assert lat.max_crosslink_range_km(alt) == pytest.approx(
                2.0 * lat.max_slant_range_km(alt)
            )


class TestBudget:
    def test_stages_sum(self) -> None:
        b = lat.ground_centralised_budget()
        assert b.total_mean_s() == pytest.approx(sum(s.mean_s for s in b.stages))

    def test_sampled_latencies_are_all_positive(self) -> None:
        """Lognormal, not Gaussian -- nothing arrives before it was sent."""
        for b in (lat.ground_centralised_budget(), lat.edge_fused_budget()):
            assert np.all(b.sample(5000) > 0)

    def test_distribution_is_right_skewed(self) -> None:
        """Queues have tails; the mean should sit above the median."""
        b = lat.ground_centralised_budget()
        p = b.percentiles(q=(50, 90, 99))
        assert p[99] > p[90] > p[50]
        assert p[99] - p[50] > p[50] - 0.0 or p[99] > 1.5 * p[50]

    def test_physics_fraction_is_tiny(self) -> None:
        """The headline honesty check, asserted rather than left in prose.

        If propagation ever becomes a meaningful share of the budget, the framing in the
        module docstring is wrong and needs revisiting.
        """
        for b in (lat.ground_centralised_budget(), lat.edge_fused_budget()):
            assert b.physics_fraction() < 0.02, (
                f"propagation is {100*b.physics_fraction():.1f}% of the budget; "
                "the 'latency is dominated by processing' framing needs re-checking"
            )

    def test_breakdown_is_sorted_and_complete(self) -> None:
        b = lat.ground_centralised_budget()
        rows = b.breakdown()
        assert len(rows) == len(b.stages)
        assert [r[1] for r in rows] == sorted((r[1] for r in rows), reverse=True)
        assert sum(r[2] for r in rows) == pytest.approx(1.0)


class TestEdgeAdvantage:
    def test_reduces_to_the_processing_difference(self) -> None:
        """Propagation contributes under 50 ms, so the trade is a compute question."""
        adv = lat.edge_advantage_s(ground_fusion_s=5.0, onboard_fusion_s=2.0)
        assert adv == pytest.approx(3.0, abs=0.05)

    def test_edge_loses_when_onboard_processing_is_slower(self) -> None:
        assert lat.edge_advantage_s(ground_fusion_s=5.0, onboard_fusion_s=10.0) < 0

    def test_breakeven_is_just_below_the_ground_time(self) -> None:
        """The crosslink overhead is tens of milliseconds against seconds of processing."""
        for g in (1.0, 5.0, 30.0):
            b = lat.breakeven_onboard_fusion_s(g)
            assert 0.0 < g - b < 0.1

    def test_more_hops_lower_the_breakeven_slightly(self) -> None:
        few = lat.breakeven_onboard_fusion_s(5.0, crosslink_hops=1)
        many = lat.breakeven_onboard_fusion_s(5.0, crosslink_hops=6)
        assert few > many
        assert few - many < 0.2, "crosslink hops should not dominate a seconds-scale budget"


class TestPublishedPriors:
    def test_every_prior_carries_a_status_and_source(self) -> None:
        for key, prior in lat.PUBLISHED_PRIORS.items():
            assert prior["status"] in {"PUBLISHED", "REPORTED", "UNVERIFIED"}
            assert prior["source"], f"{key} has no source"

    def test_no_prior_is_labelled_published(self) -> None:
        """None of these are agency performance specifications, and none may pose as one."""
        assert all(p["status"] != "PUBLISHED" for p in lat.PUBLISHED_PRIORS.values())
