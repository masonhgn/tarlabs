"""The S-03 validation gate.

Three checks, in the order the plan states them:

1.  Propagation reproduces Vallado's published SGP4 verification vectors.
2.  SBIRS GEO satellites hold about 35,786 km altitude and about 1.0 rev/day.
3.  SDA Tranche 0 Tracking satellites sit at about 1000 km and about 81 degrees.

Check 1 is the one that matters: it is an external, citable reference, and it is what
separates "our propagator agrees with itself" from "our propagator agrees with the
standard". Checks 2 and 3 are cheap sanity gates that would catch a frame or unit error
that the verification vectors alone would not surface in our own call path.

If any of these fail, stop and fix the propagator before doing anything else downstream.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pytest
from sgp4.api import Satrec

from mwsim import catalog, propagate, registry

#: Vallado's verification data ships inside the sgp4 package itself.
_SGP4_DIR = Path(__import__("sgp4").__file__).resolve().parent
VER_TLE = _SGP4_DIR / "SGP4-VER.TLE"
TCPPVER = _SGP4_DIR / "tcppver.out"

#: Vallado's reference output is printed to 8 decimal places in km; agreement at the
#: sub-metre level means we are running the same algorithm, not merely a similar one.
VALLADO_TOL_KM = 1e-5
VALLADO_TOL_KM_S = 1e-8


def _parse_verification_cases() -> dict[str, list[tuple[float, np.ndarray, np.ndarray]]]:
    """Read tcppver.out into {satnum: [(minutes_since_epoch, r_teme, v_teme), ...]}."""
    cases: dict[str, list[tuple[float, np.ndarray, np.ndarray]]] = {}
    current: str | None = None
    for line in TCPPVER.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.endswith("xx"):
            current = stripped.split()[0]
            cases[current] = []
            continue
        if current is None:
            continue
        parts = stripped.split()
        if len(parts) < 7:
            continue
        try:
            values = [float(p) for p in parts[:7]]
        except ValueError:
            continue
        cases[current].append(
            (values[0], np.array(values[1:4]), np.array(values[4:7]))
        )
    return {k: v for k, v in cases.items() if v}


def _parse_verification_tles() -> dict[str, tuple[str, str]]:
    """Read SGP4-VER.TLE into {satnum: (line1, line2)}."""
    tles: dict[str, tuple[str, str]] = {}
    line1: str | None = None
    for raw in VER_TLE.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.startswith("#") or not line.strip():
            continue
        if line.startswith("1 "):
            line1 = line
        elif line.startswith("2 ") and line1 is not None:
            satnum = line1[2:7].strip()
            tles[satnum] = (line1, line)
            line1 = None
    return tles


class TestVerificationVectors:
    """Check 1 — agreement with Vallado's published SGP4 test vectors."""

    def test_verification_data_is_present(self) -> None:
        assert VER_TLE.exists(), f"missing {VER_TLE}"
        assert TCPPVER.exists(), f"missing {TCPPVER}"

    def test_matches_published_vectors(self) -> None:
        cases = _parse_verification_cases()
        tles = _parse_verification_tles()
        shared = sorted(set(cases) & set(tles))
        assert len(shared) >= 25, f"only {len(shared)} verification cases matched up"

        compared = 0
        worst_position = 0.0
        worst_velocity = 0.0

        for satnum in shared:
            line1, line2 = tles[satnum]
            sat = Satrec.twoline2rv(line1, line2)
            for minutes, r_expected, v_expected in cases[satnum]:
                error, r, v = sat.sgp4_tsince(minutes)
                if error != 0:
                    # Vallado's set deliberately includes decayed and error cases; those
                    # have no reference vector to compare against.
                    continue
                worst_position = max(
                    worst_position, float(np.max(np.abs(np.array(r) - r_expected)))
                )
                worst_velocity = max(
                    worst_velocity, float(np.max(np.abs(np.array(v) - v_expected)))
                )
                compared += 1

        assert compared >= 200, f"only compared {compared} state vectors"
        assert worst_position < VALLADO_TOL_KM, (
            f"worst position disagreement {worst_position:.3e} km "
            f"exceeds {VALLADO_TOL_KM:.0e} km over {compared} vectors"
        )
        assert worst_velocity < VALLADO_TOL_KM_S, (
            f"worst velocity disagreement {worst_velocity:.3e} km/s "
            f"exceeds {VALLADO_TOL_KM_S:.0e} km/s"
        )

    def test_our_propagate_path_agrees_with_the_library(self) -> None:
        """The vectors above exercise sgp4 directly; this exercises *our* call path.

        A frame, unit or time-grid mistake in propagate.propagate would not show up in the
        test above, which is exactly the kind of error that would silently poison every
        downstream coverage number.
        """
        tles = _parse_verification_tles()
        line1, line2 = tles["00005"]
        sat = Satrec.twoline2rv(line1, line2)

        # Anchor to the element-set epoch itself rather than a hand-typed date: getting
        # that offset wrong is precisely the class of error this test exists to catch.
        epoch = propagate.satrec_epoch(sat)
        assert epoch.year == 2000 and epoch.month == 6 and epoch.day == 27
        step = timedelta(minutes=6)
        times = propagate.time_grid(epoch, timedelta(minutes=60), step)

        eph = propagate.propagate({5: sat}, times)

        for i in range(eph.n_time):
            minutes = i * 6.0
            error, r_expected, _ = sat.sgp4_tsince(minutes)
            assert error == 0
            got = eph.position_teme_km[0, i]
            # The grid is built from a datetime, so it carries microsecond rounding that
            # sgp4_tsince does not. A metre of slack absorbs that and nothing else.
            assert np.allclose(got, r_expected, atol=1e-3), (
                f"step {i}: our path gave {got}, library gave {r_expected}"
            )


class TestFrameConversions:
    """Frame and geodetic conversions, checked against closed-form expectations."""

    def test_geodetic_round_trip_at_known_points(self) -> None:
        # Equator at the prime meridian, on the ellipsoid.
        ecef = np.array([[propagate.WGS84_A_KM, 0.0, 0.0]])
        lat, lon, alt = propagate.ecef_to_geodetic(ecef)
        assert np.allclose(lat, 0.0, atol=1e-9)
        assert np.allclose(lon, 0.0, atol=1e-9)
        assert np.allclose(alt, 0.0, atol=1e-9)

        # North pole, on the ellipsoid: the flattened, shorter semi-axis.
        ecef = np.array([[0.0, 0.0, propagate.WGS84_B_KM]])
        lat, _, alt = propagate.ecef_to_geodetic(ecef)
        assert np.allclose(lat, 90.0, atol=1e-6)
        assert np.allclose(alt, 0.0, atol=1e-6)

        # A point 1000 km up over the equator at 90 deg east.
        r = propagate.WGS84_A_KM + 1000.0
        ecef = np.array([[0.0, r, 0.0]])
        lat, lon, alt = propagate.ecef_to_geodetic(ecef)
        assert np.allclose(lat, 0.0, atol=1e-9)
        assert np.allclose(lon, 90.0, atol=1e-9)
        assert np.allclose(alt, 1000.0, atol=1e-6)

    def test_teme_to_ecef_preserves_radius(self) -> None:
        """The rotation is about the pole, so it cannot change a radius or a z."""
        rng = np.random.default_rng(20260922)
        times = propagate.time_grid(
            datetime(2026, 9, 22, tzinfo=timezone.utc), timedelta(hours=6), timedelta(minutes=30)
        )
        teme = rng.normal(scale=8000.0, size=(len(times), 3))
        ecef = propagate.teme_to_ecef(teme, times)
        assert np.allclose(
            np.linalg.norm(teme, axis=-1), np.linalg.norm(ecef, axis=-1), rtol=1e-12
        )
        assert np.allclose(teme[..., 2], ecef[..., 2], rtol=1e-12)

    def test_gmst_advances_one_sidereal_day(self) -> None:
        """GMST must advance by 2*pi over one sidereal day, not one solar day."""
        sidereal_day = timedelta(seconds=86164.0905)
        times = np.array(
            [
                np.datetime64(datetime(2026, 9, 22, tzinfo=timezone.utc).replace(tzinfo=None), "us"),
                np.datetime64(
                    (datetime(2026, 9, 22, tzinfo=timezone.utc) + sidereal_day).replace(tzinfo=None),
                    "us",
                ),
            ]
        )
        theta = propagate.gmst_rad(times)
        delta = (theta[1] - theta[0]) % (2 * np.pi)
        # Within an arcsecond of a full turn.
        assert min(delta, 2 * np.pi - delta) < np.deg2rad(1 / 3600)


class TestTimeGrid:
    def test_length_and_spacing(self) -> None:
        times = propagate.time_grid(
            datetime(2026, 1, 1, tzinfo=timezone.utc), timedelta(hours=1), timedelta(minutes=10)
        )
        assert len(times) == 7  # inclusive of both endpoints
        spacing = np.diff(times).astype("timedelta64[s]").astype(int)
        assert set(spacing.tolist()) == {600}

    def test_rejects_nonpositive_step(self) -> None:
        with pytest.raises(ValueError):
            propagate.time_grid(
                datetime(2026, 1, 1, tzinfo=timezone.utc), timedelta(hours=1), timedelta(0)
            )


# --------------------------------------------------------------------------------------
# Checks 2 and 3 need real catalogue elements. They run against the on-disk cache so the
# suite stays deterministic and offline; scripts/fetch_catalog.py refreshes that cache.
# --------------------------------------------------------------------------------------

def _cached_records(norad_ids: list[int]) -> dict[int, catalog.OmmRecord]:
    return catalog.fetch_many(norad_ids, offline=True)


requires_catalog = pytest.mark.skipif(
    not any(catalog.OMM_CACHE.glob("*.json")) if catalog.OMM_CACHE.exists() else True,
    reason="no cached OMM records; run scripts/fetch_catalog.py first",
)


@requires_catalog
class TestRealConstellations:
    """Checks 2 and 3 — the real elements land where the public record says they should."""

    def test_sbirs_geo_holds_geostationary_altitude_and_rate(self) -> None:
        ids = registry.norad_ids(registry.SBIRS_GEO)
        records = _cached_records(ids)
        assert records, "no cached SBIRS GEO records"

        satrecs = {k: propagate.satrec_from_omm(v) for k, v in records.items()}
        rates = propagate.revs_per_day(satrecs)
        for norad_id, rate in rates.items():
            assert 0.95 <= rate <= 1.05, f"NORAD {norad_id} at {rate:.3f} rev/day, not GEO"

        times = propagate.time_grid(
            datetime.now(timezone.utc), timedelta(hours=24), timedelta(minutes=30)
        )
        eph = propagate.propagate(satrecs, times)
        radius = np.nanmean(eph.radius_km(), axis=1)
        # Allow a wide band: these satellites drift, and some are in inclined
        # graveyard-adjacent or relocated slots. The point is the regime, not the slot.
        assert np.all(np.abs(radius - propagate.GEO_RADIUS_KM) < 1500.0), (
            f"mean radii {radius} km are not geostationary"
        )

    def test_tranche0_tracking_is_near_polar_leo(self) -> None:
        """Check 3, asserting what the catalogue actually shows.

        The inclination matches the published SDA figure exactly. **The altitude does
        not**, and the assertion here deliberately does not pretend otherwise -- see
        test_published_tranche0_altitude_does_not_match_the_catalogue below.
        """
        ids = registry.norad_ids(registry.SDA_TRANCHE0_TRACKING)
        records = _cached_records(ids)
        assert records, "no cached Tranche 0 records"

        satrecs = {k: propagate.satrec_from_omm(v) for k, v in records.items()}
        inclinations = propagate.inclination_deg(satrecs)

        times = propagate.time_grid(
            datetime.now(timezone.utc), timedelta(hours=6), timedelta(minutes=5)
        )
        eph = propagate.propagate(satrecs, times)
        altitudes = propagate.mean_altitude_km(eph)

        for norad_id, alt in zip(eph.norad_ids, altitudes):
            obj = registry.by_id(int(norad_id))
            assert 400.0 < alt < 1200.0, f"{obj.name} at {alt:.0f} km is not LEO at all"

        # The four SpaceX-built "BB" satellites form the near-polar group. The L3Harris
        # Raptor flew on USSF-124 into a ~40 deg orbit and is excluded by design.
        for norad_id in (56170, 56171, 57757, 57760):
            if norad_id in inclinations:
                inc = inclinations[norad_id]
                assert 75.0 < inc < 95.0, f"NORAD {norad_id} at {inc:.1f} deg, not near-polar"

    def test_tracking_layer_spans_two_distinct_geometries(self) -> None:
        """Pin the two-group structure of the Tranche 0 Tracking Layer (decision DEC-10).

        The eight Tracking satellites are not one homogeneous shell. The four SpaceX "BB"
        spacecraft are near-polar at ~620-790 km; the four L3Harris "RAPTOR" spacecraft
        are at ~40 deg and ~1000 km.

        This is **not** a contradiction of SDA's published figures, and an earlier version
        of this test wrongly framed it as one (retracted decision DEC-08). SDA's wording is
        that the *majority of Tranche 0 space vehicles* occupy two planes near 1000 km and
        80 deg -- a hedged statement about the tranche, not a specification for every
        Tracking satellite. The public record does not explain the RAPTOR geometry, and we
        do not invent a rationale for it.

        The test exists so that a re-identification of these objects, or a manoeuvre that
        collapses the two groups together, fails loudly rather than silently changing the
        coverage geometry the whole study rests on.
        """
        bb_ids = [56170, 56171, 57757, 57760]
        raptor_ids = [58956, 58957, 58958, 58959]
        records = _cached_records(bb_ids + raptor_ids)
        if len(records) < 8:
            pytest.skip("need all eight Tranche 0 Tracking satellites cached")

        satrecs = {k: propagate.satrec_from_omm(v) for k, v in records.items()}
        times = propagate.time_grid(
            datetime.now(timezone.utc), timedelta(hours=6), timedelta(minutes=5)
        )
        eph = propagate.propagate(satrecs, times)
        altitudes = dict(zip((int(n) for n in eph.norad_ids), propagate.mean_altitude_km(eph)))
        inclinations = propagate.inclination_deg(satrecs)

        bb_alt = np.array([altitudes[i] for i in bb_ids])
        raptor_alt = np.array([altitudes[i] for i in raptor_ids])

        # The two groups must stay separable, in both inclination and altitude.
        for i in bb_ids:
            assert 75.0 < inclinations[i] < 95.0, f"BB {i} at {inclinations[i]:.1f} deg"
        for i in raptor_ids:
            assert 35.0 < inclinations[i] < 45.0, f"RAPTOR {i} at {inclinations[i]:.1f} deg"

        assert np.all(bb_alt < 900.0), f"BB group has risen: {np.round(bb_alt)} km"
        assert np.all(raptor_alt > 900.0), f"RAPTOR group has fallen: {np.round(raptor_alt)} km"

    def test_ussf124_group_splits_into_two_altitudes(self) -> None:
        """The 2024-028 objects are not one homogeneous layer either.

        Raptor 2 and HBTSS-SV2 sit at ~1000 km; HBTSS-SV1 sits far lower. Recorded
        because the proposal must not model HBTSS as a single validated operational
        capability -- MDA reported (SpaceNews, 2025-04-25) that one of the two prototypes
        did not meet its requirements.
        """
        records = _cached_records([58955, 58959, 58960])
        if len(records) < 3:
            pytest.skip("need all three USSF-124 objects cached")

        satrecs = {k: propagate.satrec_from_omm(v) for k, v in records.items()}
        times = propagate.time_grid(
            datetime.now(timezone.utc), timedelta(hours=6), timedelta(minutes=5)
        )
        eph = propagate.propagate(satrecs, times)
        altitudes = dict(zip((int(n) for n in eph.norad_ids), propagate.mean_altitude_km(eph)))

        assert 900.0 < altitudes[58955] < 1100.0, f"HBTSS-SV2 at {altitudes[58955]:.0f} km"
        assert 900.0 < altitudes[58959] < 1100.0, f"Raptor 2 at {altitudes[58959]:.0f} km"
        assert altitudes[58960] < 700.0, (
            f"HBTSS-SV1 at {altitudes[58960]:.0f} km now matches its sibling; re-check D-8"
        )

    def test_element_sets_are_not_dangerously_stale(self) -> None:
        """SGP4 error grows 1-3 km/day past epoch. Warn loudly before it matters."""
        records = _cached_records(registry.norad_ids())
        assert records, "no cached records at all"
        stale = {
            r.norad_id: r.age.days for r in records.values() if r.age > timedelta(days=14)
        }
        assert not stale, (
            f"element sets older than 14 days (NORAD: days): {stale}. "
            "Re-run scripts/fetch_catalog.py."
        )
