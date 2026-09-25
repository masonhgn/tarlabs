"""Solar/lunar geometry validation (task D-08).

Anchored to astronomy that is true independently of this code: solstice declinations equal
the obliquity, the Earth is nearest the Sun in January, and the subsolar point has zero
solar zenith angle by definition.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

from mwsim import ephemeris as eph
from mwsim import propagate

AU_KM = 1.495978707e8


def _t(dt: datetime) -> np.ndarray:
    return propagate.time_grid(dt, timedelta(0), timedelta(minutes=1))


def _wrap(x: float) -> float:
    return (x + 180.0) % 360.0 - 180.0


def _subsolar(times: np.ndarray) -> tuple[float, float]:
    sun = eph.sun_position_gcrs_km(times)[0]
    decl = float(np.degrees(np.arcsin(sun[2] / np.linalg.norm(sun))))
    ra = float(np.degrees(np.arctan2(sun[1], sun[0])))
    lon = _wrap(ra - float(np.degrees(propagate.gmst_rad(times))[0]))
    return decl, lon


try:
    eph.sun_position_gcrs_km(_t(datetime(2026, 1, 1, tzinfo=timezone.utc)))
    _HAVE = True
except Exception:
    _HAVE = False

requires_ephemeris = pytest.mark.skipif(_HAVE is False, reason="ephemeris kernel unavailable")


@requires_ephemeris
class TestSolarPosition:
    @pytest.mark.parametrize(
        "dt,expected",
        [
            (datetime(2026, 6, 21, 12, tzinfo=timezone.utc), 23.44),
            (datetime(2026, 12, 21, 12, tzinfo=timezone.utc), -23.44),
        ],
    )
    def test_solstice_declination_equals_the_obliquity(self, dt, expected) -> None:
        decl, _ = _subsolar(_t(dt))
        assert decl == pytest.approx(expected, abs=0.1)

    def test_equinox_declination_is_near_zero(self) -> None:
        decl, _ = _subsolar(_t(datetime(2026, 3, 20, 12, tzinfo=timezone.utc)))
        assert abs(decl) < 0.5

    def test_earth_is_nearer_the_sun_in_january(self) -> None:
        """Perihelion is early January, aphelion early July — not the solstices."""
        jan = np.linalg.norm(
            eph.sun_position_gcrs_km(_t(datetime(2026, 1, 4, tzinfo=timezone.utc)))[0]
        )
        jul = np.linalg.norm(
            eph.sun_position_gcrs_km(_t(datetime(2026, 7, 5, tzinfo=timezone.utc)))[0]
        )
        assert jan < jul
        assert 0.98 < jan / AU_KM < 0.99
        assert 1.01 < jul / AU_KM < 1.02

    def test_moon_distance_is_plausible(self) -> None:
        d = np.linalg.norm(
            eph.moon_position_gcrs_km(_t(datetime(2026, 5, 1, tzinfo=timezone.utc)))[0]
        )
        assert 356000.0 < d < 407000.0


@requires_ephemeris
class TestTerminator:
    def test_subsolar_point_has_zero_zenith_angle(self) -> None:
        times = _t(datetime(2026, 6, 21, 12, tzinfo=timezone.utc))
        decl, lon = _subsolar(times)
        z = eph.solar_zenith_angle_deg(np.array([decl]), np.array([lon]), times)
        assert float(z[0]) == pytest.approx(0.0, abs=0.05)

    def test_antipode_has_180_degree_zenith_angle(self) -> None:
        """The antipode negates latitude AND shifts longitude by 180."""
        times = _t(datetime(2026, 6, 21, 12, tzinfo=timezone.utc))
        decl, lon = _subsolar(times)
        z = eph.solar_zenith_angle_deg(
            np.array([-decl]), np.array([_wrap(lon + 180.0)]), times
        )
        assert float(z[0]) == pytest.approx(180.0, abs=0.05)

    def test_zenith_angle_matches_great_circle_distance(self) -> None:
        """Solar zenith angle IS the great-circle distance from the subsolar point.

        Guards against confusing a longitude offset with an angular one: 90 degrees of
        longitude at 23 degrees latitude is only ~81 degrees of arc.
        """
        times = _t(datetime(2026, 6, 21, 12, tzinfo=timezone.utc))
        decl, lon = _subsolar(times)
        lat2, lon2 = decl, _wrap(lon + 90.0)
        expected = np.degrees(
            np.arccos(
                np.sin(np.radians(decl)) * np.sin(np.radians(lat2))
                + np.cos(np.radians(decl))
                * np.cos(np.radians(lat2))
                * np.cos(np.radians(lon2 - lon))
            )
        )
        z = eph.solar_zenith_angle_deg(np.array([lat2]), np.array([lon2]), times)
        assert float(z[0]) == pytest.approx(float(expected), abs=0.1)


class TestOcclusion:
    RE = eph.EARTH_RADIUS_KM

    def test_opposite_sides_are_occulted(self) -> None:
        a = np.array([[self.RE + 1000.0, 0.0, 0.0]])
        b = np.array([[-(self.RE + 1000.0), 0.0, 0.0]])
        assert bool(eph.earth_occulted(a, b)[0])

    def test_adjacent_satellites_are_not(self) -> None:
        a = np.array([[self.RE + 1000.0, 0.0, 0.0]])
        b = np.array([[self.RE + 1000.0, 500.0, 0.0]])
        assert not bool(eph.earth_occulted(a, b)[0])

    def test_segment_not_infinite_line(self) -> None:
        """Two satellites on the same side, whose extended line passes near the centre.

        An infinite-line test reports an occultation here that does not exist. This is the
        specific bug the segment clamp prevents.
        """
        a = np.array([[self.RE + 1000.0, 500.0, 0.0]])
        b = np.array([[self.RE + 1000.0, -500.0, 0.0]])
        assert not bool(eph.earth_occulted(a, b)[0])

    def test_geo_to_leo_across_the_limb(self) -> None:
        geo = np.array([[42164.0, 0.0, 0.0]])
        leo = np.array([[0.0, self.RE + 1000.0, 0.0]])
        assert not bool(eph.earth_occulted(geo, leo)[0])
        # Directly opposite the GEO satellite, so the line of sight runs through the
        # Earth's centre.
        behind = np.array([[-(self.RE + 200.0), 0.0, 0.0]])
        assert bool(eph.earth_occulted(geo, behind)[0])

    def test_grazing_ray_is_not_occulted(self) -> None:
        """A near-limb sightline that clears the surface must stay visible.

        Worth pinning because intuition is unreliable here: a target at 219 km altitude
        apparently 'behind' the Earth from GEO turns out to have a sightline clearing the
        surface by 47 km. Off-by-a-limb errors of this kind would quietly delete real
        coverage.

        Note this model ignores atmospheric refraction and absorption, so a ray grazing at
        47 km is geometrically clear but radiometrically questionable. The detection model
        applies a separate minimum grazing-angle cut (S-07); this function answers only
        the geometric question.
        """
        geo = np.array([[42164.0, 0.0, 0.0]])
        grazing = np.array([[-500.0, -(self.RE + 200.0), 0.0]])
        assert not bool(eph.earth_occulted(geo, grazing)[0])


@requires_ephemeris
class TestIllumination:
    def test_sunward_point_is_lit_and_antisunward_is_not(self) -> None:
        times = _t(datetime(2026, 6, 21, 12, tzinfo=timezone.utc))
        sun = eph.sun_position_gcrs_km(times)[0]
        unit = sun / np.linalg.norm(sun)
        r = eph.EARTH_RADIUS_KM + 1000.0
        assert bool(eph.is_sunlit(np.atleast_2d(unit * r), times)[0])
        assert not bool(eph.is_sunlit(np.atleast_2d(-unit * r), times)[0])

    def test_a_point_beside_the_shadow_is_lit(self) -> None:
        """Anti-sunward but outside the shadow cylinder: still illuminated."""
        times = _t(datetime(2026, 6, 21, 12, tzinfo=timezone.utc))
        sun = eph.sun_position_gcrs_km(times)[0]
        unit = sun / np.linalg.norm(sun)
        perp = np.cross(unit, [0.0, 0.0, 1.0])
        perp /= np.linalg.norm(perp)
        p = -unit * 8000.0 + perp * (eph.EARTH_RADIUS_KM + 2000.0)
        assert bool(eph.is_sunlit(np.atleast_2d(p), times)[0])


class TestAngleBetween:
    def test_orthogonal_and_parallel(self) -> None:
        x = np.array([[1.0, 0.0, 0.0]])
        y = np.array([[0.0, 1.0, 0.0]])
        assert float(eph.angle_between_deg(x, y)[0]) == pytest.approx(90.0)
        assert float(eph.angle_between_deg(x, x)[0]) == pytest.approx(0.0, abs=1e-9)
        assert float(eph.angle_between_deg(x, -x)[0]) == pytest.approx(180.0)

    def test_precision_for_nearly_parallel_vectors(self) -> None:
        """The reason for arctan2 rather than arccos of the dot product."""
        a = np.array([[1.0, 0.0, 0.0]])
        b = np.array([[1.0, 1e-7, 0.0]])
        got = float(eph.angle_between_deg(a, b)[0])
        assert got == pytest.approx(np.degrees(1e-7), rel=1e-3)
