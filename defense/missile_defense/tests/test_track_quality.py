"""Track quality and covariance consistency (task D-23)."""

from __future__ import annotations

import numpy as np
import pytest

from mwsim import track_quality as tq


def _synthetic(n=500, sigma_km=1.0, reported_sigma_km=1.0, seed=7):
    """Truth, estimates with known error, and a filter's claimed covariance."""
    rng = np.random.default_rng(seed)
    t = np.arange(n, dtype=float)
    truth = np.stack([t * 7.0, t * 0.5, np.full(n, 40.0)], axis=-1)
    est = truth + rng.normal(scale=sigma_km, size=(n, 3))
    cov = np.eye(3) * reported_sigma_km**2
    return t, est, truth, cov


class TestNEES:
    def test_consistent_filter_has_nees_near_state_dimension(self) -> None:
        """The defining property: E[NEES] = dim for an honest filter."""
        t, est, truth, cov = _synthetic(sigma_km=1.0, reported_sigma_km=1.0)
        v = tq.nees(est, truth, cov)
        assert float(np.mean(v)) == pytest.approx(3.0, rel=0.15)
        assert tq.classify_consistency(v, 3) == "consistent"

    def test_overconfident_filter_is_caught(self) -> None:
        """Errors 3x larger than the filter claims -- the dangerous direction."""
        t, est, truth, cov = _synthetic(sigma_km=3.0, reported_sigma_km=1.0)
        v = tq.nees(est, truth, cov)
        assert float(np.mean(v)) > 3.0
        assert tq.classify_consistency(v, 3) == "overconfident"

    def test_conservative_filter_is_caught(self) -> None:
        t, est, truth, cov = _synthetic(sigma_km=0.3, reported_sigma_km=3.0)
        assert tq.classify_consistency(tq.nees(est, truth, cov), 3) == "conservative"

    def test_singular_covariance_is_infinite_not_pseudo_inverted(self) -> None:
        """A filter claiming zero uncertainty makes an infinitely strong claim.

        Pseudo-inverting would average that away into a finite, respectable-looking number.
        """
        est = np.array([[1.0, 0.0, 0.0]])
        truth = np.zeros((1, 3))
        singular = np.diag([1.0, 1.0, 0.0])
        assert np.isinf(tq.nees(est, truth, singular)[0])

    def test_overconfidence_survives_a_few_good_samples(self) -> None:
        """An overconfident filter should not be rescued by mostly-small errors."""
        rng = np.random.default_rng(1)
        n = 400
        err = rng.normal(scale=0.2, size=(n, 3))
        err[::10] *= 40.0          # occasional large excursions
        truth = np.zeros((n, 3))
        cov = np.eye(3) * 0.04
        assert tq.classify_consistency(tq.nees(err, truth, cov), 3) == "overconfident"


class TestCustody:
    def test_continuous_good_track_is_one_interval(self) -> None:
        t = np.arange(100, dtype=float)
        e = np.full(100, 0.5)
        iv = tq.custody_intervals(t, e, 1.0)
        assert len(iv) == 1 and iv[0] == (0.0, 99.0)

    def test_a_gap_splits_custody(self) -> None:
        t = np.arange(100, dtype=float)
        e = np.full(100, 0.5)
        e[40:60] = 5.0
        iv = tq.custody_intervals(t, e, 1.0)
        assert len(iv) == 2

    def test_custody_distinguishes_what_rms_hides(self) -> None:
        """The reason custody is reported as intervals rather than a mean.

        Two tracks with near-identical RMS: one degrades gently throughout, the other is
        excellent except for a total loss during the manoeuvre. Operationally these are
        not the same, and RMS alone cannot tell them apart.
        """
        t = np.arange(200, dtype=float)
        spread = np.full(200, 1.02)            # everywhere just over threshold
        concentrated = np.full(200, 0.1)
        concentrated[95:105] = 4.5             # brief total loss

        assert np.sqrt(np.mean(spread**2)) == pytest.approx(1.02, rel=0.01)
        assert tq.custody_intervals(t, spread, 1.0) == []
        held = tq.custody_intervals(t, concentrated, 1.0)
        assert len(held) == 2
        assert sum(b - a for a, b in held) > 180.0


class TestAssess:
    def test_reports_confidence_ratio_near_one_when_honest(self) -> None:
        """An honest filter must score ~1.0, not 1/sqrt(3).

        This caught a real bug: reported uncertainty was sqrt(trace(P)/3), the PER-AXIS
        sigma, while the error was 3-D magnitude RMS. Comparing them scored every honest
        filter at 0.577 and would have flagged it overconfident -- inverting the meaning
        of the one metric whose whole purpose is detecting overconfidence.
        """
        t, est, truth, cov = _synthetic(sigma_km=1.0, reported_sigma_km=1.0)
        q = tq.assess(t, est, truth, cov, custody_threshold_km=5.0)
        assert q.is_consistent
        assert q.confidence_ratio == pytest.approx(1.0, rel=0.15)
        assert q.custody_fraction > 0.95

    def test_reported_sigma_and_error_are_the_same_quantity(self) -> None:
        """Guards the units of the comparison directly, at three noise levels."""
        for s in (0.5, 1.0, 4.0):
            t, est, truth, cov = _synthetic(sigma_km=s, reported_sigma_km=s)
            q = tq.assess(t, est, truth, cov, custody_threshold_km=100.0)
            assert q.mean_reported_sigma_km == pytest.approx(
                q.rms_position_error_km, rel=0.2
            ), f"mismatch at sigma={s}"

    def test_confidence_ratio_below_one_flags_overconfidence(self) -> None:
        t, est, truth, cov = _synthetic(sigma_km=4.0, reported_sigma_km=1.0)
        q = tq.assess(t, est, truth, cov, custody_threshold_km=20.0)
        assert q.confidence_ratio < 0.5
        assert q.consistency == "overconfident"

    def test_rejects_mismatched_shapes(self) -> None:
        with pytest.raises(ValueError):
            tq.position_errors_km(np.zeros((10, 3)), np.zeros((9, 3)))


class TestGospaCutoff:
    def test_cutoff_follows_the_custody_threshold(self) -> None:
        """c is not a free knob -- it must follow from the problem's scale."""
        assert tq.gospa_cutoff_km(2.0) == 2.0

    def test_rejects_nonpositive(self) -> None:
        with pytest.raises(ValueError):
            tq.gospa_cutoff_km(0.0)
