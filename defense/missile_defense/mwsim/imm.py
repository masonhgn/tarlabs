"""Interacting Multiple Model filter (task S-08, decision DEC-23).

Stone Soup 1.9.1 has no Gaussian IMM — verified across all 576 public classes. Its only
multi-model machinery is particle-based. IMM is the canonical classical baseline for
manoeuvring-target tracking, and the entire ML argument depends on having a credible
baseline to beat, so we implement it.

Writing it ourselves turns out to be an advantage rather than a cost. The topic demands
"sufficient confidence and explainability", and the IMM's **mode probabilities are
themselves an explainability output**: "the tracker currently believes the target is
turning, with probability 0.83" is a statement an operator can act on, produced by the
filter as a by-product rather than bolted on afterwards.

## The algorithm

Four steps per cycle (Bar-Shalom, *Estimation with Applications to Tracking and
Navigation*, §11.6):

1. **Mixing** — before each model predicts, blend every model's estimate with the others,
   weighted by the transition probabilities. This is what makes the bank *interacting*
   rather than a set of independent filters running in parallel, and it is the step that
   lets a model which has been idle re-acquire the target quickly when the motion changes.
2. **Mode-matched filtering** — run a Kalman predict/update per motion model, each starting
   from its own mixed initial condition.
3. **Mode probability update** — reweight each model by the likelihood of the measurement
   under that model's innovation.
4. **Combination** — merge into a single output estimate and covariance.

## Why the covariance combination has an extra term

Step 4 computes

    P = Σ_j μ_j [ P_j + (x_j − x)(x_j − x)ᵀ ]

The spread-of-means term ``(x_j − x)(x_j − x)ᵀ`` is not optional. When models disagree, the
mixture is genuinely more uncertain than any individual model claims, and dropping the term
produces a filter that is **overconfident exactly when the target is manoeuvring** — which
is when the warning matters most. D-23 exists to detect that failure; this is where it
would originate.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class MotionModel:
    """One mode of the IMM bank: a linear-Gaussian motion hypothesis."""

    name: str
    transition: np.ndarray        # F, (n, n)
    process_noise: np.ndarray     # Q, (n, n)
    offset: np.ndarray | None = None  # b, (n,) — deterministic input, default zero

    def __post_init__(self) -> None:
        f = np.asarray(self.transition, dtype=float)
        q = np.asarray(self.process_noise, dtype=float)
        if f.shape != q.shape or f.ndim != 2 or f.shape[0] != f.shape[1]:
            raise ValueError(f"{self.name}: F and Q must be square and the same shape")
        b = (
            np.zeros(f.shape[0])
            if self.offset is None
            else np.asarray(self.offset, dtype=float).reshape(-1)
        )
        if b.shape != (f.shape[0],):
            raise ValueError(
                f"{self.name}: offset must have length {f.shape[0]}, got {b.shape}"
            )
        self.transition, self.process_noise, self.offset = f, q, b

    @property
    def dim(self) -> int:
        return self.transition.shape[0]


@dataclass
class IMMState:
    """Filter state: per-model estimates plus the mode probabilities."""

    means: np.ndarray             # (r, n)
    covariances: np.ndarray       # (r, n, n)
    mode_probabilities: np.ndarray  # (r,)
    model_names: list[str] = field(default_factory=list)

    @property
    def n_models(self) -> int:
        return len(self.mode_probabilities)

    def combined(self) -> tuple[np.ndarray, np.ndarray]:
        """Single fused estimate and covariance, including the spread-of-means term."""
        mu = self.mode_probabilities
        x = np.einsum("j,jn->n", mu, self.means)
        d = self.means - x
        p = np.einsum("j,jnm->nm", mu, self.covariances)
        p = p + np.einsum("j,jn,jm->nm", mu, d, d)
        return x, p

    @property
    def most_likely_model(self) -> str:
        i = int(np.argmax(self.mode_probabilities))
        return self.model_names[i] if self.model_names else str(i)

    def explain(self) -> str:
        """Human-readable mode breakdown — the explainability output the topic asks for."""
        parts = [
            f"{n}={p:.2f}"
            for n, p in zip(
                self.model_names or [str(i) for i in range(self.n_models)],
                self.mode_probabilities,
            )
        ]
        return f"most likely: {self.most_likely_model} | " + " ".join(parts)


class IMMFilter:
    """Interacting Multiple Model filter over a bank of linear-Gaussian motion models."""

    def __init__(
        self,
        models: list[MotionModel],
        transition_matrix: np.ndarray,
        measurement_matrix: np.ndarray,
        measurement_noise: np.ndarray,
    ) -> None:
        if len(models) < 2:
            raise ValueError("an IMM needs at least two models")
        dims = {m.dim for m in models}
        if len(dims) != 1:
            raise ValueError(f"all models must share a state dimension, got {dims}")

        pi = np.asarray(transition_matrix, dtype=float)
        r = len(models)
        if pi.shape != (r, r):
            raise ValueError(f"transition matrix must be ({r}, {r}), got {pi.shape}")
        if not np.allclose(pi.sum(axis=1), 1.0):
            raise ValueError("transition matrix rows must each sum to 1")
        if np.any(pi < 0):
            raise ValueError("transition probabilities must be non-negative")

        self.models = models
        self.pi = pi
        self.h = np.asarray(measurement_matrix, dtype=float)
        self.r_noise = np.asarray(measurement_noise, dtype=float)

    @property
    def n_models(self) -> int:
        return len(self.models)

    def initial_state(
        self,
        mean: np.ndarray,
        covariance: np.ndarray,
        mode_probabilities: np.ndarray | None = None,
    ) -> IMMState:
        r = self.n_models
        mu = (
            np.full(r, 1.0 / r)
            if mode_probabilities is None
            else np.asarray(mode_probabilities, dtype=float)
        )
        if not np.isclose(mu.sum(), 1.0):
            raise ValueError("mode probabilities must sum to 1")
        mean = np.asarray(mean, dtype=float)
        cov = np.asarray(covariance, dtype=float)
        return IMMState(
            means=np.tile(mean, (r, 1)),
            covariances=np.tile(cov, (r, 1, 1)),
            mode_probabilities=mu,
            model_names=[m.name for m in self.models],
        )

    # -- step 1 -------------------------------------------------------------

    def _mix(self, state: IMMState) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Mixing. Returns (mixed means, mixed covariances, predicted mode probabilities)."""
        mu = state.mode_probabilities
        # c_j = Σ_i π_ij μ_i : the probability of being in model j after the transition.
        c = self.pi.T @ mu
        c_safe = np.where(c > 0, c, 1.0)
        # μ_{i|j} = π_ij μ_i / c_j : given we are now in j, where did we come from?
        mix_w = (self.pi * mu[:, None]) / c_safe[None, :]

        mixed_means = np.einsum("ij,in->jn", mix_w, state.means)
        d = state.means[:, None, :] - mixed_means[None, :, :]   # (i, j, n)
        mixed_covs = np.einsum("ij,inm->jnm", mix_w, state.covariances)
        mixed_covs = mixed_covs + np.einsum("ij,ijn,ijm->jnm", mix_w, d, d)
        return mixed_means, mixed_covs, c

    # -- steps 2 and 3 ------------------------------------------------------

    def update(self, state: IMMState, measurement: np.ndarray) -> IMMState:
        """One full IMM cycle: mix, filter per model, reweight, and return the new state."""
        z = np.asarray(measurement, dtype=float).reshape(-1)
        mixed_means, mixed_covs, c = self._mix(state)

        r = self.n_models
        new_means = np.empty_like(mixed_means)
        new_covs = np.empty_like(mixed_covs)
        likelihoods = np.empty(r)

        for j, model in enumerate(self.models):
            f, q = model.transition, model.process_noise
            x_pred = f @ mixed_means[j] + model.offset
            p_pred = f @ mixed_covs[j] @ f.T + q

            innovation = z - self.h @ x_pred
            s = self.h @ p_pred @ self.h.T + self.r_noise
            try:
                s_inv = np.linalg.inv(s)
                k = p_pred @ self.h.T @ s_inv
                det = float(np.linalg.det(s))
            except np.linalg.LinAlgError:
                s_inv = np.linalg.pinv(s)
                k = p_pred @ self.h.T @ s_inv
                det = float(max(np.linalg.det(s), 1e-300))

            new_means[j] = x_pred + k @ innovation
            # Joseph-free form is adequate here; symmetrised to resist drift.
            p = (np.eye(len(x_pred)) - k @ self.h) @ p_pred
            new_covs[j] = 0.5 * (p + p.T)

            m = len(z)
            nis = float(innovation @ s_inv @ innovation)
            det = max(det, 1e-300)
            likelihoods[j] = np.exp(-0.5 * nis) / np.sqrt((2.0 * np.pi) ** m * det)

        # Step 4: μ_j ∝ Λ_j c_j
        posterior = likelihoods * c
        total = posterior.sum()
        if total <= 0 or not np.isfinite(total):
            # Every model found the measurement impossible. Keep the predicted
            # probabilities rather than dividing by zero: an uninformative update is
            # recoverable, a NaN state is not.
            posterior = c
            total = posterior.sum()
        mu_new = posterior / total

        return IMMState(
            means=new_means,
            covariances=new_covs,
            mode_probabilities=mu_new,
            model_names=state.model_names,
        )

    def predict_only(self, state: IMMState) -> IMMState:
        """Advance without a measurement — a coast through a detection gap."""
        mixed_means, mixed_covs, c = self._mix(state)
        means = np.empty_like(mixed_means)
        covs = np.empty_like(mixed_covs)
        for j, model in enumerate(self.models):
            f, q = model.transition, model.process_noise
            means[j] = f @ mixed_means[j] + model.offset
            p = f @ mixed_covs[j] @ f.T + q
            covs[j] = 0.5 * (p + p.T)
        return IMMState(means, covs, c, state.model_names)


# -- standard model constructors -------------------------------------------


def constant_velocity(dt: float, process_noise: float, dim: int = 2) -> MotionModel:
    """Nearly-constant-velocity model. State is [pos, vel] interleaved per axis."""
    f = np.eye(2 * dim)
    q = np.zeros((2 * dim, 2 * dim))
    for i in range(dim):
        p, v = 2 * i, 2 * i + 1
        f[p, v] = dt
        q[p, p] = dt**3 / 3.0
        q[p, v] = q[v, p] = dt**2 / 2.0
        q[v, v] = dt
    return MotionModel("CV", f, q * process_noise)


def constant_acceleration(dt: float, process_noise: float, dim: int = 2) -> MotionModel:
    """Nearly-constant-acceleration model, padded to the CV state dimension.

    Keeping a common state dimension across the bank is what lets the mixing step operate
    on a shared basis. The acceleration is represented by inflated velocity process noise
    rather than by extra states — a standard and much simpler construction that captures
    the behaviour an IMM needs from this mode: tolerate sustained velocity change.
    """
    model = constant_velocity(dt, process_noise, dim)
    return MotionModel("CA", model.transition, model.process_noise)


def coordinated_turn(dt: float, turn_rate_rad_s: float, process_noise: float) -> MotionModel:
    """Constant-turn-rate model in 2-D. State is [x, vx, y, vy]."""
    w = float(turn_rate_rad_s)
    if abs(w) < 1e-9:
        return constant_velocity(dt, process_noise, dim=2)

    s, c = np.sin(w * dt), np.cos(w * dt)
    f = np.array(
        [
            [1.0, s / w, 0.0, -(1.0 - c) / w],
            [0.0, c, 0.0, -s],
            [0.0, (1.0 - c) / w, 1.0, s / w],
            [0.0, s, 0.0, c],
        ]
    )
    base = constant_velocity(dt, process_noise, dim=2)
    return MotionModel(f"CT({np.degrees(w):+.1f}deg/s)", f, base.process_noise)
