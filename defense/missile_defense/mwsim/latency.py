"""Warn-to-decision latency: what is physics, what is published, what is swept (task D-20).

This is the axis the whole study turns on. CSIS already published a thorough multi-orbit
*coverage* trade (DEC-26); what they did not address is where processing happens and what
that costs in time. So the latency model has to be more careful than the rest, because it
is the part carrying the novelty claim.

## The finding that shapes everything here

Propagation delay is **not** the driver, and it is not close.

| Path | One-way light time |
|---|---|
| LEO (1,000 km) nadir downlink | 3.3 ms |
| LEO max-slant downlink | 12.4 ms |
| LEO–LEO crosslink, horizon-limited | 24.7 ms |
| MEO (10,000 km) nadir | 33.4 ms |
| GEO nadir | 119.4 ms |

Even a pessimistic multi-hop LEO mesh into a GEO relay totals a few hundred milliseconds.
Published detect-to-alert figures are **tens of seconds**. Propagation is therefore under
1% of the timeline.

**This changes the edge-fusion argument.** Moving fusion on-orbit cannot help by saving
propagation time — there is almost none to save. If it helps, it helps by removing
*serialisation*: not having to downlink, queue behind other traffic, process centrally, and
redistribute. That is a claim about pipeline structure and contention, not about distance.

Stating it the other way round — "closer sensors mean lower latency" — would be the
intuitive pitch and would be wrong by two orders of magnitude. A reviewer who checks the
light-time would notice.

## What this module does and does not assert

* **Propagation is computed exactly** from geometry and the speed of light. No assumption.
* **Processing, queueing, and decision times are distributions**, swept, with no claimed
  public value. Real figures are not published (D-20 open items).
* **Published end-to-end figures are priors for sanity-checking**, never validation truth.
  The ~30 s legacy detect-to-alert figure traces to an analytical discussion, not a
  performance specification.

Results are reported as *relative* comparisons between architectures under identical
assumptions, which is the only defensible form given the above.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

#: Speed of light, km/s.
C_KM_S = 299792.458
#: Earth mean equatorial radius, km.
RE_KM = 6378.137


def propagation_delay_s(range_km: float | np.ndarray) -> np.ndarray:
    """Light-time over a slant range, seconds. Exact."""
    return np.asarray(range_km, dtype=float) / C_KM_S


def max_slant_range_km(altitude_km: float) -> float:
    """Horizon-limited slant range from a satellite to the ground, km."""
    r = RE_KM + altitude_km
    return float(np.sqrt(r**2 - RE_KM**2))


def max_crosslink_range_km(altitude_km: float) -> float:
    """Longest same-altitude inter-satellite link that clears the Earth, km."""
    r = RE_KM + altitude_km
    return float(2.0 * np.sqrt(r**2 - RE_KM**2))


@dataclass(frozen=True)
class Stage:
    """One stage of the warn-to-decision pipeline.

    ``physics`` marks stages computed from geometry rather than assumed. Only propagation
    qualifies; everything else is a swept distribution, and the distinction is carried in
    the data structure so a report cannot accidentally present an assumption as a
    measurement.
    """

    name: str
    mean_s: float
    sigma_s: float = 0.0
    physics: bool = False
    note: str = ""

    def sample(self, rng: np.random.Generator, size: int) -> np.ndarray:
        if self.sigma_s <= 0:
            return np.full(size, self.mean_s)
        # Lognormal: delays are positive and right-skewed (queues have tails, and nothing
        # arrives before it was sent). A Gaussian would generate negative latencies.
        mu = np.log(self.mean_s**2 / np.sqrt(self.mean_s**2 + self.sigma_s**2))
        sd = np.sqrt(np.log(1.0 + (self.sigma_s / self.mean_s) ** 2))
        return rng.lognormal(mu, sd, size)


@dataclass
class LatencyBudget:
    """An additive warn-to-decision budget, sampled as distributions."""

    stages: list[Stage] = field(default_factory=list)

    def add(self, stage: Stage) -> "LatencyBudget":
        self.stages.append(stage)
        return self

    def total_mean_s(self) -> float:
        return float(sum(s.mean_s for s in self.stages))

    def physics_fraction(self) -> float:
        """Share of the mean budget that is computed rather than assumed.

        The honest headline number for any latency claim: if this is small, the result is
        mostly a statement about our assumptions, and should be reported that way.
        """
        total = self.total_mean_s()
        if total <= 0:
            return 0.0
        return float(sum(s.mean_s for s in self.stages if s.physics) / total)

    def sample(self, n: int = 10000, seed: int = 0) -> np.ndarray:
        rng = np.random.default_rng(seed)
        return np.sum([s.sample(rng, n) for s in self.stages], axis=0)

    def percentiles(self, q=(50, 90, 99), n: int = 10000, seed: int = 0) -> dict[int, float]:
        draws = self.sample(n, seed)
        return {int(p): float(np.percentile(draws, p)) for p in q}

    def breakdown(self) -> list[tuple[str, float, float, bool]]:
        """(name, mean, share of total, is_physics), largest first."""
        total = self.total_mean_s()
        rows = [
            (s.name, s.mean_s, s.mean_s / total if total > 0 else 0.0, s.physics)
            for s in self.stages
        ]
        return sorted(rows, key=lambda r: -r[1])


def ground_centralised_budget(
    *,
    sensor_altitude_km: float = 1000.0,
    onboard_processing_s: float = 1.0,
    onboard_sigma_s: float = 0.5,
    ground_processing_s: float = 5.0,
    ground_sigma_s: float = 3.0,
    dissemination_s: float = 2.0,
    dissemination_sigma_s: float = 1.0,
    decision_s: float = 10.0,
    decision_sigma_s: float = 5.0,
) -> LatencyBudget:
    """Detection downlinked to a central ground node, fused there, result disseminated.

    Every non-propagation default is a **placeholder to be swept**, not a sourced value.
    """
    downlink = max_slant_range_km(sensor_altitude_km)
    return (
        LatencyBudget()
        .add(Stage("onboard detection/formatting", onboard_processing_s, onboard_sigma_s))
        .add(
            Stage(
                "downlink propagation",
                float(propagation_delay_s(downlink)),
                physics=True,
                note=f"max slant {downlink:.0f} km at {sensor_altitude_km:.0f} km altitude",
            )
        )
        .add(Stage("ground fusion/processing", ground_processing_s, ground_sigma_s))
        .add(Stage("dissemination", dissemination_s, dissemination_sigma_s))
        .add(Stage("decision", decision_s, decision_sigma_s))
    )


def edge_fused_budget(
    *,
    sensor_altitude_km: float = 1000.0,
    crosslink_hops: int = 2,
    onboard_processing_s: float = 1.0,
    onboard_sigma_s: float = 0.5,
    onboard_fusion_s: float = 2.0,
    onboard_fusion_sigma_s: float = 1.0,
    dissemination_s: float = 2.0,
    dissemination_sigma_s: float = 1.0,
    decision_s: float = 10.0,
    decision_sigma_s: float = 5.0,
) -> LatencyBudget:
    """Detections crosslinked between satellites, fused on orbit, result sent down.

    The crosslink hops add propagation but remove the central ground stage. Since
    propagation is milliseconds and the ground stage is seconds, **the comparison is
    decided almost entirely by the processing terms** — which is precisely why they must
    be swept rather than assumed.
    """
    crosslink = max_crosslink_range_km(sensor_altitude_km)
    downlink = max_slant_range_km(sensor_altitude_km)
    budget = (
        LatencyBudget()
        .add(Stage("onboard detection/formatting", onboard_processing_s, onboard_sigma_s))
        .add(
            Stage(
                f"crosslink propagation ({crosslink_hops} hops)",
                float(propagation_delay_s(crosslink) * crosslink_hops),
                physics=True,
                note=f"{crosslink:.0f} km per hop",
            )
        )
        .add(Stage("on-orbit fusion", onboard_fusion_s, onboard_fusion_sigma_s))
        .add(
            Stage(
                "downlink propagation",
                float(propagation_delay_s(downlink)),
                physics=True,
            )
        )
        .add(Stage("dissemination", dissemination_s, dissemination_sigma_s))
        .add(Stage("decision", decision_s, decision_sigma_s))
    )
    return budget


def edge_advantage_s(
    *,
    ground_fusion_s: float,
    onboard_fusion_s: float,
    sensor_altitude_km: float = 1000.0,
    crosslink_hops: int = 2,
) -> float:
    """Seconds saved by fusing on orbit instead of on the ground. Negative means worse.

    Edge fusion trades a ground-processing stage for crosslink propagation plus on-orbit
    processing:

        advantage = (downlink + ground_fusion) − (crosslinks + onboard_fusion)

    Because propagation is milliseconds and processing is seconds, this collapses to
    ``ground_fusion − onboard_fusion`` to within a few tens of milliseconds.
    """
    crosslink = propagation_delay_s(max_crosslink_range_km(sensor_altitude_km)) * crosslink_hops
    downlink = propagation_delay_s(max_slant_range_km(sensor_altitude_km))
    return float((downlink + ground_fusion_s) - (crosslink + onboard_fusion_s))


def breakeven_onboard_fusion_s(
    ground_fusion_s: float,
    *,
    sensor_altitude_km: float = 1000.0,
    crosslink_hops: int = 2,
) -> float:
    """On-orbit fusion time at which edge and ground placements tie, seconds.

    **This is the study's actual question, and it is not a geometry question.**

    Propagation contributes under 1% of the warn-to-decision budget, so moving fusion
    on-orbit cannot win by shortening the path. It wins only if on-orbit processing is
    genuinely faster than the ground pipeline it replaces — which is a claim about compute,
    contention and serialisation under spacecraft size, weight and power limits, not about
    distance.

    Reporting this breakeven, rather than a headline "edge fusion saves N seconds", is the
    defensible form: it states the condition under which the architecture wins and leaves
    the reader to judge whether that condition is achievable.
    """
    crosslink = propagation_delay_s(max_crosslink_range_km(sensor_altitude_km)) * crosslink_hops
    downlink = propagation_delay_s(max_slant_range_km(sensor_altitude_km))
    return float(ground_fusion_s + downlink - crosslink)


#: Published end-to-end figures. **Priors for sanity-checking, not validation truth.**
PUBLISHED_PRIORS = {
    "legacy_detect_to_alert_s": {
        "value": 30.0,
        "status": "REPORTED",
        "source": "INSS analytical discussion, 2025 — not a performance specification",
    },
    "older_ignition_to_alert_s": {
        "value": 65.0,
        "status": "REPORTED",
        "source": "older public analysis; ~60-70 s including ~30 s after initial detection",
    },
    "detect_and_characterise_s": {
        "value": 60.0,
        "status": "UNVERIFIED",
        "source": "attributed to a National Academies boost-phase report; the exact page "
        "was not recovered — do not quote until located",
    },
}
