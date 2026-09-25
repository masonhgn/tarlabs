"""Target motion sourcing (task S-06, DEC-38).

We consume an external published tool rather than modelling this motion ourselves. These
tests cover the parts that *are* ours: caching, resampling, and placing a track-relative
trajectory onto a spherical Earth.
"""

from __future__ import annotations

import numpy as np
import pytest

from mwsim import target_motion as tm


def _cached():
    return tm.load_cached()


requires_cache = pytest.mark.skipif(not _cached(), reason="no cached trajectory")


class TestCacheKey:
    def test_integer_and_float_conditions_hash_alike(self) -> None:
        """0 and 0.0 are the same flight condition.

        Without normalisation they serialise differently, miss the cache, and re-hit a
        free public research service for a trajectory already on disk.
        """
        assert tm._cache_key({"v0": 6.1, "roll": 0}) == tm._cache_key({"v0": 6.1, "roll": 0.0})

    def test_different_conditions_hash_differently(self) -> None:
        assert tm._cache_key({"v0": 6.1}) != tm._cache_key({"v0": 5.0})

    def test_key_is_order_independent(self) -> None:
        assert tm._cache_key({"a": 1.0, "b": 2.0}) == tm._cache_key({"b": 2.0, "a": 1.0})


class TestOfflineBehaviour:
    def test_offline_without_cache_raises_rather_than_inventing(self) -> None:
        with pytest.raises(tm.TargetMotionUnavailable):
            tm.fetch(
                speed_km_s=1.234, ballistic_coefficient=99999,
                lift_to_drag=9.9, offline=True,
            )


@requires_cache
class TestCachedTrack:
    @pytest.fixture(scope="class")
    def track(self):
        return _cached()[0]

    def test_has_the_expected_fields(self, track) -> None:
        for arr in (track.time_s, track.altitude_km, track.downrange_km,
                    track.speed_km_s, track.flight_path_deg, track.heading_deg):
            assert len(arr) == len(track)

    def test_records_its_source(self, track) -> None:
        """Provenance travels with the data, as everywhere else in this project."""
        assert "onrender.com" in track.source or "brsl" in track.source.lower()
        assert track.conditions, "flight conditions must be retained"

    def test_time_increases(self, track) -> None:
        assert np.all(np.diff(track.time_s) > 0)

    def test_slows_and_descends(self, track) -> None:
        """Unpowered flight: it loses speed and it comes down."""
        assert track.speed_km_s[-1] < track.speed_km_s[0]
        assert track.altitude_km[-1] < track.altitude_km[0]

    def test_reproduces_the_published_range(self, track) -> None:
        """Tracy & Wright report ~7,630 km for these conditions.

        This is why consuming the external tool is defensible: it agrees with the
        literature independently of any transcription we might have made.
        """
        assert 7400.0 < track.max_range_km < 7900.0, f"{track.max_range_km:.0f} km"


@requires_cache
class TestResampling:
    @pytest.fixture(scope="class")
    def track(self):
        return _cached()[0]

    def test_resamples_onto_a_requested_grid(self, track) -> None:
        g = np.linspace(0, 1000, 37)
        r = track.resample(g)
        assert len(r) == 37
        assert r.time_s[0] == pytest.approx(max(g[0], track.time_s[0]))

    def test_clamps_rather_than_extrapolating(self, track) -> None:
        """A target that has landed has landed.

        Extrapolating past the end of a cited trajectory would invent motion nobody
        published, which is exactly what this project avoids elsewhere.
        """
        beyond = track.time_s[-1] + 5000.0
        r = track.resample(np.array([beyond]))
        assert r.altitude_km[0] == pytest.approx(track.altitude_km[-1], abs=1e-6)

    def test_preserves_provenance_through_resampling(self, track) -> None:
        r = track.resample(np.linspace(0, 500, 10))
        assert r.source == track.source
        assert r.conditions == track.conditions


@requires_cache
class TestEciPlacement:
    @pytest.fixture(scope="class")
    def track(self):
        return _cached()[0]

    def test_radius_matches_altitude(self, track) -> None:
        eci = track.to_eci_km()
        r = np.linalg.norm(eci, axis=1)
        assert np.allclose(r - tm.RE_KM, track.altitude_km, atol=1e-6)

    def test_start_point_places_where_asked(self, track) -> None:
        eci = track.to_eci_km(start_lat_deg=30.0, start_lon_deg=-80.0)
        r = np.linalg.norm(eci[0])
        lat = np.degrees(np.arcsin(eci[0, 2] / r))
        lon = np.degrees(np.arctan2(eci[0, 1], eci[0, 0]))
        assert lat == pytest.approx(30.0, abs=0.5)
        assert lon == pytest.approx(-80.0, abs=0.5)

    def test_downrange_moves_the_target(self, track) -> None:
        eci = track.to_eci_km()
        separation = np.linalg.norm(eci[-1] - eci[0])
        assert separation > 1000.0, "the target should have travelled a long way"
