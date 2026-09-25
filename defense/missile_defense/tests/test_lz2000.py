"""Transcription integrity for the Li & Zhang (2000) benchmark (`mwsim.lz2000`).

A replication is only worth as much as its transcription. These tests exist because the
source is a **scanned** PDF with no text layer — every number in `lz2000.py` was read off
an image, and a digit misread in a 13x13 transition matrix would produce a plausible-
looking but wrong result.

The strongest check available is that the paper states the same structure twice, in two
unrelated notations: the adjacency index matrices ``Omega`` (equations 31-32) and the
transition probability matrices ``Pi`` (equations 33-34). They were typeset separately and
they must agree exactly — a transition probability is non-zero precisely when the switch is
legitimate. `TestOmegaAgreesWithPi` is therefore a genuine cross-check on both, not a
restatement of one.

The model geometry gives a third, independent check: the paper says topology A connects
nearest neighbours and topology B adds second-nearest, so the graphs must match the
Euclidean structure of the acceleration grid in equation (28).
"""

from __future__ import annotations

import numpy as np
import pytest

from mwsim import lz2000 as lz


class TestModelSet:
    def test_thirteen_models(self) -> None:
        assert lz.MODEL_ACCELERATIONS.shape == (13, 2)

    def test_m1_is_the_origin(self) -> None:
        """Fig. 3: "Model m1 corresponds to the origin of the model space"."""
        assert np.array_equal(lz.MODEL_ACCELERATIONS[0], [0.0, 0.0])

    def test_two_rings_at_twenty_and_forty(self) -> None:
        magnitudes = np.linalg.norm(lz.MODEL_ACCELERATIONS[1:], axis=1)
        assert sorted(np.unique(np.round(magnitudes, 6))) == pytest.approx(
            [20.0, 20.0 * np.sqrt(2.0), 40.0]
        )

    def test_the_axes_are_as_the_paper_describes(self) -> None:
        """"m12, m4, m1, m2 and m10 form the horizontal axis" (and m13, m5, m1, m3, m11)."""
        horizontal = [12, 4, 1, 2, 10]
        vertical = [13, 5, 1, 3, 11]
        for names, axis in ((horizontal, 1), (vertical, 0)):
            # The off-axis component is zero for every model on that axis.
            assert np.all(lz.MODEL_ACCELERATIONS[[n - 1 for n in names], axis] == 0.0)

    def test_maximum_acceleration_is_four_g(self) -> None:
        """"a maximum value of 4g (40 m/s^2) in any direction"."""
        assert np.abs(lz.MODEL_ACCELERATIONS).max() == 40.0


class TestTransitionMatrices:
    @pytest.mark.parametrize("pi", [lz.PI_A, lz.PI_B], ids=["A", "B"])
    def test_rows_sum_to_one(self, pi: np.ndarray) -> None:
        assert pi.sum(axis=1) == pytest.approx(np.ones(13))

    @pytest.mark.parametrize("pi", [lz.PI_A, lz.PI_B], ids=["A", "B"])
    def test_non_negative(self, pi: np.ndarray) -> None:
        assert np.all(pi >= 0.0)

    @pytest.mark.parametrize("pi", [lz.PI_A, lz.PI_B], ids=["A", "B"])
    def test_self_transitions_dominate(self, pi: np.ndarray) -> None:
        """"The diagonal terms were chosen based on the expected sojourn time"."""
        assert np.all(np.diag(pi) > 0.5)


class TestOmegaAgreesWithPi:
    """The cross-check: two independently typeset statements of one structure."""

    @pytest.mark.parametrize(
        "omega,pi", [(lz.OMEGA_A, lz.PI_A), (lz.OMEGA_B, lz.PI_B)], ids=["A", "B"]
    )
    def test_sparsity_patterns_are_identical(
        self, omega: np.ndarray, pi: np.ndarray
    ) -> None:
        assert np.array_equal(lz.adjacency(omega), pi > 0.0)

    @pytest.mark.parametrize("omega", [lz.OMEGA_A, lz.OMEGA_B], ids=["A", "B"])
    def test_every_model_is_adjacent_from_itself(self, omega: np.ndarray) -> None:
        """"the ith column lists all models that are adjacent from m_i, including m_i"."""
        assert np.all(np.diag(lz.adjacency(omega)))

    @pytest.mark.parametrize("omega", [lz.OMEGA_A, lz.OMEGA_B], ids=["A", "B"])
    def test_indices_stay_in_range(self, omega: np.ndarray) -> None:
        assert omega.min() >= 1 and omega.max() <= 13


class TestTopologyGeometry:
    """Does the graph match the picture in Fig. 3?"""

    @staticmethod
    def _distances() -> np.ndarray:
        a = lz.MODEL_ACCELERATIONS
        return np.linalg.norm(a[:, None, :] - a[None, :, :], axis=-1)

    def test_topology_a_is_nearest_neighbours_only(self) -> None:
        """"in topology A, a model is only allowed to switch to its nearest neighbors"."""
        d = self._distances()
        off_diagonal = lz.ADJACENCY_A & ~np.eye(13, dtype=bool)
        assert np.allclose(d[off_diagonal], 20.0)

    def test_topology_b_adds_the_diagonals(self) -> None:
        """"in topology B, switches to its second nearest neighbors ... are also allowed"."""
        d = self._distances()
        off_diagonal = lz.ADJACENCY_B & ~np.eye(13, dtype=bool)
        assert set(np.round(d[off_diagonal], 6)) == {
            20.0, round(20.0 * np.sqrt(2.0), 6)
        }

    def test_b_strictly_contains_a(self) -> None:
        assert np.all(lz.ADJACENCY_B >= lz.ADJACENCY_A)
        assert lz.ADJACENCY_B.sum() > lz.ADJACENCY_A.sum()

    def test_both_graphs_are_symmetric(self) -> None:
        """A switch that is legitimate one way is legitimate back."""
        assert np.array_equal(lz.ADJACENCY_A, lz.ADJACENCY_A.T)
        assert np.array_equal(lz.ADJACENCY_B, lz.ADJACENCY_B.T)

    def test_outer_ring_is_reachable_from_the_origin_only_through_the_inner_ring(
        self,
    ) -> None:
        """The structural reason topology A is hard, and why LMS3 struggles on it.

        The paper names this weakness directly: "jumps between two widely separated modes
        that are connected only through several intermediate modes".
        """
        assert not lz.ADJACENCY_A[0, 9]          # m1 -> m10 is not a legal single step
        assert lz.ADJACENCY_A[0, 1] and lz.ADJACENCY_A[1, 9]   # m1 -> m2 -> m10 is


class TestScenarios:
    @pytest.mark.parametrize("scenario", [1, 2])
    def test_runs_for_one_hundred_and_sixty_steps(self, scenario: int) -> None:
        assert lz.acceleration_sequence(scenario).shape == (160, 2)

    def test_table_three_values_land_in_the_right_periods(self) -> None:
        a = lz.acceleration_sequence(1)
        assert np.array_equal(a[0], [0.0, 0.0])        # period 1-30
        assert np.array_equal(a[29], [0.0, 0.0])
        assert np.array_equal(a[30], [18.0, 22.0])     # period 31-45
        assert np.array_equal(a[44], [18.0, 22.0])
        assert np.array_equal(a[45], [2.0, 37.0])      # period 46-55
        assert np.array_equal(a[139], [38.0, -1.0])    # period 140-150
        assert np.array_equal(a[159], [0.0, 0.0])      # period 151-160

    def test_scenario_two_has_the_larger_jumps(self) -> None:
        """"Second scenario has several large jumps in system mode"."""
        jumps = lambda s: np.linalg.norm(  # noqa: E731
            np.diff(lz.acceleration_sequence(s), axis=0), axis=1
        ).max()
        assert jumps(2) > jumps(1)

    def test_rejects_an_unknown_scenario(self) -> None:
        with pytest.raises(ValueError, match="scenario"):
            lz.acceleration_sequence(3)

    def test_random_scenario_respects_its_bounds(self) -> None:
        """Equation (30): magnitude never exceeds a_max, and starts at zero."""
        a = lz.random_acceleration_sequence(np.random.default_rng(1))
        magnitude = np.linalg.norm(a, axis=1)
        assert a.shape == (160, 2)
        assert magnitude.max() <= lz.A_MAX + 1e-9
        assert magnitude[0] == pytest.approx(0.0)

    def test_random_scenario_holds_each_mode_for_a_while(self) -> None:
        """It is a semi-Markov *sojourn* process, not white noise."""
        a = lz.random_acceleration_sequence(np.random.default_rng(2))
        changes = int(np.sum(np.any(np.diff(a, axis=0) != 0.0, axis=1)))
        assert 1 <= changes <= 20, f"{changes} mode changes in 160 steps"


class TestSimulation:
    def test_true_process_noise_is_zero(self) -> None:
        """"The true process noise covariance was set to zero" — so truth is repeatable."""
        a = lz.acceleration_sequence(1)
        one = lz.simulate(a, np.random.default_rng(0))
        two = lz.simulate(a, np.random.default_rng(99))
        assert np.array_equal(one.states, two.states)
        assert not np.array_equal(one.measurements, two.measurements)

    def test_measurement_noise_matches_r(self) -> None:
        a = lz.acceleration_sequence(1)
        residuals = []
        for seed in range(40):
            t = lz.simulate(a, np.random.default_rng(seed))
            residuals.append(t.measurements - t.positions)
        spread = np.std(np.concatenate(residuals))
        assert spread == pytest.approx(np.sqrt(lz.R_VARIANCE), rel=0.05)

    def test_estimation_error_is_invariant_to_where_the_target_starts(self) -> None:
        """Claimed in `simulate`'s docstring; asserted here rather than assumed.

        The dynamics are linear and state-independent and the filter is initialised from
        the measurements, so the unreported initial state cannot affect any reported
        error. That is what lets us ignore a parameter the paper never gives.
        """
        from mwsim.imm import IMMFilter

        a = lz.acceleration_sequence(1)
        errors = []
        for x0 in (np.zeros(4), np.array([5e4, -300.0, -2e4, 450.0])):
            truth = lz.simulate(a, np.random.default_rng(7), initial_state=x0)
            f = IMMFilter(lz.build_models(), lz.PI_A, lz.H, lz.measurement_noise())
            mean, cov = lz.two_point_initialisation(truth.measurements)
            s = f.initial_state(mean, cov, lz.initial_mode_probabilities("A"))
            e = []
            for k in range(2, len(truth.measurements)):
                s = f.update(s, truth.measurements[k])
                x, _ = s.combined()
                e.append(np.hypot(x[0] - truth.states[k, 0], x[2] - truth.states[k, 2]))
            errors.append(np.array(e))
        assert errors[0] == pytest.approx(errors[1], rel=1e-6)


class TestInitialisation:
    def test_two_point_differencing_recovers_position_and_velocity(self) -> None:
        z = np.array([[0.0, 0.0], [10.0, -4.0]])
        mean, cov = lz.two_point_initialisation(z, dt=1.0, r=lz.R_VARIANCE)
        assert mean == pytest.approx([10.0, 10.0, -4.0, -4.0])
        assert cov[0, 0] == pytest.approx(lz.R_VARIANCE)
        assert cov[1, 1] == pytest.approx(2.0 * lz.R_VARIANCE)

    @pytest.mark.parametrize("topology,n", [("A", 5), ("B", 9)])
    def test_initial_probabilities_match_the_paper(self, topology: str, n: int) -> None:
        mu = lz.initial_mode_probabilities(topology)
        assert mu.sum() == pytest.approx(1.0)
        assert np.count_nonzero(mu) == n
        assert mu[:n] == pytest.approx(np.full(n, 1.0 / n))
