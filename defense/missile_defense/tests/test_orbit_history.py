"""Tests for the multi-epoch orbit audit (D-14).

The synthetic tests pin the detector's behaviour independently of any downloaded data.
The catalogue tests pin the findings themselves, so that a re-identification of these
objects or a change in their flight profile fails loudly rather than quietly altering a
conclusion the proposal rests on.
"""

from __future__ import annotations

import numpy as np
import pytest

from mwsim import orbit_history as oh
from mwsim import registry


def _synthetic(
    *,
    days: int = 400,
    per_day: int = 2,
    start_sma: float = 7300.0,
    drift_km_per_year: float = 0.0,
    steps: dict[int, float] | None = None,
    noise_km: float = 0.0,
    seed: int = 20260923,
) -> oh.OrbitHistory:
    """Build an OrbitHistory with a known drift, known steps and known noise."""
    rng = np.random.default_rng(seed)
    n = days * per_day
    day_index = np.arange(n) / per_day
    sma = start_sma + drift_km_per_year * day_index / 365.25
    if steps:
        for day, delta in steps.items():
            sma[day_index >= day] += delta
    if noise_km:
        sma = sma + rng.normal(scale=noise_km, size=n)

    epochs = np.datetime64("2024-01-01T00:00:00", "s") + (
        (day_index * 86400).astype("int64").astype("timedelta64[s]")
    )
    zeros = np.zeros(n)
    return oh.OrbitHistory(
        norad_id=99999,
        epochs=epochs,
        semi_major_km=sma,
        apoapsis_km=sma - 6378.137,
        periapsis_km=sma - 6378.137,
        inclination_deg=zeros + 81.0,
        eccentricity=zeros,
        mean_motion=zeros + 14.0,
    )


class TestManeuverDetection:
    def test_quiet_orbit_reports_nothing(self) -> None:
        history = _synthetic(drift_km_per_year=-0.5, noise_km=0.01)
        assert oh.detect_maneuvers(history) == []
        assert oh.classify(history) in {"stable", "decaying"}

    def test_single_step_is_found_once(self) -> None:
        history = _synthetic(steps={200: -25.0}, noise_km=0.01)
        maneuvers = oh.detect_maneuvers(history)
        assert len(maneuvers) == 1, f"expected one manoeuvre, got {len(maneuvers)}"
        assert maneuvers[0].delta_km == pytest.approx(-25.0, abs=0.5)

    def test_realistic_element_noise_does_not_trigger(self) -> None:
        """Noise at the scale the real catalogue shows must not register.

        Measured on the control objects, consecutive-record scatter has sigma of roughly
        0.002 km. This test runs at 0.05 km -- about 25x worse than reality -- and still
        demands silence.
        """
        history = _synthetic(noise_km=0.05)
        assert oh.detect_maneuvers(history) == []

    def test_detector_breaks_down_when_noise_approaches_the_threshold(self) -> None:
        """Document the validity condition rather than pretend it does not exist.

        A median-of-3 comparison against a fixed threshold is only safe while per-record
        noise is far below that threshold. At sigma = threshold/2 the median's standard
        error is around a third of the threshold, so ordinary scatter clears it several
        times per hundred records and the detector fires on nothing.

        This is acceptable *for this data* because the real margin is a factor of several
        hundred, and `scripts/audit_orbit_history.py` reports the measured noise ceiling
        alongside the results so the margin is visible rather than assumed. Pinning the
        breakdown here means that if the detector is ever reused on noisier data, the
        assumption it depends on is already written down.
        """
        history = _synthetic(noise_km=oh.MANEUVER_THRESHOLD_KM / 2.0)
        assert oh.detect_maneuvers(history), (
            "expected the detector to break down at this noise level; if it no longer "
            "does, the method has changed and this test should be revisited"
        )

    def test_isolated_outlier_is_rejected(self) -> None:
        """One bad element fit that snaps back is not a manoeuvre."""
        history = _synthetic(noise_km=0.01)
        history.semi_major_km[300] += 40.0
        assert oh.detect_maneuvers(history) == []

    def test_maneuver_fraction_separates_thrust_from_drift(self) -> None:
        flown = _synthetic(steps={100: -30.0, 250: -30.0}, noise_km=0.01)
        assert oh.maneuver_fraction(flown) > 0.9

        drifting = _synthetic(drift_km_per_year=-20.0, noise_km=0.01)
        assert oh.maneuver_fraction(drifting) == 0.0


class TestDecayEstimate:
    def test_recovers_a_known_drift(self) -> None:
        history = _synthetic(drift_km_per_year=-3.0, noise_km=0.01)
        assert oh.decay_rate_km_per_year(history) == pytest.approx(-3.0, abs=0.1)

    def test_is_not_measurable_when_maneuvers_dominate(self) -> None:
        """The bug this guard exists for: clustered burns yielding a nonsense slope.

        Fitting scattered survivors between clustered steps once produced a *positive*
        drag rate for a satellite that had lost 325 km of altitude.
        """
        steps = {day: -20.0 for day in range(60, 380, 20)}
        history = _synthetic(steps=steps, noise_km=0.01)
        assert np.isnan(oh.decay_rate_km_per_year(history))

    def test_fits_only_a_contiguous_quiet_run(self) -> None:
        """With one burn, the fit must use one side, not straddle the step."""
        history = _synthetic(days=600, drift_km_per_year=-2.0, steps={300: -50.0}, noise_km=0.01)
        estimate = oh.decay_estimate(history)
        assert estimate.is_valid
        assert estimate.km_per_year == pytest.approx(-2.0, abs=0.3)
        # The window must not span the step at day 300.
        assert estimate.end_day < 300 or estimate.start_day > 300


# --------------------------------------------------------------------------------------
# Findings, pinned against the real cached histories.
# --------------------------------------------------------------------------------------

def _available(norad_id: int) -> bool:
    return (oh.HISTORY_CACHE / f"gp_history_{norad_id}.json").exists()


requires_history = pytest.mark.skipif(
    not _available(56171), reason="no cached history; run scripts/fetch_orbit_history.py"
)


@requires_history
class TestRealFindings:
    def test_all_were_inserted_near_the_published_altitude(self) -> None:
        """Finding 1: the premise of the retracted DEC-08 was false.

        Every one of these satellites began near 1000 km, consistent with SDA's published
        figure. The 'discrepancy' was an artefact of reading one current epoch.
        """
        for obj in registry.SDA_TRANCHE0_TRACKING + registry.HBTSS:
            if not _available(obj.norad_id):
                continue
            history = oh.load_history(obj.norad_id)
            insertion = (history.apoapsis_km[0] + history.periapsis_km[0]) / 2.0
            assert 900.0 < insertion < 1050.0, (
                f"{obj.name} was inserted at {insertion:.0f} km, outside the published band"
            )

    def test_drag_is_negligible_at_these_altitudes(self) -> None:
        """Finding 2: what makes finding 3 conclusive."""
        measured = []
        for obj in registry.SDA_TRANCHE0_TRACKING + registry.HBTSS:
            if not _available(obj.norad_id):
                continue
            estimate = oh.decay_estimate(oh.load_history(obj.norad_id))
            if estimate.is_valid:
                measured.append(estimate.km_per_year)
        assert measured, "no measurable quiet stretches at all"
        assert max(abs(v) for v in measured) < 5.0, (
            f"drag rates {measured} are too large to call negligible"
        )

    def test_the_moved_satellites_were_flown_not_abandoned(self) -> None:
        """Finding 3: steps account for essentially the whole change."""
        for norad_id in (56171, 56170, 57760, 57757, 58960):
            if not _available(norad_id):
                continue
            history = oh.load_history(norad_id)
            name = registry.by_id(norad_id).name
            assert abs(history.total_change_km()) > 100.0, f"{name} has not moved far"
            assert oh.maneuver_fraction(history) > 0.8, (
                f"{name}: steps explain only {oh.maneuver_fraction(history):.0%} of the change"
            )
            assert oh.classify(history) == "manoeuvred"

    def test_the_control_group_never_fires_the_detector(self) -> None:
        """Finding 4: the same detector on the same kind of data, silent.

        Without this, the detections above could be an artefact of the method.
        """
        for norad_id in (58959, 58955):
            if not _available(norad_id):
                continue
            history = oh.load_history(norad_id)
            name = registry.by_id(norad_id).name
            assert oh.detect_maneuvers(history) == [], f"{name} now shows manoeuvres"
            assert abs(history.total_change_km()) < 5.0
            assert oh.classify(history) == "stable"

    def test_noise_floor_justifies_the_threshold(self) -> None:
        """The control objects bound element-fit noise well below the threshold."""
        worst = 0.0
        for norad_id in (58959, 58955):
            if not _available(norad_id):
                continue
            history = oh.load_history(norad_id)
            worst = max(worst, float(np.abs(np.diff(history.semi_major_km)).max()))
        assert worst < oh.MANEUVER_THRESHOLD_KM, (
            f"noise reaches {worst:.3f} km, at or above the "
            f"{oh.MANEUVER_THRESHOLD_KM} km detection threshold"
        )
