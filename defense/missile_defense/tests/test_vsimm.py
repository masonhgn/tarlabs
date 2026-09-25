"""Variable-structure IMM, first cut — see `tests/test_lms.py` for the real thing.

`mwsim.vsimm` is superseded by `mwsim.lms` (DEC-43), which implements the published LMS3
algorithm and is validated against the benchmark it came from. These tests still cover
behaviour any variable-structure bank should have — the set varies, it never collapses
below the floor, probabilities stay normalised, full adjacency degenerates to fixed
structure — on a scenario of our own construction.

Note what they do *not* assert: that VS-IMM beats fixed-structure IMM on accuracy. They
never did, and the replication in `tests/test_lms.py` shows why that was the right call.
Plain LMS is not an accuracy improvement over fixed-structure IMM in the primary source
either; it is a compute saving at matched accuracy. DEC-41 originally framed that as a
failure to reproduce a published advantage, which was wrong — the advantage was never
claimed for plain LMS. Superseded by DEC-42.
"""

from __future__ import annotations

import numpy as np
import pytest

from mwsim import imm, vsimm

DT = 1.0
H = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]])
R = np.eye(2)
QS = [0.01, 0.5, 5.0, 50.0]


def _models():
    out = []
    for q in QS:
        m = imm.constant_velocity(DT, q)
        out.append(imm.MotionModel(f"q{q:g}", m.transition, m.process_noise))
    return out


def _pi(n: int, stay: float = 0.85) -> np.ndarray:
    pi = np.full((n, n), (1.0 - stay) / (n - 1))
    np.fill_diagonal(pi, stay)
    return pi


def _scenario(seed: int, n_steps: int = 100):
    """Quiet, hard turn, then quiet again — exercises escalation and relaxation."""
    rng = np.random.default_rng(seed)
    t = np.arange(n_steps).astype(float)
    cross = np.piecewise(
        t,
        [t < 30, (t >= 30) & (t < 60), t >= 60],
        [lambda x: 0 * x, lambda x: (x - 30) ** 2 * 0.5,
         lambda x: 29.0**2 * 0.5 + (x - 60) * 29.0],
    )
    truth = np.stack([t * 2.0, cross], axis=-1)
    return truth, truth + rng.normal(scale=1.0, size=truth.shape)


def _run(f, z, truth):
    s = f.initial_state(np.array([truth[0, 0], 0.0, truth[0, 1], 0.0]), np.eye(4) * 10.0)
    err, sizes = [], []
    for m, x in zip(z, truth):
        s = f.update(s, m)
        xe, _ = s.combined()
        err.append(np.hypot(xe[0] - x[0], xe[2] - x[1]))
        sizes.append(getattr(s, "n_active", len(QS)))
    return np.array(err), np.array(sizes)


class TestConstruction:
    def test_rejects_inverted_thresholds(self) -> None:
        with pytest.raises(ValueError, match="t_unlikely"):
            vsimm.VSIMMFilter(_models(), _pi(4), H, R, t_unlikely=0.5, t_principal=0.1)

    def test_rejects_min_active_below_two(self) -> None:
        with pytest.raises(ValueError, match="at least two"):
            vsimm.VSIMMFilter(_models(), _pi(4), H, R, min_active=1)

    def test_rejects_mis_shaped_adjacency(self) -> None:
        with pytest.raises(ValueError, match="adjacency"):
            vsimm.VSIMMFilter(_models(), _pi(4), H, R, adjacency=np.ones((3, 3), bool))


class TestStructureAdaptation:
    def test_the_active_set_actually_varies(self) -> None:
        """If the set never changes, the filter is fixed-structure wearing a costume."""
        f = vsimm.VSIMMFilter(_models(), _pi(4), H, R,
                              adjacency=vsimm.chain_adjacency(4))
        truth, z = _scenario(5)
        _, sizes = _run(f, z, truth)
        assert len(set(sizes.tolist())) > 1, "active set size never changed"
        assert sizes.min() >= 2

    def test_never_drops_below_the_floor(self) -> None:
        f = vsimm.VSIMMFilter(_models(), _pi(4), H, R,
                              adjacency=vsimm.chain_adjacency(4),
                              t_unlikely=0.49, t_principal=0.5, min_active=2)
        truth, z = _scenario(7)
        _, sizes = _run(f, z, truth)
        assert sizes.min() >= 2

    def test_full_adjacency_with_low_thresholds_degenerates_to_fixed_structure(self) -> None:
        """The control. If this fails, the implementation is wrong.

        With every model reachable and nothing ever unlikely, expansion re-activates the
        whole bank each step, so LMS must behave exactly as a fixed-structure IMM.
        """
        f = vsimm.VSIMMFilter(_models(), _pi(4), H, R,
                              adjacency=vsimm.full_adjacency(4),
                              t_unlikely=1e-9, t_principal=1e-6)
        truth, z = _scenario(5)
        _, sizes = _run(f, z, truth)
        assert set(sizes.tolist()) == {4}

    def test_probabilities_stay_normalised_across_structure_changes(self) -> None:
        f = vsimm.VSIMMFilter(_models(), _pi(4), H, R,
                              adjacency=vsimm.chain_adjacency(4))
        s = f.initial_state(np.zeros(4), np.eye(4) * 10.0)
        truth, z = _scenario(9)
        for m in z:
            s = f.update(s, m)
            assert s.inner.mode_probabilities.sum() == pytest.approx(1.0)
            assert s.full_probabilities.sum() == pytest.approx(1.0)
            # Inactive models must carry exactly zero, not a stale value.
            inactive = [i for i in range(4) if i not in s.active]
            assert np.all(s.full_probabilities[inactive] == 0.0)

    def test_explain_reports_the_active_set(self) -> None:
        f = vsimm.VSIMMFilter(_models(), _pi(4), H, R,
                              adjacency=vsimm.chain_adjacency(4))
        s = f.initial_state(np.zeros(4), np.eye(4) * 10.0)
        truth, z = _scenario(3)
        for m in z[:20]:
            s = f.update(s, m)
        assert "active" in s.explain()


class TestAdjacency:
    def test_chain_connects_only_neighbours(self) -> None:
        a = vsimm.chain_adjacency(4)
        assert a[0, 1] and a[1, 0] and not a[0, 2] and not a[0, 3]

    def test_full_connects_everything(self) -> None:
        assert vsimm.full_adjacency(3).all()

    def test_bandwidth_widens_reachability(self) -> None:
        a = vsimm.banded_adjacency(7, 2)
        assert a[3, 1] and a[3, 5] and not a[3, 0] and not a[3, 6]

    def test_chain_equals_bandwidth_one(self) -> None:
        assert np.array_equal(vsimm.chain_adjacency(6), vsimm.banded_adjacency(6, 1))

    def test_rejects_zero_bandwidth(self) -> None:
        with pytest.raises(ValueError, match="bandwidth"):
            vsimm.banded_adjacency(5, 0)

    def test_wider_bandwidth_activates_more_models(self) -> None:
        """The parameter that decides whether variable structure helps or hurts."""
        truth, z = _scenario(4)
        sizes = {}
        for bw in (1, 3):
            f = vsimm.VSIMMFilter(_models(), _pi(4), H, R,
                                  adjacency=vsimm.banded_adjacency(4, bw))
            _, s = _run(f, z, truth)
            sizes[bw] = s.mean()
        assert sizes[3] > sizes[1]


class TestMeasuredBehaviour:
    def test_saves_computation_at_matched_accuracy(self) -> None:
        """Matched accuracy, far fewer filters — which is what the source reports too.

        This was recorded under DEC-41 as reproducing "cost effectiveness" but not the
        survey's "substantially outperforms". Tracing that phrase to Li & Zhang (2000)
        showed there was nothing to fail to reproduce: Table IV has plain LMS *behind*
        fixed-structure IMM on RMS position error in all six published cases, at a third
        to two-thirds of the FLOPs. See `tests/test_lms.py`.

        The compute saving is the finding that matters here regardless, because it feeds
        the on-orbit fusion breakeven directly (DEC-29).
        """
        fs = imm.IMMFilter(_models(), _pi(4), H, R)
        vs = vsimm.VSIMMFilter(_models(), _pi(4), H, R,
                               adjacency=vsimm.chain_adjacency(4),
                               t_unlikely=0.15, t_principal=0.5)

        fs_rms, vs_rms, active = [], [], []
        for seed in range(2, 7):
            truth, z = _scenario(seed)
            e_fs, _ = _run(fs, z, truth)
            e_vs, sizes = _run(vs, z, truth)
            fs_rms.append(np.sqrt(np.mean(e_fs**2)))
            vs_rms.append(np.sqrt(np.mean(e_vs**2)))
            active.append(sizes.mean())

        # Accuracy: comparable, not dramatically better.
        assert np.mean(vs_rms) < np.mean(fs_rms) * 1.05, "VS-IMM should not be much worse"
        # Computation: genuinely and reliably cheaper.
        assert np.mean(active) < 3.0, (
            f"mean active set {np.mean(active):.2f} of 4 — no computational saving"
        )


class TestTuning:
    def test_tune_selects_by_error_on_supplied_data(self) -> None:
        """Thresholds fitted to data, not chosen to flatter a later comparison."""
        truth, z = _scenario(1)
        build = lambda lo, hi: vsimm.VSIMMFilter(  # noqa: E731
            _models(), _pi(4), H, R, adjacency=vsimm.chain_adjacency(4),
            t_unlikely=lo, t_principal=hi,
        )
        state0 = np.array([truth[0, 0], 0.0, truth[0, 1], 0.0])
        chosen = vsimm.tune(build, z, np.tile(state0, (len(z), 1)))
        assert len(chosen) == 2
        assert 0.0 < chosen[0] < chosen[1] < 1.0
