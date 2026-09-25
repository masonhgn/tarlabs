"""Earth orientation parameter bounds (task D-15).

These tests exist to keep two documented approximations honest. If UT1-UTC or polar motion
ever grow enough to matter against the SGP4 error floor, the assertions here fail and the
decision not to correct for them gets revisited with evidence.
"""

from __future__ import annotations

import numpy as np
import pytest

from mwsim import earth_orientation as eo

_HAVE = eo.EOP_FILE.exists()
requires_eop = pytest.mark.skipif(not _HAVE, reason="IERS finals2000A not downloaded")


class TestErrorConversion:
    def test_one_second_is_about_465_metres_at_the_equator(self) -> None:
        """Earth's equatorial surface speed: 2*pi*R_E per sidereal day."""
        assert float(eo.rotation_error_km(1.0)) == pytest.approx(0.465, abs=0.005)

    def test_one_arcsecond_of_pole_motion_is_about_31_metres(self) -> None:
        assert float(eo.polar_motion_error_km(1.0, 0.0)) == pytest.approx(0.0309, abs=0.001)

    def test_errors_scale_linearly(self) -> None:
        assert float(eo.rotation_error_km(2.0)) == pytest.approx(
            2.0 * float(eo.rotation_error_km(1.0))
        )

    def test_sign_does_not_matter(self) -> None:
        assert float(eo.rotation_error_km(-0.5)) == float(eo.rotation_error_km(0.5))


@requires_eop
class TestMeasuredBounds:
    def test_ut1_utc_stays_small_enough_to_ignore(self) -> None:
        """The approximation UT1 ~ UTC, bounded against the SGP4 floor.

        SGP4 carries ~1 km at epoch. If the rotation error from ignoring UT1-UTC ever
        approaches a tenth of that, the approximation deserves revisiting.
        """
        b = eo.approximation_bounds()
        assert b["max_ut1_utc_s"] < 0.5, f"UT1-UTC reached {b['max_ut1_utc_s']:.3f} s"
        assert b["max_rotation_error_km"] < 0.25, (
            f"rotation error reached {b['max_rotation_error_km']*1000:.0f} m; "
            "reconsider correcting for UT1-UTC"
        )

    def test_polar_motion_stays_negligible(self) -> None:
        b = eo.approximation_bounds()
        assert b["max_polar_motion_error_km"] < 0.05, (
            f"polar motion reached {b['max_polar_motion_error_km']*1000:.0f} m"
        )

    def test_both_are_well_below_the_sgp4_error_floor(self) -> None:
        """The actual justification for ignoring them, asserted rather than asserted-in-prose."""
        sgp4_floor_km = 1.0
        b = eo.approximation_bounds()
        assert b["max_rotation_error_km"] < sgp4_floor_km / 5.0
        assert b["max_polar_motion_error_km"] < sgp4_floor_km / 20.0

    def test_lookup_interpolates_within_the_series(self) -> None:
        t = np.array([np.datetime64("2024-06-15T12:00:00", "s")])
        v = float(eo.ut1_minus_utc(t)[0])
        assert -1.0 < v < 1.0
        x, y = eo.polar_motion_arcsec(t)
        assert abs(float(x[0])) < 1.0 and abs(float(y[0])) < 1.0

    def test_clamps_rather_than_extrapolating_outside_the_range(self) -> None:
        """Leap seconds reset UT1-UTC discontinuously; extrapolation would be worse."""
        far = np.array([np.datetime64("2200-01-01T00:00:00", "s")])
        assert abs(float(eo.ut1_minus_utc(far)[0])) < 2.0

    def test_mjd_conversion_anchors_correctly(self) -> None:
        """MJD 40587 is the Unix epoch, 1970-01-01."""
        t = np.array([np.datetime64("1970-01-01T00:00:00", "s")])
        assert float(eo.datetime64_to_mjd(t)[0]) == pytest.approx(40587.0)
