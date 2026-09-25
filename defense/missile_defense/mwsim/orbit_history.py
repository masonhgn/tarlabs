"""Multi-epoch orbit audit: telling commanded manoeuvres apart from secular decay (D-14).

This module exists because of a mistake. Working from a single element epoch, we inferred
that the Tranche 0 "BB" satellites were decaying, and from that inferred things about their
mission status. A single fitted drag derivative cannot support either conclusion. The fix
is to use the whole `gp_history` series and separate two physically different things:

*   **Secular decay** — a smooth, monotonic contraction of the semi-major axis, driven by
    drag, whose rate grows as altitude falls. At ~950 km it is extremely slow: decades.
*   **A commanded manoeuvre** — a step change in semi-major axis over one or two element
    sets, far faster than drag could produce at that altitude.

The distinction matters for the study because it decides whether the current geometry is
where an operator *put* these satellites or where physics *left* them, and it decides
whether we may describe them as operational at all. We still never label a manoeuvre as
"disposal" without an agency source: the data shows what happened, not why.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

_DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
HISTORY_CACHE = _DATA_ROOT / "raw" / "spacetrack"

#: Earth's gravitational parameter, km^3/s^2 (WGS-84).
MU_EARTH = 398600.4418

#: A semi-major-axis step larger than this between consecutive element sets is treated as
#: a manoeuvre candidate. Drag at these altitudes produces far less than this per day;
#: the threshold's job is to sit above element-fit noise, not to be physically derived.
#:
#: **Validity condition.** A median-of-N comparison against a fixed threshold is only
#: sound while per-record noise is far below that threshold: the median of N samples has
#: a standard error around sigma/sqrt(N), so at sigma near the threshold ordinary scatter
#: clears it routinely and the detector fires on nothing. For this data the margin is
#: comfortable -- measured consecutive-record scatter on objects that never manoeuvred is
#: about 0.002 km, roughly 500x below the threshold -- and
#: `scripts/audit_orbit_history.py` reports that measured ceiling alongside the results so
#: the margin is visible rather than assumed. Reusing this detector on noisier element
#: sets would require scaling the threshold to a local noise estimate instead.
MANEUVER_THRESHOLD_KM = 1.0

#: Element sets are noisy. Require the step to persist, so a single bad fit followed by a
#: correction back to the trend is not counted as a manoeuvre.
PERSISTENCE_RECORDS = 3


@dataclass(frozen=True)
class OrbitHistory:
    """One object's element-set time series, as numpy arrays on a common index."""

    norad_id: int
    epochs: np.ndarray          # datetime64[s]
    semi_major_km: np.ndarray
    apoapsis_km: np.ndarray     # altitude above the reference sphere, as Space-Track gives it
    periapsis_km: np.ndarray
    inclination_deg: np.ndarray
    eccentricity: np.ndarray
    mean_motion: np.ndarray

    @property
    def n(self) -> int:
        return len(self.epochs)

    @property
    def span_days(self) -> float:
        if self.n < 2:
            return 0.0
        delta = self.epochs[-1] - self.epochs[0]
        return float(delta / np.timedelta64(1, "D"))

    def total_change_km(self) -> float:
        """Net change in semi-major axis across the whole record."""
        return float(self.semi_major_km[-1] - self.semi_major_km[0])


@dataclass(frozen=True)
class Maneuver:
    """A detected step change in semi-major axis."""

    epoch: np.datetime64
    delta_km: float
    semi_major_before_km: float
    semi_major_after_km: float


def load_history(norad_id: int, cache_dir: Path = HISTORY_CACHE) -> OrbitHistory:
    """Read one cached `gp_history` pull into arrays, sorted by epoch.

    Records missing the fields we need are dropped rather than zero-filled: a zero
    semi-major axis would look exactly like a catastrophic manoeuvre.
    """
    path = cache_dir / f"gp_history_{norad_id}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"no cached history for NORAD {norad_id}; run scripts/fetch_orbit_history.py"
        )
    payload = json.loads(path.read_text(encoding="utf-8"))

    rows = []
    for record in payload["records"]:
        try:
            epoch = np.datetime64(record["EPOCH"][:19], "s")
            sma = float(record["SEMIMAJOR_AXIS"])
            apo = float(record["APOAPSIS"])
            peri = float(record["PERIAPSIS"])
            inc = float(record["INCLINATION"])
            ecc = float(record["ECCENTRICITY"])
            mm = float(record["MEAN_MOTION"])
        except (KeyError, TypeError, ValueError):
            continue
        if sma <= 0.0:
            continue
        rows.append((epoch, sma, apo, peri, inc, ecc, mm))

    if not rows:
        raise ValueError(f"no usable records for NORAD {norad_id}")

    rows.sort(key=lambda r: r[0])
    cols = list(zip(*rows))
    return OrbitHistory(
        norad_id=norad_id,
        epochs=np.array(cols[0]),
        semi_major_km=np.array(cols[1], dtype=float),
        apoapsis_km=np.array(cols[2], dtype=float),
        periapsis_km=np.array(cols[3], dtype=float),
        inclination_deg=np.array(cols[4], dtype=float),
        eccentricity=np.array(cols[5], dtype=float),
        mean_motion=np.array(cols[6], dtype=float),
    )


def detect_maneuvers(
    history: OrbitHistory,
    *,
    threshold_km: float = MANEUVER_THRESHOLD_KM,
    persistence: int = PERSISTENCE_RECORDS,
) -> list[Maneuver]:
    """Find persistent step changes in semi-major axis.

    A step counts only if the median semi-major axis over the next ``persistence``
    records stays displaced by at least ``threshold_km`` from the median over the previous
    ``persistence``. That rejects isolated bad element fits, which are common, without
    needing to smooth the series and blur the real steps.
    """
    sma = history.semi_major_km
    n = len(sma)
    if n < 2 * persistence + 1:
        return []

    maneuvers: list[Maneuver] = []
    i = persistence
    while i < n - persistence:
        before = float(np.median(sma[i - persistence : i]))
        after = float(np.median(sma[i : i + persistence]))
        delta = after - before
        if abs(delta) >= threshold_km:
            maneuvers.append(
                Maneuver(
                    epoch=history.epochs[i],
                    delta_km=delta,
                    semi_major_before_km=before,
                    semi_major_after_km=after,
                )
            )
            # Skip past this event so one manoeuvre is reported once, not once per record
            # while the step is inside the comparison window.
            i += persistence
        else:
            i += 1
    return maneuvers


#: A quiet-period drag fit needs enough of the record to be quiet. Below this fraction the
#: surviving samples are short disconnected islands between burns, and a straight line
#: through them describes nothing physical.
MIN_QUIET_FRACTION = 0.5


#: A drag fit needs a quiet stretch of at least this long to mean anything.
MIN_QUIET_SEGMENT_DAYS = 60.0


@dataclass(frozen=True)
class DecayEstimate:
    """A drag-rate estimate together with the interval it was actually measured over."""

    km_per_year: float
    start_day: float
    end_day: float
    n_samples: int

    @property
    def span_days(self) -> float:
        return self.end_day - self.start_day

    @property
    def is_valid(self) -> bool:
        return not np.isnan(self.km_per_year)


def longest_quiet_segment(history: OrbitHistory) -> tuple[int, int] | None:
    """Index bounds of the longest *contiguous* run free of manoeuvres.

    Contiguity is the whole point. Masking samples near each burn and fitting whatever
    survives sounds reasonable and is badly wrong when the burns are clustered: the
    survivors then come from two different regimes -- a quiet pre-manoeuvre era and narrow
    gaps between later burns -- and a straight line through both measures the gap between
    the regimes, not drag. That failure produced a *positive* drag rate for a satellite
    that had lost 325 km.
    """
    if history.n < 3:
        return None

    quiet = np.ones(history.n, dtype=bool)
    for maneuver in detect_maneuvers(history):
        quiet &= np.abs(history.epochs - maneuver.epoch) >= np.timedelta64(14, "D")

    best: tuple[int, int] | None = None
    best_len = 0
    start: int | None = None
    for i in range(history.n + 1):
        if i < history.n and quiet[i]:
            if start is None:
                start = i
        elif start is not None:
            if i - start > best_len:
                best_len = i - start
                best = (start, i)
            start = None
    return best


def decay_rate_km_per_year(history: OrbitHistory) -> float:
    """Drag-driven trend in semi-major axis, km/year, or NaN if it cannot be measured.

    Fitted over the longest contiguous manoeuvre-free stretch. Returns NaN when no such
    stretch is long enough, which is the correct answer for a satellite that was under
    powered flight for most of its record: a number there would read as a measurement.
    """
    return decay_estimate(history).km_per_year


def decay_estimate(history: OrbitHistory) -> DecayEstimate:
    """``decay_rate_km_per_year`` plus the interval used, for reporting."""
    nan = DecayEstimate(float("nan"), float("nan"), float("nan"), 0)
    segment = longest_quiet_segment(history)
    if segment is None:
        return nan

    lo, hi = segment
    days = ((history.epochs - history.epochs[0]) / np.timedelta64(1, "D")).astype(float)
    span = days[hi - 1] - days[lo]
    if hi - lo < 3 or span < MIN_QUIET_SEGMENT_DAYS:
        return nan

    slope, _ = np.polyfit(days[lo:hi], history.semi_major_km[lo:hi], 1)
    return DecayEstimate(float(slope * 365.25), float(days[lo]), float(days[hi - 1]), hi - lo)


def maneuver_fraction(history: OrbitHistory) -> float:
    """Share of the net semi-major-axis change attributable to detected steps.

    Near 1.0 the orbit was flown; near 0.0 it was left alone. This is the quantity that
    actually separates the two populations, and it degrades gracefully where a single
    verdict word would have to pick a side.
    """
    net = abs(history.total_change_km())
    if net < 1e-6:
        return 0.0
    stepped = sum(abs(m.delta_km) for m in detect_maneuvers(history))
    return float(stepped / net)


def classify(history: OrbitHistory) -> str:
    """A one-word verdict on what moved this orbit. Deliberately descriptive.

    Returns 'manoeuvred', 'decaying', 'stable' or 'mixed'. It describes the *orbit*, never
    the mission: this function does not and cannot say whether a satellite is operational,
    retired or being disposed of.
    """
    maneuvers = detect_maneuvers(history)
    drift = decay_rate_km_per_year(history)
    total = history.total_change_km()

    significant = abs(total) > 5.0
    if maneuvers and significant:
        maneuvered_km = sum(abs(m.delta_km) for m in maneuvers)
        # If steps account for most of the net change, thrust dominates drag.
        return "manoeuvred" if maneuvered_km > 0.5 * abs(total) else "mixed"
    if maneuvers:
        return "manoeuvred"
    if significant and drift < -1.0:
        return "decaying"
    return "stable"
