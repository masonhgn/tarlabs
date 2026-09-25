"""The real, publicly catalogued missile-warning space objects we seed the simulation with.

Every object here except DSP-23 had published orbital elements when last checked, so the
GEO and LEO missile-warning layers can be seeded with *real* elements and only the
not-yet-launched layers (MEO, Tranche 1 and later) need synthesising.

**Catalogue availability is an object-level fact, not a mission-class rule.** An earlier
version of this file asserted that withheld objects are "chiefly NRO payloads". That is
unsupported: Space-Track publishes no comprehensive mission-by-mission withheld list, and
it states elements can be absent or delayed for security reasons *and* for ordinary
tracking and data-quality reasons. Treat a missing GP record as unresolved — never as
evidence of classification, decay or retirement.

There is no CelesTrak GROUP for SDA / PWSA / Tranche / missile-warning, so these are pulled
by catalogue number or international designator.

Contractor and layer assignments are **manifest-count inferences** — see the note on
SDA_TRANCHE0_TRACKING. They are not published agency lookups, and the proposal must say so.

Sources: CelesTrak GP API (elements, verified directly);
docs/research/deep-research-report.md (manifest reconciliation, 2026-09-23).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class CatalogObject:
    """One publicly catalogued satellite."""

    norad_id: int
    name: str
    cospar: str
    layer: str
    note: str = ""


#: GEO strategic missile warning — the legacy layer the topic calls "legacy OPIR".
SBIRS_GEO: tuple[CatalogObject, ...] = (
    CatalogObject(37481, "SBIRS GEO-1 (USA-230)", "2011-019A", "geo"),
    CatalogObject(39120, "SBIRS GEO-2 (USA-241)", "2013-011A", "geo"),
    CatalogObject(41937, "SBIRS GEO-3 (USA-273)", "2017-004A", "geo"),
    CatalogObject(43162, "SBIRS GEO-4 (USA-282)", "2018-009A", "geo"),
    CatalogObject(48618, "SBIRS GEO-5 (USA-315)", "2021-042A", "geo"),
    CatalogObject(53355, "SBIRS GEO-6 (USA-336)", "2022-092A", "geo", "GEO-7/8 cancelled"),
)

#: The final Defense Support Program satellite — the pre-SBIRS heritage sensor.
#:
#: CelesTrak returns no current GP record for 32287. That absence does **not** mean
#: decayed or renumbered: DSP-23 is a GEO object, reported to have malfunctioned and begun
#: drifting in 2008, and third-party aggregators still list it as an inactive object in
#: orbit. Space-Track notes the public catalogue can omit or delay elements for security
#: and for mundane tracking reasons alike, so "no GP record" is not by itself diagnostic.
#: Recorded status: inactive/failed; current GP availability unresolved.
DSP: tuple[CatalogObject, ...] = (
    CatalogObject(32287, "DSP-23 (USA-197)", "2007-054A", "geo", "final DSP; inactive/failed"),
)

#: SDA Tranche 0 Tracking Layer — all eight, the real proliferated-LEO demonstration
#: satellites. Four SpaceX-built ("BB") near-polar, four L3Harris-built ("RAPTOR") at
#: ~40 deg inclination.
#:
#: **Provenance of this mapping: manifest-count inference, not an agency lookup table.**
#: No SDA/SSC/MDA publication joins NORAD catalogue numbers to contractor and PWSA layer.
#: The inference is nonetheless strong, because the counts match one-to-one on every
#: launch: SDA states 8 York Transport + 2 SpaceX Tracking on 2023-050, 10 Lockheed
#: Transport + 1 York Transport + 2 SpaceX Tracking on 2023-133, and 4 L3Harris Tracking
#: + 2 HBTSS on USSF-124. The catalogue contains exactly 8 CHECKMATE + 2 BB, then 10
#: WILDFIRE + 1 CHECKMATE + 2 BB, then 4 RAPTOR + 2 HBTSS. Totals: 19 Transport
#: (CHECKMATE + WILDFIRE), 8 Tracking (BB + RAPTOR). The 19 rather than 20 is itself
#: confirmatory — SDA says one of the 20 Transport vehicles was retained on the ground as
#: a testbed. Verified against the catalogue 2026-09-22; decision DEC-10.
#:
#: **On altitude:** SDA's published "~1000 km, 80 deg" describes the *majority of Tranche 0
#: space vehicles*, not every Tracking satellite. The BB group measures 621-789 km and the
#: RAPTOR group ~1000 km at 40 deg, so the Tracking Layer spans at least two distinct
#: geometries in the public catalogue. This is not a contradiction of SDA's wording. The
#: public record does not explain the ~40 deg RAPTOR geometry; do not invent a rationale.
SDA_TRANCHE0_TRACKING: tuple[CatalogObject, ...] = (
    CatalogObject(56171, "BB 1", "2023-050K", "leo", "SpaceX-built (inferred); ~81 deg"),
    CatalogObject(56170, "BB 2", "2023-050J", "leo", "SpaceX-built (inferred); ~81 deg"),
    CatalogObject(57760, "BB 3", "2023-133D", "leo", "SpaceX-built (inferred); ~81 deg"),
    CatalogObject(57757, "BB 4", "2023-133B", "leo", "SpaceX-built (inferred); ~81 deg"),
    CatalogObject(58957, "RAPTOR 1", "2024-028C", "leo", "L3Harris-built (inferred); ~40 deg"),
    CatalogObject(58959, "RAPTOR 2", "2024-028E", "leo", "L3Harris-built (inferred); ~40 deg"),
    CatalogObject(58958, "RAPTOR 3", "2024-028D", "leo", "L3Harris-built (inferred); ~40 deg"),
    CatalogObject(58956, "RAPTOR 4", "2024-028B", "leo", "L3Harris-built (inferred); ~40 deg"),
)

#: SDA Tranche 0 Transport Layer — 19 on orbit. Not missile-warning sensors, but they
#: carry the low-latency optical mesh and the Link 16 injection that any edge-fusion
#: architecture depends on, so they belong in the registry for the latency model (S-09).
#: CHECKMATE = York-built, WILDFIRE = Lockheed Martin-built (same manifest inference).
SDA_TRANCHE0_TRANSPORT: tuple[CatalogObject, ...] = tuple(
    CatalogObject(norad, name, cospar, "leo", builder)
    for norad, name, cospar, builder in (
        (56162, "CHECKMATE 8", "2023-050A", "York (inferred)"),
        (56163, "CHECKMATE 5", "2023-050B", "York (inferred)"),
        (56164, "CHECKMATE 4", "2023-050C", "York (inferred)"),
        (56165, "CHECKMATE 6", "2023-050D", "York (inferred)"),
        (56166, "CHECKMATE 7", "2023-050E", "York (inferred)"),
        (56167, "CHECKMATE 2", "2023-050F", "York (inferred)"),
        (56168, "CHECKMATE 1", "2023-050G", "York (inferred)"),
        (56169, "CHECKMATE 3", "2023-050H", "York (inferred)"),
        (57762, "CHECKMATE 10", "2023-133F", "York (inferred)"),
        (57756, "WILDFIRE 4", "2023-133A", "Lockheed Martin (inferred)"),
        (57758, "WILDFIRE 3", "2023-133C", "Lockheed Martin (inferred)"),
        (57761, "WILDFIRE 7", "2023-133E", "Lockheed Martin (inferred)"),
        (57763, "WILDFIRE 6", "2023-133G", "Lockheed Martin (inferred)"),
        (57764, "WILDFIRE 1", "2023-133H", "Lockheed Martin (inferred)"),
        (57765, "WILDFIRE 9", "2023-133J", "Lockheed Martin (inferred)"),
        (57766, "WILDFIRE 10", "2023-133K", "Lockheed Martin (inferred)"),
        (57767, "WILDFIRE 2", "2023-133L", "Lockheed Martin (inferred)"),
        (57768, "WILDFIRE 8", "2023-133M", "Lockheed Martin (inferred)"),
        (57769, "WILDFIRE 5", "2023-133N", "Lockheed Martin (inferred)"),
    )
)

#: MDA Hypersonic and Ballistic Tracking Space Sensor prototypes — the MFOV
#: "fire-control-quality" demonstration. Launched 2024-02-14 on USSF-124.
#:
#: **Contractor mapping is secondary-source and was previously recorded backwards here.**
#: Public catalogue-derived material associates SV1/58960 with L3Harris and SV2/58955 with
#: Northrop Grumman; no MDA release pairing contractor to NORAD number was found. Tag it
#: as catalogue provenance, not agency-confirmed.
#:
#: **Do not claim one prototype failed.** L3Harris publicly states its own prototype
#: demonstrated fire-control-quality tracking against a live hypersonic target. No
#: government comparative test record establishing a Northrop shortfall was located, so
#: the proposal says "L3Harris reports successful demonstration" and stops there.
#: SV1 sits ~443 km below SV2; **altitude is not evidence of payload performance** and
#: must never be used as a proxy for it.
HBTSS: tuple[CatalogObject, ...] = (
    CatalogObject(58955, "HBTSS-SV2", "2024-028A", "leo", "Northrop Grumman (secondary source)"),
    CatalogObject(58960, "HBTSS-SV1", "2024-028F", "leo", "L3Harris (secondary source)"),
)

#: Not missile warning — used only as a propagation validation reference (S-03).
REFERENCE: tuple[CatalogObject, ...] = (
    CatalogObject(25544, "ISS (ZARYA)", "1998-067A", "reference", "propagation cross-check"),
)


ALL: tuple[CatalogObject, ...] = (
    SBIRS_GEO + DSP + SDA_TRANCHE0_TRACKING + SDA_TRANCHE0_TRANSPORT + HBTSS + REFERENCE
)

#: The sensing objects proper — what detects a launch. Excludes the Transport Layer
#: (a comms mesh, not a sensor) and the propagation reference.
MISSILE_WARNING: tuple[CatalogObject, ...] = (
    SBIRS_GEO + DSP + SDA_TRANCHE0_TRACKING + HBTSS
)

#: The eight Tranche 0 Tracking satellites, by the manifest-count inference.
TRACKING_LAYER: tuple[CatalogObject, ...] = SDA_TRANCHE0_TRACKING


def by_id(norad_id: int) -> CatalogObject:
    """Look one object up by catalogue number."""
    for obj in ALL:
        if obj.norad_id == norad_id:
            return obj
    raise KeyError(f"NORAD ID {norad_id} is not in the registry")


def in_layer(layer: str) -> Iterator[CatalogObject]:
    """Iterate the registry objects in one orbital layer ('geo', 'leo', 'reference')."""
    return (obj for obj in ALL if obj.layer == layer)


def norad_ids(objects: tuple[CatalogObject, ...] = MISSILE_WARNING) -> list[int]:
    """Catalogue numbers, for handing to the fetcher."""
    return [obj.norad_id for obj in objects]
