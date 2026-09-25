"""Angles-only observability tests (task D-06)."""

from __future__ import annotations

import numpy as np
import pytest

from mwsim import observability as obs


class TestSingleSensor:
    def test_range_is_unobservable_from_one_bearing(self) -> None:
        """The defining property of a passive sensor, and the reason stereo exists."""
        r = obs.position_covariance(np.array([[0.0, 1500.0, 0.0]]), np.zeros(3), 50e-6)
        assert not r.observable
        assert np.isinf(r.rms_position_km)

    def test_two_colocated_sensors_are_still_unobservable(self) -> None:
        """Two sensors at the same place carry the information of one."""
        s = np.array([[0.0, 1500.0, 0.0], [0.0, 1500.0, 0.001]])
        assert not obs.position_covariance(s, np.zeros(3), 50e-6).observable


class TestDilution:
    def _pair(self, alpha_deg: float, rng: float = 1500.0) -> np.ndarray:
        half = np.radians(alpha_deg) / 2.0
        return np.vstack(
            [
                [rng * np.sin(half), rng * np.cos(half), 0.0],
                [-rng * np.sin(half), rng * np.cos(half), 0.0],
            ]
        )

    def test_error_follows_one_over_sine(self) -> None:
        """At small angles the 1/sin(alpha) law should hold closely."""
        rng, sigma = 1500.0, 50e-6
        e1 = obs.position_covariance(self._pair(1.0), np.zeros(3), sigma).rms_position_km
        e2 = obs.position_covariance(self._pair(2.0), np.zeros(3), sigma).rms_position_km
        assert e1 / e2 == pytest.approx(2.0, rel=0.02)

    def test_symmetric_about_ninety_degrees(self) -> None:
        """Convergence angle is what matters, not which side the sensors sit on."""
        sigma = 50e-6
        a = obs.position_covariance(self._pair(10.0), np.zeros(3), sigma).rms_position_km
        b = obs.position_covariance(self._pair(170.0), np.zeros(3), sigma).rms_position_km
        assert a == pytest.approx(b, rel=1e-6)

    def test_ninety_degrees_is_the_optimum(self) -> None:
        sigma = 50e-6
        best = obs.position_covariance(self._pair(90.0), np.zeros(3), sigma).rms_position_km
        for alpha in (20.0, 45.0, 135.0, 160.0):
            worse = obs.position_covariance(
                self._pair(alpha), np.zeros(3), sigma
            ).rms_position_km
            assert worse >= best

    def test_the_optimum_is_broad(self) -> None:
        """The practically important fact: useful stereo needs enough angle, not exact angle.

        45 degrees costs only ~34% over the 90-degree optimum, while 5 degrees costs an
        order of magnitude. The payoff is in escaping small angles.
        """
        sigma = 50e-6
        best = obs.position_covariance(self._pair(90.0), np.zeros(3), sigma).rms_position_km
        at45 = obs.position_covariance(self._pair(45.0), np.zeros(3), sigma).rms_position_km
        at5 = obs.position_covariance(self._pair(5.0), np.zeros(3), sigma).rms_position_km
        assert at45 / best < 1.5
        assert at5 / best > 8.0

    def test_error_scales_linearly_with_range_and_noise(self) -> None:
        base = obs.position_covariance(
            self._pair(90.0, 1500.0), np.zeros(3), 50e-6
        ).rms_position_km
        twice_range = obs.position_covariance(
            self._pair(90.0, 3000.0), np.zeros(3), 50e-6
        ).rms_position_km
        twice_noise = obs.position_covariance(
            self._pair(90.0, 1500.0), np.zeros(3), 100e-6
        ).rms_position_km
        assert twice_range / base == pytest.approx(2.0, rel=1e-6)
        assert twice_noise / base == pytest.approx(2.0, rel=1e-6)


class TestConvergenceAngle:
    def test_measures_the_angle_at_the_target(self) -> None:
        s = np.array([[1000.0, 0.0, 0.0], [0.0, 1000.0, 0.0]])
        assert obs.convergence_angle_deg(s, np.zeros(3)) == pytest.approx(90.0)

    def test_reports_the_widest_pair(self) -> None:
        s = np.array([[1000.0, 0.0, 0.0], [1000.0, 10.0, 0.0], [0.0, 1000.0, 0.0]])
        assert obs.convergence_angle_deg(s, np.zeros(3)) == pytest.approx(90.0, abs=1.0)

    def test_single_sensor_has_no_convergence(self) -> None:
        assert obs.convergence_angle_deg(np.array([[1000.0, 0.0, 0.0]]), np.zeros(3)) == 0.0


class TestRequiredConvergence:
    def test_tighter_accuracy_demands_wider_geometry(self) -> None:
        rng, sigma = 1500.0, 50e-6
        loose = obs.required_convergence_deg(rng, sigma, 1.0)
        tight = obs.required_convergence_deg(rng, sigma, 0.2)
        assert loose is not None and tight is not None
        assert tight > loose

    def test_unreachable_accuracy_returns_none(self) -> None:
        """No geometry beats the single-sensor cross-range limit R*sigma."""
        rng, sigma = 1500.0, 50e-6
        cross_range_limit = rng * sigma
        assert obs.required_convergence_deg(rng, sigma, cross_range_limit / 10.0) is None
