"""The Likely-Model Set algorithm (LMS3) exactly as published, for replication.

Source: Li & Zhang (2000), Table I, "One Cycle of LMS3 Algorithm with AND Logic", and
Section IV.A. See `mwsim.lz2000` for the benchmark this is validated against.

## Why this exists alongside `mwsim.vsimm`

`vsimm.py` is our own simplified variable-structure IMM, written from the Li & Jilkov
survey's prose description. It differs from the published algorithm in two ways that turn
out to matter:

1. **Activation.** `vsimm` seeds a newly activated model from the current *combined*
   estimate. LMS3 runs a second VSIMM cycle, ``VSIMM[M_n, M_{k-1}]``, so a new model is
   mixed from the previous model set through the transition matrix and then filters the
   same measurement that justified activating it. A combined-estimate seed throws away the
   mode structure; the published version does not.
2. **Deletion.** `vsimm` discards any model below the lower threshold. LMS3 discards only
   models that are unlikely **and** not adjacent from a principal model — that is the "AND
   logic" of the table's title. A model the target is about to switch into is protected
   even while its probability is still negligible.

Both differences penalise the variable-structure filter at exactly the moment a manoeuvre
starts, which is where tracking error concentrates. Reproducing the published result
requires the published algorithm.

## The cycle (Table I)

* **S1** Run ``VSIMM[M_k, M_{k-1}]``.
* **S2** Classify each model in ``M_k``: principal (``mu > t2``), unlikely (``mu < t1``),
  significant otherwise. If neither a principal nor an unlikely model exists, output and
  carry ``M_k`` forward unchanged.
* **S3** If a principal model exists, let ``M_a`` be everything adjacent from a principal
  model and ``M_n = M_a \\ M_k`` the genuinely new models. Run ``VSIMM[M_n, M_{k-1}]`` and
  fuse over the union.
* **S4** Output.
* **S5** ``M_d = M_u \\ M_a`` — unlikely *and* unprotected.
* **S6/S7** Delete the lowest-probability members of ``M_d`` while at least ``K`` models
  remain; the survivors are ``M_{k+1}``.

## A note on the bookkeeping

Estimates live over the *enlarged* set produced by S3, while ``M_{k+1}`` from S6 is the
*pruned* set. The next cycle therefore mixes from the enlarged set into the pruned one,
which is what makes ``VSIMM[M_k, M_{k-1}]`` rectangular. Our `IMMFilter` mixes a set into
itself; that is a special case, and it is why the replication needs its own cycle here
rather than reusing `IMMFilter.update`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .imm import MotionModel


@dataclass
class _Cycle:
    """Output of one VSIMM[target, source] cycle, before normalisation."""

    means: np.ndarray          # (n_target, n)
    covariances: np.ndarray    # (n_target, n, n)
    likelihoods: np.ndarray    # (n_target,)  L^i_k
    predicted: np.ndarray      # (n_target,)  mu-hat^i_{k|k-1}, NOT normalised


@dataclass
class LMSState:
    """Estimates over the enlarged model set, plus the set carried to the next step."""

    active: list[int]            # the enlarged M_k, indices into the full bank
    means: np.ndarray            # (len(active), n)
    covariances: np.ndarray      # (len(active), n, n)
    probabilities: np.ndarray    # (len(active),) sums to 1
    next_active: list[int]       # M_{k+1} from S6
    n_filters_run: int = 0       # mode-matched filters run this step, for cost accounting
    forgetting: float = 1.0
    model_names: list[str] = field(default_factory=list)

    # Unnormalised L^i_k and mu-hat^i_{k|k-1} over ``active``. Kept so that a model
    # activated one step later can be weighed against these on a common scale.
    likelihoods: np.ndarray | None = None
    predicted: np.ndarray | None = None

    # One step of history, for the paper's one-step-back activation: the set this step
    # mixed *from*, and the measurement processed to reach the present step.
    prev: "LMSState | None" = None
    measurement: np.ndarray | None = None

    @property
    def n_active(self) -> int:
        return len(self.active)

    def combined(self) -> tuple[np.ndarray, np.ndarray]:
        mu = self.probabilities
        x = np.einsum("j,jn->n", mu, self.means)
        d = self.means - x
        p = np.einsum("j,jnm->nm", mu, self.covariances)
        p = p + np.einsum("j,jn,jm->nm", mu, d, d)
        return x, p

    def full_probabilities(self, n_models: int) -> np.ndarray:
        out = np.zeros(n_models)
        out[self.active] = self.probabilities
        return out

    @property
    def most_likely_model(self) -> str:
        i = int(np.argmax(self.probabilities))
        return (
            self.model_names[self.active[i]] if self.model_names else str(self.active[i])
        )

    def explain(self) -> str:
        return (
            f"most likely: {self.most_likely_model} | "
            f"active {self.n_active} of {len(self.model_names) or '?'}"
        )


class LMSFilter:
    """LMS3 with AND logic, per Li & Zhang (2000) Table I."""

    def __init__(
        self,
        models: list[MotionModel],
        transition_matrix: np.ndarray,
        measurement_matrix: np.ndarray,
        measurement_noise: np.ndarray,
        adjacency: np.ndarray,
        *,
        t_unlikely: float = 1e-4,
        t_principal: float = 0.3,
        k_floor: int = 2,
        forgetting: tuple[float, float] | None = None,
        one_step_back: bool = True,
        iterate_expansion: bool = False,
        dt: float = 1.0,
    ) -> None:
        if not 0.0 < t_unlikely < t_principal < 1.0:
            raise ValueError(
                f"need 0 < t1 < t2 < 1, got {t_unlikely}, {t_principal}"
            )
        n = len(models)
        adjacency = np.asarray(adjacency, dtype=bool)
        if adjacency.shape != (n, n):
            raise ValueError(f"adjacency must be ({n}, {n}), got {adjacency.shape}")

        self.models = models
        self.pi = np.asarray(transition_matrix, dtype=float)
        self.h = np.asarray(measurement_matrix, dtype=float)
        self.r_noise = np.asarray(measurement_noise, dtype=float)
        self.adjacency = adjacency
        self.t_unlikely = t_unlikely
        self.t_principal = t_principal
        self.k_floor = min(max(k_floor, 1), n)
        # LMS(lambda): (lambda_nought, lambda_zero) of equations (18)-(20).
        self.forgetting = forgetting
        # "A good and systematic technique is to go back several steps in time to
        # initialize the newly activated models and their filters... One-step back is
        # recommended and was used in our examples." (pp. 454-455)
        self.one_step_back = one_step_back
        # "A possible cure or alleviation of this weakness is by repeatedly applying the
        # three adaptation rules in each time step until nothing changes... if a newly
        # activated model turns out to be a principal one at the time when it is
        # activated according to the posterior probabilities, then activate the models
        # adjacent from it immediately" (p. 454). Offered as a remedy for LMS3's
        # "weakness in handling jumps between two widely separated modes that are
        # connected only through several intermediate modes" -- but *not* stated to have
        # been used for the published results, so it is off by default.
        self.iterate_expansion = iterate_expansion
        self.dt = dt
        self._accel_threshold = np.sqrt(2.0 * float(np.max(np.diag(self.r_noise))))

    @property
    def n_models(self) -> int:
        return len(self.models)

    # -- the VSIMM cycle ----------------------------------------------------

    def _vsimm(
        self,
        source: list[int],
        source_means: np.ndarray,
        source_covs: np.ndarray,
        source_probs: np.ndarray,
        target: list[int],
        z: np.ndarray,
        inflate: float = 1.0,
    ) -> _Cycle:
        """``VSIMM[target, source]``: mix across sets, predict, update.

        ``predicted`` is deliberately left unnormalised. S3 fuses the results of two
        separate cycles, and they are only commensurable on a common scale — normalising
        each cycle independently would silently reweight the new models against the old.
        """
        pi_sub = self.pi[np.ix_(source, target)]           # (n_src, n_tgt)
        c = pi_sub.T @ source_probs                        # unnormalised mu-hat
        c_safe = np.where(c > 0, c, 1.0)
        w = (pi_sub * source_probs[:, None]) / c_safe[None, :]

        mixed_means = np.einsum("ij,in->jn", w, source_means)
        d = source_means[:, None, :] - mixed_means[None, :, :]
        mixed_covs = np.einsum("ij,inm->jnm", w, source_covs)
        mixed_covs = mixed_covs + np.einsum("ij,ijn,ijm->jnm", w, d, d)

        # Equation (18): inflate a newly activated model's covariance to acknowledge that
        # it has not been tracking. Only ever applied to the M_n cycle.
        if inflate != 1.0:
            mixed_covs = mixed_covs / inflate

        n_state = source_means.shape[1]
        means = np.empty((len(target), n_state))
        covs = np.empty((len(target), n_state, n_state))
        likelihoods = np.empty(len(target))
        eye = np.eye(n_state)
        m = len(z)

        for j, model_index in enumerate(target):
            model = self.models[model_index]
            f, q, b = model.transition, model.process_noise, model.offset
            x_pred = f @ mixed_means[j] + b
            p_pred = f @ mixed_covs[j] @ f.T + q

            innovation = z - self.h @ x_pred
            s = self.h @ p_pred @ self.h.T + self.r_noise
            try:
                s_inv = np.linalg.inv(s)
                det = float(np.linalg.det(s))
            except np.linalg.LinAlgError:
                s_inv = np.linalg.pinv(s)
                det = float(max(np.linalg.det(s), 1e-300))
            k_gain = p_pred @ self.h.T @ s_inv

            means[j] = x_pred + k_gain @ innovation
            p = (eye - k_gain @ self.h) @ p_pred
            covs[j] = 0.5 * (p + p.T)

            nis = float(innovation @ s_inv @ innovation)
            likelihoods[j] = np.exp(-0.5 * nis) / np.sqrt(
                (2.0 * np.pi) ** m * max(det, 1e-300)
            )

        return _Cycle(means=means, covariances=covs, likelihoods=likelihoods, predicted=c)

    # -- initialisation -----------------------------------------------------

    def initial_state(
        self,
        mean: np.ndarray,
        covariance: np.ndarray,
        mode_probabilities: np.ndarray,
    ) -> LMSState:
        """Seed from a full-bank probability vector; models at zero are simply inactive."""
        mu = np.asarray(mode_probabilities, dtype=float)
        active = sorted(np.flatnonzero(mu > 0).tolist())
        if len(active) < 1:
            raise ValueError("at least one model must have non-zero initial probability")
        mean = np.asarray(mean, dtype=float)
        cov = np.asarray(covariance, dtype=float)
        lam = self.forgetting[1] if self.forgetting else 1.0
        return LMSState(
            active=active,
            means=np.tile(mean, (len(active), 1)),
            covariances=np.tile(cov, (len(active), 1, 1)),
            probabilities=mu[active] / mu[active].sum(),
            next_active=list(active),
            forgetting=lam,
            model_names=[m.name for m in self.models],
        )

    # -- one full LMS3 cycle ------------------------------------------------

    def update(self, state: LMSState, measurement: np.ndarray) -> LMSState:
        z = np.asarray(measurement, dtype=float).reshape(-1)
        target = list(state.next_active)

        # S1 -----------------------------------------------------------------
        cycle = self._vsimm(
            state.active, state.means, state.covariances, state.probabilities, target, z
        )
        mu = self._normalise(cycle.likelihoods, cycle.predicted)
        n_filters = len(target)

        # S2 -----------------------------------------------------------------
        principal = [target[i] for i in range(len(target)) if mu[i] > self.t_principal]
        unlikely = [target[i] for i in range(len(target)) if mu[i] < self.t_unlikely]

        active = list(target)
        means, covs = cycle.means, cycle.covariances
        likelihoods, predicted = cycle.likelihoods, cycle.predicted
        lam = state.forgetting

        if not principal and not unlikely:
            # "output ..., let M_{k+1} = M_k and go to Step 1"
            return self._finish(state, z, active, means, covs, mu, likelihoods,
                                predicted, list(active), n_filters, lam)

        # S3 -----------------------------------------------------------------
        adjacent = set()
        expanding = list(principal)
        for _ in range(self.n_models):
            if not expanding:
                break
            reachable = set()
            for model_index in expanding:
                reachable.update(np.flatnonzero(self.adjacency[model_index]).tolist())
            adjacent.update(reachable)
            new = sorted(reachable - set(active))
            if not new:
                break

            lam = self._advance_forgetting(state, means, covs, mu, lam)
            inflate = lam if self.forgetting else 1.0
            source, s_means, s_covs, s_probs, back_filters = self._activation_source(
                state, new
            )
            n_filters += back_filters
            extra = self._vsimm(
                source, s_means, s_covs, s_probs, new, z, inflate=inflate
            )
            n_filters += len(new)

            active = active + new
            means = np.concatenate([means, extra.means], axis=0)
            covs = np.concatenate([covs, extra.covariances], axis=0)
            likelihoods = np.concatenate([likelihoods, extra.likelihoods])
            predicted = np.concatenate([predicted, extra.predicted])
            mu = self._normalise(likelihoods, predicted)

            order = np.argsort(active)
            active = [active[i] for i in order]
            means, covs, mu = means[order], covs[order], mu[order]
            likelihoods, predicted = likelihoods[order], predicted[order]

            if not self.iterate_expansion:
                break
            # Re-classify only the models just activated, on their posterior probability.
            position = {m: i for i, m in enumerate(active)}
            expanding = [m for m in new if mu[position[m]] > self.t_principal]

        # S5, S6, S7 ----------------------------------------------------------
        discardable = [m for m in unlikely if m not in adjacent]
        survivors = list(active)
        if discardable:
            position = {m: i for i, m in enumerate(active)}
            # Smallest probability first, stopping at the K floor.
            for model_index in sorted(discardable, key=lambda m: mu[position[m]]):
                if len(survivors) <= self.k_floor:
                    break
                survivors.remove(model_index)

        return self._finish(state, z, active, means, covs, mu, likelihoods, predicted,
                            survivors, n_filters, lam)

    @staticmethod
    def _normalise(likelihoods, predicted):
        """``mu = L * mu-hat / sum``, falling back to the prior if every model balks."""
        posterior = likelihoods * predicted
        total = posterior.sum()
        if total <= 0 or not np.isfinite(total):
            posterior = predicted
            total = max(posterior.sum(), 1e-300)
        return posterior / total

    def _activation_source(self, state: LMSState, new: list[int]):
        """Where a newly activated model starts from.

        Without one-step-back this is simply ``M_{k-1}``, as Table I's
        ``VSIMM[M_n, M_{k-1}]`` says. With it, the paper's recommendation applies:

            "If a model is activated at k, then n-step back means that it has zero
            probability at k-n-1 but in general non-zero probability at k-n. Thus, we may
            run the generic VSIMM recursion of Part II several times."

        So a new model is first run over the *previous* measurement, starting from
        ``M_{k-2}``, and the result is appended to ``M_{k-1}`` to form the set that the
        time-``k`` cycle mixes from. The model therefore arrives having already seen one
        measurement, rather than being born mid-manoeuvre from a stale prediction.

        The paper is explicit that this must not rewrite history — *"old overall estimate
        (and everything that has already been sent out) may not be overridden"* — so the
        augmented probabilities only launch the new models. The output already published
        for step ``k-1`` stands.

        Returns the source set, its estimates and probabilities, and the number of extra
        mode-matched filters this cost.
        """
        if not (self.one_step_back and state.prev is not None):
            return state.active, state.means, state.covariances, state.probabilities, 0

        history = state.prev
        back = self._vsimm(
            history.active,
            history.means,
            history.covariances,
            history.probabilities,
            new,
            state.measurement,
        )
        likelihoods = np.concatenate([state.likelihoods, back.likelihoods])
        predicted = np.concatenate([state.predicted, back.predicted])
        return (
            state.active + new,
            np.concatenate([state.means, back.means], axis=0),
            np.concatenate([state.covariances, back.covariances], axis=0),
            self._normalise(likelihoods, predicted),
            len(new),
        )

    def _advance_forgetting(
        self,
        state: LMSState,
        means: np.ndarray,
        covs: np.ndarray,
        mu: np.ndarray,
        lam: float,
    ) -> float:
        """Equations (19) and (20): reset on a detected manoeuvre, else relax toward 1."""
        if not self.forgetting:
            return 1.0
        lam_rate, lam_zero = self.forgetting
        x_now = np.einsum("j,jn->n", mu, means)
        x_prev, _ = state.combined()
        accel = np.hypot(
            (x_now[1] - x_prev[1]) / self.dt, (x_now[3] - x_prev[3]) / self.dt
        )
        if accel > self._accel_threshold:
            return lam_zero
        return 1.0 - lam_rate + lam_rate * lam

    def _finish(
        self,
        previous: LMSState,
        measurement: np.ndarray,
        active: list[int],
        means: np.ndarray,
        covs: np.ndarray,
        mu: np.ndarray,
        likelihoods: np.ndarray,
        predicted: np.ndarray,
        survivors: list[int],
        n_filters: int,
        lam: float,
    ) -> LMSState:
        # Only one step of history is retained; dropping the grandparent keeps the chain
        # from growing without bound over a long track.
        history = LMSState(
            active=previous.active,
            means=previous.means,
            covariances=previous.covariances,
            probabilities=previous.probabilities,
            next_active=previous.next_active,
            forgetting=previous.forgetting,
            likelihoods=previous.likelihoods,
            predicted=previous.predicted,
            model_names=previous.model_names,
        )
        return LMSState(
            active=active,
            means=means,
            covariances=covs,
            probabilities=mu / mu.sum(),
            next_active=sorted(survivors),
            n_filters_run=n_filters,
            forgetting=lam,
            model_names=[m.name for m in self.models],
            likelihoods=likelihoods,
            predicted=predicted,
            prev=history,
            measurement=measurement,
        )
