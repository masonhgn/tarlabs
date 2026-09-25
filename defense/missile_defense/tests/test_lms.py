"""The Likely-Model Set algorithm, and the replication it exists to support.

Two groups of tests here, doing different jobs.

`TestReducesToIMM` and the structure tests check that `mwsim.lms` implements Table I of
Li & Zhang (2000). The strongest of them is the degeneracy control: with a fully connected
adjacency graph no model is ever discardable and expansion never finds anything new, so
LMS3 **must** collapse into an ordinary fixed-structure IMM. It agrees with `mwsim.imm` to
machine precision, which — since that module already agrees with FilterPy to 1e-13 — chains
this implementation back to an independent third-party reference.

`TestReplicatesTableIV` is the actual finding. It runs the paper's own experiment and
records what comes out, at a reduced Monte Carlo count for test runtime; `scripts/
replicate_lms.py` runs the published 500.

## The finding, stated plainly

Our baseline ladder rested on a survey sentence saying LMS *"substantially outperforms"*
fixed-structure IMM. Traced to its primary source, **that is not what the source reports.**
Table IV gives RMS position error for both estimators in six cases, and plain LMS is
*worse* than IMM in every one of them:

| case | IMM | LMS | LMS/IMM |
|---|---|---|---|
| topology A, random | 39.56 | 40.10 | 1.014 |
| topology A, det. 1 | 37.15 | 37.58 | 1.012 |
| topology A, det. 2 | 41.52 | 42.43 | 1.022 |
| topology B, random | 36.93 | 36.94 | 1.000 |
| topology B, det. 1 | 35.28 | 35.30 | 1.001 |
| topology B, det. 2 | 36.47 | 36.73 | 1.007 |

What LMS buys is cost: a FLOP ratio of 0.36-0.67 against the IMM's 1.0. The paper's own
summary says exactly this — *"the LMS and MGS algorithms are much more cost-effective than
the IMM estimator"* — cost-effectiveness, not accuracy.

The only accuracy improvement in the table belongs to **LMS(lambda)**, the variant with a
forgetting factor, and it is 3.5-8.8% on the sparse topology and nil on the dense one.

So the result we measured earlier — matched accuracy at far fewer filters — was right, and
the claim it appeared to contradict was never made about plain LMS.
"""

from __future__ import annotations

import numpy as np
import pytest

from mwsim import lz2000 as lz
from mwsim.imm import IMMFilter
from mwsim.lms import LMSFilter

RUNS = 24  # the paper uses 500; scripts/replicate_lms.py does too


def _filters(topology: str, **kw) -> LMSFilter:
    spec = lz.TOPOLOGIES[topology]
    return LMSFilter(
        lz.build_models(), spec["pi"], lz.H, lz.measurement_noise(),
        kw.pop("adjacency", spec["adjacency"]),
        t_unlikely=kw.pop("t_unlikely", lz.T_UNLIKELY),
        t_principal=kw.pop("t_principal", lz.T_PRINCIPAL),
        k_floor=kw.pop("k_floor", spec["k_floor"]), **kw,
    )


def _run(filt, truth, topology: str):
    z = truth.measurements
    mean, cov = lz.two_point_initialisation(z)
    state = filt.initial_state(mean, cov, lz.initial_mode_probabilities(topology))
    errors, sizes, states = [], [], []
    for k in range(2, len(z)):
        state = filt.update(state, z[k])
        x, _ = state.combined()
        errors.append(np.hypot(x[0] - truth.states[k, 0], x[2] - truth.states[k, 2]))
        sizes.append(getattr(state, "n_filters_run", lz.N_MODELS))
        states.append(state)
    return np.array(errors), np.array(sizes), states


def _rms(topology: str, scenario: int, filt, runs: int = RUNS) -> tuple[float, float]:
    per_step, counts = [], []
    for seed in range(runs):
        truth = lz.simulate(lz.acceleration_sequence(scenario), np.random.default_rng(seed))
        e, n, _ = _run(filt, truth, topology)
        per_step.append(e)
        counts.append(n)
    rms_at_k = np.sqrt(np.mean(np.square(per_step), axis=0))
    return float(np.mean(rms_at_k)), float(np.mean(counts))


class TestConstruction:
    def test_rejects_inverted_thresholds(self) -> None:
        with pytest.raises(ValueError, match="t1"):
            _filters("A", t_unlikely=0.5, t_principal=0.1)

    def test_rejects_mis_shaped_adjacency(self) -> None:
        with pytest.raises(ValueError, match="adjacency"):
            _filters("A", adjacency=np.ones((3, 3), bool))


class TestReducesToIMM:
    """The control. If this fails, nothing else here means anything."""

    def test_full_adjacency_matches_the_fixed_structure_imm(self) -> None:
        models = lz.build_models()
        noise = lz.measurement_noise()
        imm = IMMFilter(models, lz.PI_B, lz.H, noise)
        lms = LMSFilter(
            models, lz.PI_B, lz.H, noise, np.ones((13, 13), bool),
            t_unlikely=lz.T_UNLIKELY, t_principal=lz.T_PRINCIPAL, k_floor=13,
        )
        truth = lz.simulate(lz.acceleration_sequence(2), np.random.default_rng(3))
        z = truth.measurements
        mean, cov = lz.two_point_initialisation(z)
        mu = np.full(13, 1.0 / 13)
        a, b = imm.initial_state(mean, cov, mu), lms.initial_state(mean, cov, mu)

        for k in range(2, len(z)):
            a, b = imm.update(a, z[k]), lms.update(b, z[k])
            x_imm, _ = a.combined()
            x_lms, _ = b.combined()
            # States run to ~1e5 m, so this is relative machine precision.
            assert np.abs(x_imm - x_lms).max() < 1e-7
            assert np.abs(
                a.mode_probabilities - b.full_probabilities(13)
            ).max() < 1e-10
        assert b.n_active == 13, "full adjacency must never prune"


class TestStructureAdaptation:
    @pytest.mark.parametrize("topology", ["A", "B"])
    def test_the_active_set_actually_varies(self, topology: str) -> None:
        """If it never varies, it is a fixed-structure filter wearing a costume."""
        truth = lz.simulate(lz.acceleration_sequence(2), np.random.default_rng(5))
        _, sizes, _ = _run(_filters(topology), truth, topology)
        assert len(set(sizes.tolist())) > 1

    @pytest.mark.parametrize("topology", ["A", "B"])
    def test_never_drops_below_the_k_floor(self, topology: str) -> None:
        """"such that M_k has at least K models" — K is 5 for topology A, 9 for B."""
        floor = lz.TOPOLOGIES[topology]["k_floor"]
        truth = lz.simulate(lz.acceleration_sequence(2), np.random.default_rng(6))
        _, _, states = _run(_filters(topology), truth, topology)
        assert min(len(s.next_active) for s in states) >= floor

    def test_probabilities_stay_normalised_across_structure_changes(self) -> None:
        truth = lz.simulate(lz.acceleration_sequence(2), np.random.default_rng(8))
        _, _, states = _run(_filters("A"), truth, "A")
        for s in states:
            assert s.probabilities.sum() == pytest.approx(1.0)
            assert s.full_probabilities(13).sum() == pytest.approx(1.0)
            inactive = [i for i in range(13) if i not in s.active]
            assert np.all(s.full_probabilities(13)[inactive] == 0.0)

    def test_and_logic_protects_a_model_adjacent_from_a_principal_one(self) -> None:
        """Table I S5: discard only models that are unlikely **and** unprotected.

        A model the target is about to switch into is kept even while its probability is
        still negligible. Dropping that protection is one of the two ways `mwsim.vsimm`
        departs from the published algorithm.

        Only the protection half is asserted here. The converse does not hold and should
        not: S6 stops deleting once ``K`` models remain, so an unlikely and unprotected
        model legitimately survives whenever the set is already at the floor.
        """
        truth = lz.simulate(lz.acceleration_sequence(2), np.random.default_rng(11))
        _, _, states = _run(_filters("A"), truth, "A")
        protected = 0
        for s in states:
            mu = s.full_probabilities(13)
            principal = [i for i in s.active if mu[i] > lz.T_PRINCIPAL]
            if not principal:
                continue
            reachable: set[int] = set()
            for p in principal:
                reachable.update(np.flatnonzero(lz.ADJACENCY_A[p]).tolist())
            for i in s.active:
                if mu[i] < lz.T_UNLIKELY and i in reachable:
                    assert i in s.next_active, (
                        f"discarded m{i + 1}, which is unlikely but adjacent from a "
                        f"principal model - the AND logic should have protected it"
                    )
                    protected += 1
        assert protected > 0, "the protection rule never actually fired"

    def test_explain_reports_the_active_set(self) -> None:
        truth = lz.simulate(lz.acceleration_sequence(1), np.random.default_rng(4))
        _, _, states = _run(_filters("A"), truth, "A")
        assert "active" in states[-1].explain()


class TestOneStepBack:
    def test_it_measurably_improves_accuracy(self) -> None:
        """"One-step back is recommended and was used in our examples" (p. 455).

        A model activated mid-manoeuvre is otherwise born from a stale prediction and has
        to compete on the very measurement that triggered it. Running it over the previous
        measurement first is what closes most of our gap to the published numbers on the
        sparse topology.
        """
        with_back, _ = _rms("A", 2, _filters("A", one_step_back=True))
        without, _ = _rms("A", 2, _filters("A", one_step_back=False))
        assert with_back < without, f"{with_back:.2f} not better than {without:.2f}"


class TestReplicatesTableIV:
    """The paper's own experiment, run as the paper ran it."""

    @pytest.mark.parametrize(
        "topology,scenario,paper", [("A", 1, 37.15), ("A", 2, 41.52),
                                    ("B", 1, 35.28), ("B", 2, 36.47)]
    )
    def test_fixed_structure_imm_reproduces_the_published_error(
        self, topology: str, scenario: int, paper: float
    ) -> None:
        """Validates the whole transcription end to end.

        Thirteen models, a 13x13 transition matrix, two noise levels, a sampling period we
        had to infer and an initialisation the paper never states — and the answer lands
        within a few percent of the published number. A misread digit would not do that.
        """
        spec = lz.TOPOLOGIES[topology]
        imm = IMMFilter(lz.build_models(), spec["pi"], lz.H, lz.measurement_noise())
        rms, _ = _rms(topology, scenario, imm)
        assert rms == pytest.approx(paper, rel=0.08), (
            f"topology {topology} scenario {scenario}: {rms:.2f} m vs published {paper} m"
        )

    @pytest.mark.parametrize(
        "topology,scenario", [("A", 1), ("A", 2), ("B", 1), ("B", 2)]
    )
    def test_lms_does_not_beat_the_imm_on_accuracy(
        self, topology: str, scenario: int
    ) -> None:
        """The correction to DEC-41, asserted rather than asserted-away.

        This is not a failure to reproduce an advantage. Table IV reports plain LMS as
        slightly *worse* than IMM in all six of its cases, and so do we. Writing the
        assertion this way means that if a future change to `mwsim.lms` ever does produce
        an accuracy win here, the test fails and forces us to explain why we now disagree
        with the primary source.
        """
        spec = lz.TOPOLOGIES[topology]
        imm = IMMFilter(lz.build_models(), spec["pi"], lz.H, lz.measurement_noise())
        imm_rms, _ = _rms(topology, scenario, imm)
        lms_rms, _ = _rms(topology, scenario, _filters(topology))
        assert lms_rms >= imm_rms * 0.995, (
            f"LMS {lms_rms:.2f} m beat IMM {imm_rms:.2f} m, which the source does not report"
        )

    @pytest.mark.parametrize("topology,ceiling", [("A", 8.0), ("B", 11.0)])
    def test_lms_runs_far_fewer_filters(self, topology: str, ceiling: float) -> None:
        """The advantage that is real, and the one that matters to us.

        Compute is the axis the on-orbit fusion breakeven turns on (DEC-29), so a filter
        bank that costs half as much at matched accuracy is directly useful even though
        it wins nothing on error.
        """
        _, filters = _rms(topology, 2, _filters(topology))
        assert filters < ceiling, f"{filters:.2f} of 13 filters per step"

    def test_the_published_table_itself_shows_no_accuracy_advantage(self) -> None:
        """A guard on the claim, independent of our code entirely.

        Reads the transcribed Table IV and checks the direction of the published result.
        If someone later edits those constants, this fails.
        """
        from scripts.replicate_lms import PAPER_TABLE_IV

        for case, row in PAPER_TABLE_IV.items():
            assert row["LMS"] >= row["IMM"], f"{case}: LMS is not worse, as claimed"
        # The forgetting-factor variant is where the accuracy gain lives, and only on the
        # sparse topology.
        assert PAPER_TABLE_IV[("A", "2")]["LMS(lambda)"] < PAPER_TABLE_IV[("A", "2")]["IMM"]
        assert PAPER_TABLE_IV[("B", "1")]["LMS(lambda)"] >= (
            PAPER_TABLE_IV[("B", "1")]["IMM"] * 0.999
        )
