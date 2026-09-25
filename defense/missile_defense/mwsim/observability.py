"""Angles-only observability: what stereo geometry buys you (task D-06).

A passive infrared sensor measures direction, not range. One sensor therefore constrains a
target to a line and leaves range completely unobservable. Two or more sensors intersect
their lines and recover a three-dimensional position — but how *well* depends entirely on
the angle between them.

This module answers that quantitatively, because the alternative is the thing the plan
warns against: picking an arbitrary "stereo works above N degrees" threshold and hiding the
geometry behind it. There is no universal minimum convergence angle. There is a
relationship between convergence angle, angular noise, range and the resulting position
covariance, and the right move is to expose it and sweep.

Method: each bearing measurement constrains the two directions perpendicular to its line of
sight, each with standard deviation ``R·σ_θ``. Stacking those constraints gives a Fisher
information matrix

    J = Σᵢ (1 / (Rᵢ σ_θ)²) · (I − uᵢ uᵢᵀ)

whose inverse is the position covariance. The ``(I − u uᵀ)`` projector is what encodes
"this sensor tells you nothing about range along its own line of sight" — with one sensor
J is singular in that direction, which is the formal statement that range is unobservable.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ObservabilityResult:
    """Position uncertainty from intersecting angles-only measurements."""

    covariance_km2: np.ndarray     # (3, 3)
    semi_axes_km: np.ndarray       # (3,) 1-sigma error ellipsoid semi-axes, descending
    rms_position_km: float
    condition_number: float
    observable: bool

    @property
    def worst_axis_km(self) -> float:
        """The long axis of the error ellipsoid — the direction range is least constrained."""
        return float(self.semi_axes_km[0])

    @property
    def best_axis_km(self) -> float:
        return float(self.semi_axes_km[-1])

    @property
    def gdop(self) -> float:
        """Geometric dilution: how much worse than the best-constrained direction."""
        best = self.best_axis_km
        return float(self.worst_axis_km / best) if best > 0 else float("inf")


def position_covariance(
    sensor_positions_km: np.ndarray,
    target_position_km: np.ndarray,
    angular_sigma_rad: float,
    *,
    condition_limit: float = 1e12,
) -> ObservabilityResult:
    """Position covariance from angles-only measurements by one or more sensors.

    ``sensor_positions_km`` is ``(n_sensor, 3)``. A single sensor produces a singular
    information matrix — range is unobservable — and is reported with ``observable=False``
    rather than being silently pseudo-inverted into a finite-looking answer.
    """
    sensors = np.atleast_2d(np.asarray(sensor_positions_km, dtype=float))
    target = np.asarray(target_position_km, dtype=float).reshape(3)

    if angular_sigma_rad <= 0:
        raise ValueError("angular_sigma_rad must be positive")

    information = np.zeros((3, 3))
    for sensor in sensors:
        delta = target - sensor
        rng = float(np.linalg.norm(delta))
        if rng <= 0:
            continue
        u = delta / rng
        cross_range_sigma = rng * angular_sigma_rad
        # (I - u u^T) keeps only the two directions this sensor actually constrains.
        information += (np.eye(3) - np.outer(u, u)) / cross_range_sigma**2

    eigenvalues = np.linalg.eigvalsh(information)
    smallest = float(np.min(eigenvalues))
    largest = float(np.max(eigenvalues))
    condition = largest / smallest if smallest > 0 else float("inf")

    if smallest <= 0 or condition > condition_limit:
        return ObservabilityResult(
            covariance_km2=np.full((3, 3), np.inf),
            semi_axes_km=np.array([np.inf, np.inf, np.inf]),
            rms_position_km=float("inf"),
            condition_number=condition,
            observable=False,
        )

    covariance = np.linalg.inv(information)
    variances = np.sort(np.linalg.eigvalsh(covariance))[::-1]
    semi_axes = np.sqrt(np.clip(variances, 0.0, None))
    return ObservabilityResult(
        covariance_km2=covariance,
        semi_axes_km=semi_axes,
        rms_position_km=float(np.sqrt(np.trace(covariance))),
        condition_number=condition,
        observable=True,
    )


def convergence_angle_deg(
    sensor_positions_km: np.ndarray, target_position_km: np.ndarray
) -> float:
    """Largest angle subtended at the target by any pair of sensors, degrees.

    The *largest* pair angle is what governs the best achievable geometry: a third sensor
    nearly co-located with a second adds little, while one well separated transforms the
    solution.
    """
    sensors = np.atleast_2d(np.asarray(sensor_positions_km, dtype=float))
    target = np.asarray(target_position_km, dtype=float).reshape(3)
    if len(sensors) < 2:
        return 0.0

    directions = []
    for sensor in sensors:
        d = sensor - target
        n = np.linalg.norm(d)
        if n > 0:
            directions.append(d / n)

    best = 0.0
    for i in range(len(directions)):
        for j in range(i + 1, len(directions)):
            cross = float(np.linalg.norm(np.cross(directions[i], directions[j])))
            dot = float(np.dot(directions[i], directions[j]))
            best = max(best, float(np.degrees(np.arctan2(cross, dot))))
    return best


def required_convergence_deg(
    range_km: float,
    angular_sigma_rad: float,
    target_accuracy_km: float,
    *,
    samples: int = 2000,
) -> float | None:
    """Smallest convergence angle meeting a position-accuracy requirement, degrees.

    This is the function the coverage metric should call. It replaces an arbitrary
    "stereo counts above N degrees" rule with the honest question: *given this angular
    noise and this range, how much separation do I need to hit the accuracy I care about?*

    Returns ``None`` when the requirement is unreachable at any angle — which happens
    whenever the cross-range error ``R·σ_θ`` alone already exceeds the target, since no
    geometry improves on the single-sensor cross-range limit.
    """
    # Two sensors equidistant from the target, symmetric about it, in a plane.
    for alpha_deg in np.linspace(0.5, 180.0, samples):
        half = np.radians(alpha_deg) / 2.0
        target = np.zeros(3)
        s1 = np.array([range_km * np.sin(half), range_km * np.cos(half), 0.0])
        s2 = np.array([-range_km * np.sin(half), range_km * np.cos(half), 0.0])
        result = position_covariance(np.vstack([s1, s2]), target, angular_sigma_rad)
        if result.observable and result.rms_position_km <= target_accuracy_km:
            return float(alpha_deg)
    return None


def dilution_curve(
    range_km: float,
    angular_sigma_rad: float,
    angles_deg: np.ndarray,
) -> np.ndarray:
    """RMS position error against convergence angle, km.

    Shows the 1/sin(α) blow-up as the geometry degenerates, and the broad, flat optimum
    near 90° — the practically important fact being that useful stereo does not require
    precise geometry, only enough of it.
    """
    out = np.empty(len(angles_deg))
    for i, alpha in enumerate(angles_deg):
        half = np.radians(alpha) / 2.0
        s1 = np.array([range_km * np.sin(half), range_km * np.cos(half), 0.0])
        s2 = np.array([-range_km * np.sin(half), range_km * np.cos(half), 0.0])
        r = position_covariance(np.vstack([s1, s2]), np.zeros(3), angular_sigma_rad)
        out[i] = r.rms_position_km if r.observable else np.inf
    return out
