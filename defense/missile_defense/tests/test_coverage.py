"""Access geometry and stereo coverage (task S-05, DEC-24)."""

from __future__ import annotations

import numpy as np
import pytest

from mwsim import constellation as con
from mwsim import coverage as cov
from mwsim import observability as obs

RE = cov.RE_KM
TARGET = np.array([RE + 45.0, 0.0, 0.0])


class TestAccess:
    def test_satellite_overhead_sees_the_target(self) -> None:
        sat = np.array([[RE + 1000.0, 0.0, 0.0]])
        r = cov.access(sat, TARGET)
        assert r.n_visible == 1
        assert r.off_nadir_deg[0] == pytest.approx(0.0, abs=1e-6)
        assert r.target_zenith_deg[0] == pytest.approx(0.0, abs=1e-6)
        assert r.slant_range_km[0] == pytest.approx(955.0, abs=1.0)

    def test_satellite_on_the_far_side_cannot(self) -> None:
        sat = np.array([[-(RE + 1000.0), 0.0, 0.0]])
        assert cov.access(sat, TARGET).n_visible == 0

    def test_field_of_regard_gates_access(self) -> None:
        """A satellite well off to the side is visible only with a wide enough sensor."""
        ang = np.radians(35.0)
        sat = np.array([[(RE + 1000.0) * np.cos(ang), (RE + 1000.0) * np.sin(ang), 0.0]])
        assert cov.access(sat, TARGET, field_of_regard_deg=40.0).n_visible == 0
        assert cov.access(sat, TARGET, field_of_regard_deg=160.0).n_visible == 1

    def test_off_nadir_is_smaller_than_target_zenith(self) -> None:
        """Geometry: the satellite is further out, so the angle is amplified at the target."""
        ang = np.radians(20.0)
        sat = np.array([[(RE + 1000.0) * np.cos(ang), (RE + 1000.0) * np.sin(ang), 0.0]])
        r = cov.access(sat, TARGET, field_of_regard_deg=180.0)
        assert r.target_zenith_deg[0] > r.off_nadir_deg[0]


class TestUsefulStereo:
    """DEC-24: score stereo by achieved convergence, not by sensor count."""

    def _pair(self, convergence_deg: float, slant_km: float = 1500.0) -> np.ndarray:
        """Two sensors placed to subtend a specified convergence angle *at the target*.

        Parametrising by geocentric angle instead is a trap: at 30 degrees geocentric the
        satellites sit near the target's horizon in opposite directions, giving 179
        degrees of convergence rather than 30.
        """
        half = np.radians(convergence_deg / 2.0)
        up = np.array([1.0, 0.0, 0.0])      # local vertical at TARGET
        east = np.array([0.0, 1.0, 0.0])
        return np.array([
            TARGET + slant_km * (np.cos(half) * up + np.sin(half) * east),
            TARGET + slant_km * (np.cos(half) * up - np.sin(half) * east),
        ])

    def test_two_sensors_is_not_automatically_useful(self) -> None:
        """The whole point of the decision: counting sensors overstates coverage."""
        r = cov.access(self._pair(4.0), TARGET, field_of_regard_deg=180.0)
        assert r.has_stereo          # two are in view
        assert not cov.useful_stereo(
            r, angular_sigma_rad=50e-6, required_accuracy_km=0.5
        )                            # but the geometry cannot deliver

    def test_adequate_separation_passes(self) -> None:
        r = cov.access(self._pair(60.0), TARGET, field_of_regard_deg=180.0)
        assert cov.useful_stereo(r, angular_sigma_rad=50e-6, required_accuracy_km=1.0)

    def test_the_adequate_band_is_symmetric_about_90_degrees(self) -> None:
        """The bug this test exists for.

        Position error scales as 1/sin(alpha), so 150 degrees is exactly as good as 30 and
        175 is exactly as bad as 5. A one-sided test (`convergence >= needed`) silently
        accepts near-antiparallel geometries where the sight lines are almost collinear
        again. On a 135-satellite constellation that overstated useful coverage by 26
        percentage points at a 0.5 km requirement.
        """
        rng, sigma = 1500.0, 50e-6
        needed = obs.required_convergence_deg(rng, sigma, 0.5)
        assert needed is not None
        lo = obs.dilution_curve(rng, sigma, np.array([needed]))[0]
        hi = obs.dilution_curve(rng, sigma, np.array([180.0 - needed]))[0]
        assert lo == pytest.approx(hi, rel=1e-6), "the curve must be symmetric about 90 deg"

        just_past = obs.dilution_curve(rng, sigma, np.array([180.0 - needed + 5.0]))[0]
        assert just_past > lo, "beyond the upper edge the geometry must be worse"

    def test_single_sensor_is_never_useful(self) -> None:
        sat = np.array([[RE + 1000.0, 0.0, 0.0]])
        r = cov.access(sat, TARGET)
        assert not cov.useful_stereo(r, angular_sigma_rad=50e-6, required_accuracy_km=10.0)

    def test_unreachable_accuracy_is_never_useful(self) -> None:
        """No geometry beats the single-sensor cross-range limit R*sigma."""
        r = cov.access(self._pair(90.0), TARGET, field_of_regard_deg=180.0)
        assert not cov.useful_stereo(
            r, angular_sigma_rad=50e-6, required_accuracy_km=1e-4
        )


class TestFieldOfRegardLimit:
    def test_reproduces_the_csis_curvature_limit(self) -> None:
        assert cov.max_field_of_regard_deg(1000.0, 45.0) == pytest.approx(121.0, abs=1.5)


class TestConstellationCoverage:
    """Independent reproduction of the CSIS field-of-regard finding (D-09)."""

    @pytest.fixture(scope="class")
    def positions(self):
        c = con.csis_architecture("csis_91_leo")
        return con.propagate_kepler(c, np.linspace(0, 6 * 3600, 180))

    def test_120_degrees_works_where_110_and_100_fail(self, positions) -> None:
        """CSIS: a 91-satellite constellation gives persistent global stereo at 120 deg
        field of regard and fails at 110 or 100. Reproduced from our own geometry.
        """
        frac = {}
        for forr in (100.0, 110.0, 120.0):
            r = cov.coverage_over_time(
                positions, TARGET, field_of_regard_deg=forr, required_accuracy_km=1.0
            )
            frac[forr] = r["naive_stereo_fraction"]
        assert frac[100.0] < 0.05, f"100 deg gave {frac[100.0]:.1%} stereo"
        assert frac[110.0] < 0.35, f"110 deg gave {frac[110.0]:.1%} stereo"
        assert frac[120.0] > 0.6, f"120 deg gave only {frac[120.0]:.1%} stereo"
        assert frac[120.0] > frac[110.0] > frac[100.0]

    def test_more_satellites_give_more_coverage(self) -> None:
        t = np.linspace(0, 6 * 3600, 120)
        small = con.propagate_kepler(con.csis_architecture("csis_91_leo"), t)
        large = con.propagate_kepler(con.csis_architecture("csis_135_leo"), t)
        a = cov.coverage_over_time(small, TARGET, field_of_regard_deg=120.0)
        b = cov.coverage_over_time(large, TARGET, field_of_regard_deg=120.0)
        assert b["mean_visible"] > a["mean_visible"]

    def test_tighter_accuracy_shrinks_useful_coverage(self, positions) -> None:
        """Naive and useful coverage must diverge as the requirement tightens."""
        loose = cov.coverage_over_time(
            positions, TARGET, field_of_regard_deg=120.0, required_accuracy_km=2.0
        )
        tight = cov.coverage_over_time(
            positions, TARGET, field_of_regard_deg=120.0, required_accuracy_km=0.1
        )
        assert loose["naive_stereo_fraction"] == tight["naive_stereo_fraction"]
        assert tight["useful_stereo_fraction"] < loose["useful_stereo_fraction"]
