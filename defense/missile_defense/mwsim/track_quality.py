"""Track quality: what we measure, and what we explicitly do not claim (task D-23).

The topic asks for results against **accuracy, latency, resilience and coverage**, and
separately demands "sufficient confidence and explainability". It also uses the term
*fire-control quality*, whose numeric thresholds are classified and which no public source
quantifies (D-04, open item C-4).

So this module defines **our** metric. Three commitments follow from that:

1. Everything here is computable from our own simulation and stated in the open.
2. Nothing here is claimed to equal the classified fire-control threshold. Where a
   threshold is needed, it is a swept parameter, and results are reported as *relative*
   comparisons between architectures rather than as absolute qualification.
3. The metric includes whether the filter is **honest about its own uncertainty**, not just
   whether it is accurate. A tracker that is wrong is a problem; a tracker that is wrong
   while reporting high confidence is a different and worse problem for a warning mission.

## Why covariance consistency is the important one

Accuracy alone cannot support a warning decision. An operator handed a track needs to know
how much to trust it, and that trust comes from the reported covariance. If the filter's
covariance is optimistic, every downstream consumer — association gating, handover, the
decision itself — inherits a false confidence that nothing else in the chain will catch.

**NEES** (normalised estimation error squared) tests exactly this. For an unbiased filter
with a correct covariance, NEES has expectation equal to the state dimension. Consistently
above that means overconfident; consistently below means needlessly conservative. This is
the quantitative form of the topic's "sufficient confidence" requirement, and it is
reportable without knowing any classified threshold.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

#: Chi-square 95% bounds for the NEES average over N samples, per degree of freedom.
#: Used to decide whether a filter's covariance is consistent rather than eyeballing it.
_CHI2_95 = {1: (0.001, 5.02), 2: (0.05, 3.69), 3: (0.22, 3.12), 6: (0.68, 2.41)}


@dataclass(frozen=True)
class TrackQuality:
    """Quality of one track against truth, over its lifetime."""

    rms_position_error_km: float
    max_position_error_km: float
    #: RMS 3-D position uncertainty the filter reports, sqrt(trace(P)) — deliberately the
    #: same quantity as rms_position_error_km so the two are directly comparable. Using
    #: the per-axis sigma sqrt(trace(P)/3) here instead makes an honest filter score
    #: 1/sqrt(3) and read as overconfident.
    mean_reported_sigma_km: float
    nees_mean: float
    state_dimension: int
    consistency: str            # 'consistent' | 'overconfident' | 'conservative'
    custody_fraction: float
    longest_custody_s: float
    n_samples: int

    @property
    def is_consistent(self) -> bool:
        return self.consistency == "consistent"

    @property
    def confidence_ratio(self) -> float:
        """Reported sigma over actual RMS error.

        Near 1 means the filter's stated uncertainty matches reality. Below 1 means it is
        claiming more precision than it has — the dangerous direction.
        """
        return (
            self.mean_reported_sigma_km / self.rms_position_error_km
            if self.rms_position_error_km > 0
            else float("inf")
        )


def position_errors_km(estimated_km: np.ndarray, truth_km: np.ndarray) -> np.ndarray:
    """Per-sample 3-D position error magnitude."""
    e = np.atleast_2d(np.asarray(estimated_km, dtype=float))
    t = np.atleast_2d(np.asarray(truth_km, dtype=float))
    if e.shape != t.shape:
        raise ValueError(f"shape mismatch: estimate {e.shape} vs truth {t.shape}")
    return np.linalg.norm(e - t, axis=-1)


def nees(
    estimated_km: np.ndarray, truth_km: np.ndarray, covariance_km2: np.ndarray
) -> np.ndarray:
    """Normalised estimation error squared, per sample.

        NEES = (x̂ − x)ᵀ P⁻¹ (x̂ − x)

    For a consistent filter this has expectation equal to the state dimension. Singular or
    near-singular covariances yield ``inf`` rather than a pseudo-inverse: a filter claiming
    zero uncertainty in some direction is making an infinitely strong claim, and averaging
    that away would hide it.
    """
    e = np.atleast_2d(np.asarray(estimated_km, dtype=float))
    t = np.atleast_2d(np.asarray(truth_km, dtype=float))
    p = np.asarray(covariance_km2, dtype=float)
    if p.ndim == 2:
        p = np.broadcast_to(p, (len(e), *p.shape))

    out = np.empty(len(e))
    for i, (err, cov) in enumerate(zip(e - t, p)):
        try:
            if np.linalg.cond(cov) > 1e12:
                out[i] = np.inf
                continue
            out[i] = float(err @ np.linalg.solve(cov, err))
        except np.linalg.LinAlgError:
            out[i] = np.inf
    return out


def classify_consistency(nees_values: np.ndarray, state_dimension: int) -> str:
    """Is the filter's reported covariance consistent with its actual error?

    Compares the average NEES against chi-square bounds. 'overconfident' is the finding
    that matters: the filter is claiming more certainty than it has earned.
    """
    finite = np.asarray(nees_values)[np.isfinite(nees_values)]
    if finite.size == 0:
        return "overconfident"

    mean_per_dof = float(np.mean(finite)) / state_dimension
    lo, hi = _CHI2_95.get(state_dimension, (0.5, 2.0))
    if mean_per_dof > hi:
        return "overconfident"
    if mean_per_dof < lo:
        return "conservative"
    return "consistent"


def custody_intervals(
    times_s: np.ndarray, errors_km: np.ndarray, threshold_km: float
) -> list[tuple[float, float]]:
    """Contiguous intervals where position error stays within a threshold.

    **Custody is about continuity, not average accuracy.** A track that is excellent for
    90% of a flight and lost during the manoeuvre has failed at exactly the moment that
    mattered, yet would show a respectable RMS. Reporting intervals rather than a mean
    keeps that visible.

    ``threshold_km`` is a **swept parameter**, not a qualification standard — see the
    module docstring.
    """
    t = np.atleast_1d(np.asarray(times_s, dtype=float))
    e = np.atleast_1d(np.asarray(errors_km, dtype=float))
    good = np.isfinite(e) & (e <= threshold_km)

    intervals: list[tuple[float, float]] = []
    start: float | None = None
    for i, ok in enumerate(good):
        if ok and start is None:
            start = float(t[i])
        elif not ok and start is not None:
            intervals.append((start, float(t[i - 1])))
            start = None
    if start is not None:
        intervals.append((start, float(t[-1])))
    return intervals


def assess(
    times_s: np.ndarray,
    estimated_km: np.ndarray,
    truth_km: np.ndarray,
    covariance_km2: np.ndarray,
    *,
    custody_threshold_km: float,
    state_dimension: int = 3,
) -> TrackQuality:
    """Full quality assessment of one track against truth."""
    errors = position_errors_km(estimated_km, truth_km)
    nees_vals = nees(estimated_km, truth_km, covariance_km2)

    p = np.asarray(covariance_km2, dtype=float)
    if p.ndim == 2:
        p = np.broadcast_to(p, (len(errors), *p.shape))
    # sqrt(trace(P)) is the RMS 3-D position uncertainty, which is the same quantity as
    # the RMS 3-D position error. The per-axis form sqrt(trace(P)/3) is a different
    # quantity by a factor of sqrt(3), and comparing the two would make every honest
    # filter score 0.577 and read as overconfident.
    reported = np.sqrt(np.trace(p, axis1=-2, axis2=-1))

    intervals = custody_intervals(times_s, errors, custody_threshold_km)
    total = float(times_s[-1] - times_s[0]) if len(times_s) > 1 else 0.0
    held = sum(b - a for a, b in intervals)

    return TrackQuality(
        rms_position_error_km=float(np.sqrt(np.mean(errors**2))),
        max_position_error_km=float(np.max(errors)),
        mean_reported_sigma_km=float(np.mean(reported)),
        nees_mean=float(np.mean(nees_vals[np.isfinite(nees_vals)]))
        if np.any(np.isfinite(nees_vals))
        else float("inf"),
        state_dimension=state_dimension,
        consistency=classify_consistency(nees_vals, state_dimension),
        custody_fraction=float(held / total) if total > 0 else 0.0,
        longest_custody_s=max((b - a for a, b in intervals), default=0.0),
        n_samples=len(errors),
    )


def gospa_cutoff_km(custody_threshold_km: float) -> float:
    """A defensible GOSPA/OSPA cutoff ``c`` derived from the custody threshold.

    ``c`` is not a free tuning knob: it sets what "completely wrong" costs, and therefore
    how a missed track trades against an inaccurate one. Quoting a number from a tutorial
    written at a different scale is meaningless — the value must follow from the problem.

    Tying it to the custody threshold makes the trade explicit: a track worse than the
    custody threshold is scored as no better than a miss, because operationally it is.
    """
    if custody_threshold_km <= 0:
        raise ValueError("custody threshold must be positive")
    return float(custody_threshold_km)
