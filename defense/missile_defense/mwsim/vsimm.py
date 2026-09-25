"""Variable-structure IMM, first cut — **superseded by `mwsim.lms` (DEC-43)**.

This module was written from the Li & Jilkov survey's *prose* description of the
Likely-Model Set algorithm. `mwsim.lms` implements the algorithm as actually published
(Li & Zhang 2000, Table I) and is the one to use. The two differ in ways that turn out to
change the measured answer:

* a newly activated model here is seeded from the combined estimate; the published
  algorithm runs a proper ``VSIMM[M_n, M_{k-1}]`` cycle and, on the authors' own
  recommendation, first runs the new model over the *previous* measurement;
* deletion here drops anything below the lower threshold, where the published algorithm
  protects a model that is unlikely **but** adjacent from a principal one.

Both simplifications bite hardest at the start of a manoeuvre. Retained for history and
because its tests still document the general behaviour of a variable-structure bank; not
retained as evidence for anything.

**Withdrawn:** this module's docstrings previously carried a measured table of accuracy
versus adjacency bandwidth, and the survey quotation that LMS *"substantially
outperforms"* fixed-structure IMM. Both are withdrawn. The measurements were made with
the simplified algorithm above on a scenario we invented, and the survey sentence does not
survive contact with its primary source — Table IV of Li & Zhang reports plain LMS as
slightly *worse* than fixed-structure IMM in all six of its cases. See
`analysis/validation/lms_replication.md`.

What does survive, and is reproduced from the paper's own experiment, is the
cost-effectiveness claim: matched accuracy at roughly half the filters. That is the part
this study needs, because compute is the axis the on-orbit fusion breakeven turns on
(DEC-29).

## The algorithm

At each step, classify every model in the active set by its mode probability:

* **unlikely** — below ``t_unlikely``; discard it,
* **significant** — between the thresholds; keep it,
* **principal** — above ``t_principal``; keep it, *and* activate every model it may switch
  to under the adjacency graph.

The adjacency graph encodes which motion changes are physically reachable in one step.
Without it, expansion would simply re-activate everything and the structure would stop
being variable.

## The honesty problem, stated up front

LMS has tuning knobs — two thresholds and a graph — and a badly tuned variable-structure
filter is a strawman that makes anything look good by comparison. The defaults here are
the survey's own suggested behaviour rather than values chosen to flatter a later result,
``tune`` exists so the thresholds can be fitted on held-out data, and the active-set size
is reported so a reviewer can see whether the structure actually varied or silently
collapsed to a fixed set.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .imm import IMMFilter, IMMState, MotionModel


@dataclass
class VSIMMState:
    """IMM state plus the currently active model subset."""

    inner: IMMState
    active: list[int]              # indices into the full model bank
    full_probabilities: np.ndarray  # (n_full,) zero for inactive models

    @property
    def n_active(self) -> int:
        return len(self.active)

    def combined(self) -> tuple[np.ndarray, np.ndarray]:
        return self.inner.combined()

    @property
    def most_likely_model(self) -> str:
        return self.inner.most_likely_model

    def explain(self) -> str:
        """Explainability output: what is believed, and what is even being considered.

        The active set is as informative as the probabilities — "the tracker has stopped
        considering the ballistic hypothesis entirely" is an operator-relevant statement
        that a fixed-structure filter cannot make.
        """
        return f"{self.inner.explain()} | active {self.n_active} of {len(self.full_probabilities)}"


def full_adjacency(n_models: int) -> np.ndarray:
    """Every model reachable from every other. Use only as a deliberate baseline.

    With full adjacency, expansion re-activates the whole bank whenever any model is
    principal, so the filter degenerates to a fixed-structure IMM. Useful precisely as a
    control: if LMS with full adjacency does not match the fixed-structure result, the
    implementation is wrong.
    """
    return np.ones((n_models, n_models), dtype=bool)


def banded_adjacency(n_models: int, bandwidth: int = 2) -> np.ndarray:
    """Models may switch to any model within ``bandwidth`` places in an ordered bank.

    Adjacency decides how far the target can move through the model space in one step, so
    a graph that is too sparse forces a manoeuvring target to walk its bank one neighbour
    at a time — and mode changes are exactly where tracking error spikes.

    **Withdrawn:** a table of accuracy against bandwidth previously appeared here. It was
    measured with this module's simplified activation and deletion rules on a scenario we
    invented, and most of the penalty it attributed to narrow adjacency was an artifact of
    those simplifications rather than of the bandwidth. See the module docstring and
    `mwsim.lz2000` for the published graphs and the published result.

    A real instance of the effect does survive, in the source rather than in our
    measurements: Li & Zhang's sparse topology A is a 4-connected grid in which the outer
    acceleration ring is unreachable from the origin in one step, and the paper names the
    resulting "weakness in handling jumps between two widely separated modes that are
    connected only through several intermediate modes".
    """
    if bandwidth < 1:
        raise ValueError("bandwidth must be at least 1")
    a = np.zeros((n_models, n_models), dtype=bool)
    for i in range(n_models):
        lo, hi = max(0, i - bandwidth), min(n_models, i + bandwidth + 1)
        a[i, lo:hi] = True
    return a


def chain_adjacency(n_models: int) -> np.ndarray:
    """Nearest-neighbour switching only. Equivalent to ``banded_adjacency(n, 1)``.

    Retained because it is the obvious first thing to reach for and the measured result
    is a useful warning: see `banded_adjacency` for why bandwidth 1 costs accuracy.
    """
    return banded_adjacency(n_models, 1)


class VSIMMFilter:
    """Likely-Model Set variable-structure IMM over a full bank of motion models."""

    def __init__(
        self,
        models: list[MotionModel],
        transition_matrix: np.ndarray,
        measurement_matrix: np.ndarray,
        measurement_noise: np.ndarray,
        *,
        adjacency: np.ndarray | None = None,
        t_unlikely: float = 0.05,
        t_principal: float = 0.30,
        min_active: int = 2,
    ) -> None:
        if not 0.0 < t_unlikely < t_principal < 1.0:
            raise ValueError(
                f"need 0 < t_unlikely < t_principal < 1, got {t_unlikely}, {t_principal}"
            )
        if min_active < 2:
            raise ValueError("an IMM needs at least two active models")

        self.models = models
        self.pi_full = np.asarray(transition_matrix, dtype=float)
        self.h = np.asarray(measurement_matrix, dtype=float)
        self.r_noise = np.asarray(measurement_noise, dtype=float)
        self.adjacency = (
            full_adjacency(len(models)) if adjacency is None
            else np.asarray(adjacency, dtype=bool)
        )
        if self.adjacency.shape != (len(models), len(models)):
            raise ValueError("adjacency must be (n_models, n_models)")

        self.t_unlikely = t_unlikely
        self.t_principal = t_principal
        self.min_active = min(min_active, len(models))

    @property
    def n_models(self) -> int:
        return len(self.models)

    def _sub_filter(self, active: list[int]) -> IMMFilter:
        """An IMM over just the active subset, with its transition matrix renormalised."""
        pi = self.pi_full[np.ix_(active, active)]
        row = pi.sum(axis=1, keepdims=True)
        # Renormalise: dropping models removes probability mass that must go somewhere,
        # and leaving the rows sub-stochastic would quietly leak probability each step.
        pi = np.divide(pi, row, out=np.full_like(pi, 1.0 / len(active)), where=row > 0)
        return IMMFilter([self.models[i] for i in active], pi, self.h, self.r_noise)

    def initial_state(
        self, mean: np.ndarray, covariance: np.ndarray, active: list[int] | None = None
    ) -> VSIMMState:
        active = list(range(self.n_models)) if active is None else sorted(active)
        inner = self._sub_filter(active).initial_state(mean, covariance)
        full = np.zeros(self.n_models)
        full[active] = inner.mode_probabilities
        return VSIMMState(inner=inner, active=active, full_probabilities=full)

    def _next_active(self, active: list[int], probabilities: np.ndarray) -> list[int]:
        """The LMS structure update: discard unlikely, keep significant, expand principal."""
        keep: set[int] = set()
        principal: list[int] = []

        for local, model_index in enumerate(active):
            p = probabilities[local]
            if p >= self.t_principal:
                keep.add(model_index)
                principal.append(model_index)
            elif p >= self.t_unlikely:
                keep.add(model_index)

        # Expansion: activate whatever the principal models can switch to.
        for model_index in principal:
            keep.update(np.flatnonzero(self.adjacency[model_index]).tolist())

        # Never drop below the floor; top up with the highest-probability models dropped.
        if len(keep) < self.min_active:
            order = np.argsort(probabilities)[::-1]
            for local in order:
                keep.add(active[local])
                if len(keep) >= self.min_active:
                    break
        return sorted(keep)

    def update(self, state: VSIMMState, measurement: np.ndarray) -> VSIMMState:
        """One cycle: **adapt the active set first, then filter with it.**

        Ordering matters and the survey is explicit about it: models in ``M_{k-1}`` are
        classified, ``M_k`` is derived from that classification, and ``M_k`` is the set in
        effect at time ``k``. Filtering with ``M_{k-1}`` and adapting afterwards introduces
        a one-step lag — a newly activated model cannot compete for the very measurement
        that justified activating it.

        That lag costs most precisely when a manoeuvre begins, which is when the filter
        matters. Measured on a nine-model coordinated-turn bank it degraded accuracy by
        ~20% against fixed-structure IMM with narrow adjacency, and the penalty shrank as
        adjacency widened — the signature of a timing problem being masked by allowing
        larger jumps, rather than of a pruning problem.
        """
        # Step 1: structure adaptation, from the probabilities currently in effect.
        new_active = self._next_active(state.active, state.inner.mode_probabilities)

        # Carry state across the structure change. Models that stay keep their estimate;
        # models being activated start from the combined estimate, which is the
        # information the bank currently holds about the target.
        combined_mean, combined_cov = state.inner.combined()
        old = {m: i for i, m in enumerate(state.active)}

        means, covs, probs = [], [], []
        for m in new_active:
            if m in old:
                means.append(state.inner.means[old[m]])
                covs.append(state.inner.covariances[old[m]])
                probs.append(state.inner.mode_probabilities[old[m]])
            else:
                means.append(combined_mean)
                covs.append(combined_cov)
                # A newly activated model starts at the unlikely threshold: present, but
                # not yet believed. Starting at zero would make it unrecoverable.
                probs.append(self.t_unlikely)

        probs = np.asarray(probs, dtype=float)
        probs = probs / probs.sum()

        carried = IMMState(
            means=np.asarray(means),
            covariances=np.asarray(covs),
            mode_probabilities=probs,
            model_names=[self.models[m].name for m in new_active],
        )

        # Step 2: filter this measurement with the set now in effect.
        inner = self._sub_filter(new_active).update(carried, measurement)

        full = np.zeros(self.n_models)
        full[new_active] = inner.mode_probabilities
        return VSIMMState(inner=inner, active=new_active, full_probabilities=full)


def tune(
    build_filter,
    measurements: np.ndarray,
    truth: np.ndarray,
    *,
    candidates=((0.02, 0.2), (0.05, 0.3), (0.10, 0.4), (0.15, 0.5)),
) -> tuple[float, float]:
    """Choose thresholds on held-out data rather than to flatter a later result.

    ``build_filter(t_unlikely, t_principal)`` returns a configured ``VSIMMFilter``.
    Selection is by RMS position error against truth.

    This exists because a badly tuned variable-structure filter is a strawman. If the
    classical baseline is hand-crippled, every comparison against it is worthless — and a
    reviewer is entitled to ask how the thresholds were picked.
    """
    best, best_err = candidates[0], np.inf
    for t_low, t_high in candidates:
        f = build_filter(t_low, t_high)
        s = f.initial_state(truth[0], np.eye(len(truth[0])) * 10.0)
        errs = []
        for z, x_true in zip(measurements, truth):
            s = f.update(s, z)
            x, _ = s.combined()
            errs.append(np.linalg.norm(x - x_true))
        err = float(np.sqrt(np.mean(np.square(errs))))
        if err < best_err:
            best, best_err = (t_low, t_high), err
    return best
