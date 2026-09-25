"""Independent cross-validation of our IMM against FilterPy (task S-08).

We wrote our own IMM because Stone Soup has none (DEC-23). That leaves an obvious
question: **is ours correct?** Our own tests check that it behaves sensibly — mode
probabilities track the truth, the bank beats a single filter, the covariance widens on
disagreement. Sensible behaviour is necessary but not sufficient; a subtly wrong
implementation can still behave sensibly.

FilterPy's `IMMEstimator` (MIT, Roger Labbe) is an independent implementation of the same
Bar-Shalom algorithm, written by someone else from the same literature. Driving both with
identical inputs and comparing is the same validation pattern used elsewhere in this
project: SGP4 against Vallado's vectors, the atmosphere against the published table,
transmission against the known opacity of the 4.3 µm band.

Agreement is at machine precision, which is the strongest result available — it means the
two implementations are not merely similar but algebraically identical.

Note on sequencing: FilterPy performs the mixing step inside `predict()` and the
mode-probability update inside `update()`, whereas ours does mix-predict-update in a single
call. The comparison is therefore `predict(); update(z)` against `update(z)`, and the exact
agreement confirms the step ordering matches as well as the arithmetic.
"""

from __future__ import annotations

import numpy as np
import pytest

from mwsim import imm

filterpy = pytest.importorskip("filterpy", reason="filterpy not installed")
from filterpy.kalman import IMMEstimator, KalmanFilter  # noqa: E402

H = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]])
R = np.eye(2)
M = np.array([[0.95, 0.05], [0.05, 0.95]])
DT = 1.0


def _both(q_low: float = 0.01, q_high: float = 5.0):
    """The same two-model bank, built in each library."""
    lo = imm.constant_velocity(DT, q_low)
    hi = imm.constant_velocity(DT, q_high)

    ours = imm.IMMFilter(
        [
            imm.MotionModel("lo", lo.transition, lo.process_noise),
            imm.MotionModel("hi", hi.transition, hi.process_noise),
        ],
        M, H, R,
    )
    state = ours.initial_state(np.zeros(4), np.eye(4) * 10.0, np.array([0.5, 0.5]))

    filters = []
    for m in (lo, hi):
        f = KalmanFilter(dim_x=4, dim_z=2)
        f.F, f.Q = m.transition.copy(), m.process_noise.copy()
        f.H, f.R = H.copy(), R.copy()
        f.x, f.P = np.zeros(4), np.eye(4) * 10.0
        filters.append(f)
    theirs = IMMEstimator(filters, np.array([0.5, 0.5]), M.copy())
    return ours, state, theirs


def _drive(measurements: np.ndarray, **kw):
    ours, state, theirs = _both(**kw)
    d_state, d_mu = [], []
    for z in measurements:
        state = ours.update(state, z)
        x_ours, _ = state.combined()
        theirs.predict()
        theirs.update(z)
        d_state.append(np.abs(x_ours - theirs.x))
        d_mu.append(np.abs(state.mode_probabilities - theirs.mu))
    return np.array(d_state), np.array(d_mu)


class TestAgreesWithFilterPy:
    def test_straight_flight(self) -> None:
        rng = np.random.default_rng(0)
        truth = np.stack([np.arange(50) * 2.0, np.zeros(50)], axis=-1)
        z = truth + rng.normal(scale=1.0, size=truth.shape)
        d_state, d_mu = _drive(z)
        assert d_state.max() < 1e-9, f"state diverged by {d_state.max():.2e}"
        assert d_mu.max() < 1e-9, f"mode probabilities diverged by {d_mu.max():.2e}"

    def test_through_a_manoeuvre(self) -> None:
        """The case that exercises mixing hardest, and where an error would show."""
        rng = np.random.default_rng(42)
        t = np.arange(60)
        truth = np.stack([t * 2.0, np.where(t < 30, 0.0, (t - 30) ** 2 * 0.3)], axis=-1)
        z = truth + rng.normal(scale=1.0, size=truth.shape)
        d_state, d_mu = _drive(z)
        assert d_state.max() < 1e-9, f"state diverged by {d_state.max():.2e}"
        assert d_mu.max() < 1e-9, f"mode probabilities diverged by {d_mu.max():.2e}"

    def test_agreement_is_at_machine_precision(self) -> None:
        """Not merely close — algebraically identical."""
        rng = np.random.default_rng(7)
        z = np.cumsum(rng.normal(scale=2.0, size=(40, 2)), axis=0)
        d_state, d_mu = _drive(z)
        assert d_state.max() < 1e-11
        assert d_mu.max() < 1e-11

    @pytest.mark.parametrize("q_low,q_high", [(0.001, 1.0), (0.1, 50.0), (1.0, 2.0)])
    def test_holds_across_model_tunings(self, q_low: float, q_high: float) -> None:
        """Agreement must not depend on a lucky choice of process noise."""
        rng = np.random.default_rng(3)
        t = np.arange(40)
        truth = np.stack([t * 3.0, np.sin(t / 5.0) * 20.0], axis=-1)
        z = truth + rng.normal(scale=1.5, size=truth.shape)
        d_state, d_mu = _drive(z, q_low=q_low, q_high=q_high)
        assert d_state.max() < 1e-9
        assert d_mu.max() < 1e-9

    def test_mode_probabilities_match_exactly_at_the_end(self) -> None:
        rng = np.random.default_rng(11)
        t = np.arange(50)
        truth = np.stack([t * 2.0, np.where(t < 25, 0.0, (t - 25) * 5.0)], axis=-1)
        z = truth + rng.normal(scale=1.0, size=truth.shape)

        ours, state, theirs = _both()
        for m in z:
            state = ours.update(state, m)
            theirs.predict()
            theirs.update(m)
        assert state.mode_probabilities == pytest.approx(theirs.mu, abs=1e-12)
