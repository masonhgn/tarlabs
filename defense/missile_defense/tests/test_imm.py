"""IMM filter validation (task S-08, DEC-23).

This is the classical baseline every later claim is measured against, so the tests check
behaviour rather than just absence of crashes: does the mode probability actually follow
the truth, does the combined covariance widen when models disagree, does the bank beat a
single well-tuned filter through a manoeuvre.
"""

from __future__ import annotations

import numpy as np
import pytest

from mwsim import imm

H = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]])


def _bank(dt=1.0, q_low=0.01, q_high=5.0):
    """A two-model bank: a quiet model and a manoeuvre-tolerant one."""
    quiet = imm.constant_velocity(dt, q_low)
    agile = imm.constant_velocity(dt, q_high)
    models = [
        imm.MotionModel("quiet", quiet.transition, quiet.process_noise),
        imm.MotionModel("agile", agile.transition, agile.process_noise),
    ]
    pi = np.array([[0.95, 0.05], [0.05, 0.95]])
    return imm.IMMFilter(models, pi, H, np.eye(2))


class TestConstruction:
    def test_rejects_single_model(self) -> None:
        m = imm.constant_velocity(1.0, 1.0)
        with pytest.raises(ValueError):
            imm.IMMFilter([m], np.array([[1.0]]), H, np.eye(2))

    def test_rejects_non_stochastic_transition_matrix(self) -> None:
        m = imm.constant_velocity(1.0, 1.0)
        bad = np.array([[0.9, 0.2], [0.1, 0.9]])  # rows do not sum to 1
        with pytest.raises(ValueError, match="sum to 1"):
            imm.IMMFilter([m, m], bad, H, np.eye(2))

    def test_rejects_negative_probabilities(self) -> None:
        m = imm.constant_velocity(1.0, 1.0)
        with pytest.raises(ValueError):
            imm.IMMFilter([m, m], np.array([[1.2, -0.2], [0.05, 0.95]]), H, np.eye(2))


class TestInvariants:
    def test_mode_probabilities_stay_normalised(self) -> None:
        f = _bank()
        s = f.initial_state(np.zeros(4), np.eye(4))
        rng = np.random.default_rng(0)
        for k in range(60):
            s = f.update(s, np.array([k * 1.0, 0.0]) + rng.normal(scale=1.0, size=2))
            assert s.mode_probabilities.sum() == pytest.approx(1.0)
            assert np.all(s.mode_probabilities >= 0)

    def test_covariances_stay_symmetric_positive_definite(self) -> None:
        f = _bank()
        s = f.initial_state(np.zeros(4), np.eye(4))
        rng = np.random.default_rng(1)
        for k in range(40):
            s = f.update(s, np.array([k * 1.0, 0.0]) + rng.normal(scale=1.0, size=2))
            _, p = s.combined()
            assert np.allclose(p, p.T, atol=1e-9)
            assert np.all(np.linalg.eigvalsh(p) > 0)

    def test_survives_an_impossible_measurement(self) -> None:
        """A wild outlier must not produce NaN; an uninformative update is recoverable."""
        f = _bank()
        s = f.update(f.initial_state(np.zeros(4), np.eye(4)), np.array([1e9, -1e9]))
        assert np.all(np.isfinite(s.mode_probabilities))
        assert s.mode_probabilities.sum() == pytest.approx(1.0)


def _run(f, truth, seed=3, noise=1.0):
    rng = np.random.default_rng(seed)
    s = f.initial_state(np.array([truth[0, 0], 0.0, truth[0, 1], 0.0]), np.eye(4) * 10.0)
    est, modes = [], []
    for p in truth:
        s = f.update(s, p + rng.normal(scale=noise, size=2))
        x, _ = s.combined()
        est.append([x[0], x[2]])
        modes.append(s.mode_probabilities.copy())
    return np.array(est), np.array(modes)


class TestTracking:
    def test_follows_a_straight_line(self) -> None:
        truth = np.stack([np.arange(60) * 2.0, np.zeros(60)], axis=-1)
        est, _ = _run(_bank(), truth)
        err = np.linalg.norm(est[10:] - truth[10:], axis=1)
        assert err.mean() < 1.5, f"mean error {err.mean():.2f}"

    def test_mode_probability_shifts_when_the_target_manoeuvres(self) -> None:
        """The core IMM behaviour, and the explainability output the topic asks for."""
        straight = np.stack([np.arange(40) * 2.0, np.zeros(40)], axis=-1)
        t = np.arange(40)
        turn = np.stack([80.0 + t * 2.0, t**2 * 0.4], axis=-1)
        truth = np.vstack([straight, turn])

        _, modes = _run(_bank(), truth, noise=0.5)
        quiet_before = modes[20:38, 0].mean()
        quiet_after = modes[60:, 0].mean()
        assert quiet_before > 0.5, f"quiet should dominate straight flight, got {quiet_before:.2f}"
        assert quiet_after < quiet_before - 0.15, (
            f"quiet {quiet_before:.2f} -> {quiet_after:.2f}: bank did not react to the manoeuvre"
        )

    def test_beats_a_single_quiet_model_through_a_manoeuvre(self) -> None:
        """Why an IMM rather than one well-tuned filter."""
        t = np.arange(50)
        truth = np.stack([t * 2.0, np.where(t < 25, 0.0, (t - 25) ** 2 * 0.5)], axis=-1)

        imm_est, _ = _run(_bank(), truth, noise=0.5)
        quiet = imm.constant_velocity(1.0, 0.01)
        single = imm.IMMFilter(
            [quiet, quiet], np.array([[0.5, 0.5], [0.5, 0.5]]), H, np.eye(2)
        )
        single_est, _ = _run(single, truth, noise=0.5)

        imm_err = np.linalg.norm(imm_est[30:] - truth[30:], axis=1).mean()
        single_err = np.linalg.norm(single_est[30:] - truth[30:], axis=1).mean()
        assert imm_err < single_err, f"IMM {imm_err:.2f} vs single {single_err:.2f}"


class TestCombination:
    def test_disagreement_widens_the_combined_covariance(self) -> None:
        """The spread-of-means term.

        Dropping it makes the filter overconfident exactly when models disagree, which is
        during a manoeuvre, which is when the warning matters most.
        """
        s = imm.IMMState(
            means=np.array([[0.0, 0, 0, 0], [100.0, 0, 0, 0]]),
            covariances=np.stack([np.eye(4), np.eye(4)]),
            mode_probabilities=np.array([0.5, 0.5]),
            model_names=["a", "b"],
        )
        _, p = s.combined()
        assert p[0, 0] > 2400.0, "combined covariance must include the spread of the means"

    def test_agreement_leaves_covariance_alone(self) -> None:
        s = imm.IMMState(
            means=np.zeros((2, 4)),
            covariances=np.stack([np.eye(4), np.eye(4)]),
            mode_probabilities=np.array([0.5, 0.5]),
            model_names=["a", "b"],
        )
        _, p = s.combined()
        assert np.allclose(p, np.eye(4))

    def test_explain_names_the_leading_model(self) -> None:
        s = imm.IMMState(
            means=np.zeros((2, 4)),
            covariances=np.stack([np.eye(4)] * 2),
            mode_probabilities=np.array([0.2, 0.8]),
            model_names=["quiet", "agile"],
        )
        assert s.most_likely_model == "agile"
        assert "agile=0.80" in s.explain()


class TestCoordinatedTurn:
    def test_preserves_speed(self) -> None:
        """A pure rotation must not change the speed of the state it acts on."""
        m = imm.coordinated_turn(1.0, np.radians(3.0), 0.1)
        x = np.array([0.0, 10.0, 0.0, 0.0])
        for _ in range(30):
            x = m.transition @ x
        assert np.hypot(x[1], x[3]) == pytest.approx(10.0, rel=1e-6)

    def test_degenerates_to_constant_velocity_at_zero_turn_rate(self) -> None:
        assert np.allclose(
            imm.coordinated_turn(1.0, 0.0, 0.1).transition,
            imm.constant_velocity(1.0, 0.1, dim=2).transition,
        )


class TestPredictOnly:
    def test_coasting_grows_uncertainty(self) -> None:
        f = _bank()
        s = f.initial_state(np.zeros(4), np.eye(4))
        _, p0 = s.combined()
        for _ in range(5):
            s = f.predict_only(s)
        _, p1 = s.combined()
        assert np.trace(p1) > np.trace(p0)
