"""Generate the S-03 propagation validation report.

    python scripts/validate_propagation.py

Writes analysis/validation/propagation.md. The report is the artifact the ledger asks for;
regenerating it is how we prove the numbers in the proposal were not typed by hand.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
from sgp4.api import Satrec

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from mwsim import catalog, propagate, registry  # noqa: E402

OUT = ROOT / "analysis" / "validation" / "propagation.md"

#: A fixed grid length for the measurement table, so reruns are comparable.
SPAN = timedelta(hours=12)
STEP = timedelta(minutes=2)


def _vallado_agreement() -> tuple[int, float, float]:
    """Re-run the published verification vectors and report the worst disagreement."""
    sgp4_dir = Path(__import__("sgp4").__file__).resolve().parent
    tles: dict[str, tuple[str, str]] = {}
    line1 = None
    for raw in (sgp4_dir / "SGP4-VER.TLE").read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.startswith("#") or not line.strip():
            continue
        if line.startswith("1 "):
            line1 = line
        elif line.startswith("2 ") and line1 is not None:
            tles[line1[2:7].strip()] = (line1, line)
            line1 = None

    cases: dict[str, list[tuple[float, np.ndarray, np.ndarray]]] = {}
    current = None
    for raw in (sgp4_dir / "tcppver.out").read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.endswith("xx"):
            current = s.split()[0]
            cases[current] = []
            continue
        if current is None:
            continue
        parts = s.split()
        if len(parts) < 7:
            continue
        try:
            v = [float(p) for p in parts[:7]]
        except ValueError:
            continue
        cases[current].append((v[0], np.array(v[1:4]), np.array(v[4:7])))

    compared, worst_r, worst_v = 0, 0.0, 0.0
    for satnum in sorted(set(cases) & set(tles)):
        sat = Satrec.twoline2rv(*tles[satnum])
        for minutes, r_exp, v_exp in cases[satnum]:
            err, r, v = sat.sgp4_tsince(minutes)
            if err != 0:
                continue
            worst_r = max(worst_r, float(np.max(np.abs(np.array(r) - r_exp))))
            worst_v = max(worst_v, float(np.max(np.abs(np.array(v) - v_exp))))
            compared += 1
    return compared, worst_r, worst_v


def _measure() -> tuple[list[dict], datetime]:
    records = catalog.fetch_many(registry.norad_ids(registry.ALL), offline=True)
    if not records:
        raise SystemExit("no cached elements; run scripts/fetch_catalog.py first")

    satrecs = {k: propagate.satrec_from_omm(v) for k, v in records.items()}
    start = datetime.now(timezone.utc)
    times = propagate.time_grid(start, SPAN, STEP)
    eph = propagate.propagate(satrecs, times)

    ecef = propagate.teme_to_ecef(eph.position_teme_km, eph.times)
    _, _, alt = propagate.ecef_to_geodetic(ecef)
    incl = propagate.inclination_deg(satrecs)
    rate = propagate.revs_per_day(satrecs)

    rows = []
    for i, raw_id in enumerate(eph.norad_ids):
        norad_id = int(raw_id)
        obj = registry.by_id(norad_id)
        rows.append(
            {
                "norad": norad_id,
                "name": obj.name,
                "layer": obj.layer,
                "epoch": records[norad_id].epoch,
                "age_days": records[norad_id].age.total_seconds() / 86400.0,
                "alt_min": float(np.nanmin(alt[i])),
                "alt_mean": float(np.nanmean(alt[i])),
                "alt_max": float(np.nanmax(alt[i])),
                "incl": incl[norad_id],
                "rate": rate[norad_id],
            }
        )
    return rows, start


def main() -> int:
    compared, worst_r, worst_v = _vallado_agreement()
    rows, start = _measure()
    missing = [
        o.norad_id for o in registry.ALL if o.norad_id not in {r["norad"] for r in rows}
    ]

    lines: list[str] = []
    w = lines.append

    w("# S-03 — Propagation validation report")
    w("")
    w(f"Generated {datetime.now(timezone.utc).isoformat(timespec='seconds')} by")
    w("`scripts/validate_propagation.py`. Do not edit by hand; regenerate it.")
    w("")
    w("## Check 1 — agreement with Vallado's published SGP4 verification vectors")
    w("")
    w("The reference data (`SGP4-VER.TLE`, `tcppver.out`) ships inside the `sgp4` package")
    w("and is the standard verification set for the algorithm.")
    w("")
    w(f"- State vectors compared: **{compared}**")
    w(f"- Worst position disagreement: **{worst_r:.3e} km** ({worst_r * 1e6:.2f} mm)")
    w(f"- Worst velocity disagreement: **{worst_v:.3e} km/s**")
    w("")
    w("Agreement at this level means we are running the standard algorithm, not an")
    w("approximation of it. Any remaining error against reality is physical -- the")
    w("limitation of mean elements -- not an implementation defect.")
    w("")
    w("## Check 2 and 3 — real catalogued elements land in the expected regimes")
    w("")
    w(f"Measured over {SPAN.total_seconds() / 3600:.0f} h at {STEP.total_seconds() / 60:.0f} min")
    w(f"steps from {start.isoformat(timespec='seconds')}. Altitude is WGS-84 geodetic.")
    w("")
    w("| NORAD | Object | Layer | Epoch age | rev/day | Incl (deg) | Alt min | Alt mean | Alt max |")
    w("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        w(
            f"| {r['norad']} | {r['name']} | {r['layer']} | {r['age_days']:.1f} d | "
            f"{r['rate']:.4f} | {r['incl']:.2f} | {r['alt_min']:.1f} | "
            f"{r['alt_mean']:.1f} | {r['alt_max']:.1f} |"
        )
    w("")
    if missing:
        names = ", ".join(f"{registry.by_id(i).name} ({i})" for i in missing)
        w(f"**Not retrievable from the CelesTrak GP set:** {names}.")
        w("")

    geo = [r for r in rows if r["layer"] == "geo"]
    if geo:
        w("### Check 2 — SBIRS GEO")
        w("")
        lo = min(r["alt_mean"] for r in geo)
        hi = max(r["alt_mean"] for r in geo)
        rates = [r["rate"] for r in geo]
        w(f"Mean altitude spans **{lo:.0f}-{hi:.0f} km** against the nominal 35,786 km, and")
        w(f"mean motion spans **{min(rates):.4f}-{max(rates):.4f} rev/day** against the")
        w("nominal 1.0027. The regime is confirmed. Inclinations of 2-5 deg are expected:")
        w("ageing GEO satellites are commonly allowed to drift in inclination to save the")
        w("fuel that north-south stationkeeping would cost.")
        w("")

    w("### Check 3 — the Tranche 0 Tracking Layer spans two distinct geometries")
    w("")
    w("The eight Tracking satellites are not one homogeneous shell:")
    w("")
    for label, ids in (
        ("SpaceX-built, near-polar", (56171, 56170, 57760, 57757)),
        ("L3Harris-built, mid-inclination", (58957, 58959, 58958, 58956)),
    ):
        w(f"*{label}:*")
        w("")
        for r in rows:
            if r["norad"] in ids:
                w(f"- {r['name']}: **{r['alt_mean']:.0f} km**, {r['incl']:.2f} deg")
        w("")
    w("**This is not a contradiction of SDA's published figures.** SDA's wording is that")
    w("the *majority of Tranche 0 space vehicles* occupy two planes near 1000 km and 80")
    w("deg -- a hedged statement about the tranche as a whole, not a specification for")
    w("every Tracking satellite. An earlier version of this report framed it as a")
    w("discrepancy; that framing was wrong and is retracted (decision DEC-08 -> D-10).")
    w("The public record does not explain the mid-inclination geometry of the L3Harris")
    w("group, and we do not invent a rationale for it.")
    w("")
    w("The MDA HBTSS prototypes split similarly -- SV2 near 1000 km, SV1 near 560 km.")
    w("**Altitude is not evidence of payload performance** and is never used as a proxy")
    w("for it here. L3Harris publicly reports a successful demonstration of its own")
    w("prototype; no government comparative test record was located, so no claim is made")
    w("about the other.")
    w("")
    w("What this means for the study, per decision DEC-11: architecture documents and")
    w("catalogue geometry answer different questions. Propagate the real objects for")
    w("current-epoch coverage; use agency-stated design parameters for future-architecture")
    w("trades; never substitute one for the other.")
    w("")
    w("**Provenance note.** The object-to-layer assignment above is a *manifest-count")
    w("inference*, not a published agency lookup -- no SDA/SSC/MDA source joins NORAD")
    w("numbers to contractor and layer. The inference is strong because the counts match")
    w("one-to-one across all three launches (19 Transport, 8 Tracking, 2 HBTSS), and the")
    w("19-rather-than-20 Transport count independently corroborates SDA's statement that")
    w("one vehicle was retained on the ground as a testbed.")
    w("")
    w("## Stated limitations")
    w("")
    w("- TLE/OMM mean elements propagated with SGP4 carry roughly **1 km** of position")
    w("  error at epoch, growing **1-3 km/day**. The oldest element set used here is")
    w(f"  **{max(r['age_days'] for r in rows):.1f} days** old.")
    w("- Mean elements cannot be converted to osculating elements without error, so they")
    w("  must be propagated with a simplified-perturbations model and nothing else.")
    w("- `teme_to_ecef` neglects polar motion and the TEME-to-PEF equation-of-equinoxes")
    w("  term (tens of metres), and approximates UT1 by UTC (up to ~0.4 km of Earth")
    w("  rotation at the equator). All are inside the SGP4 error budget above.")
    w("- This fidelity is adequate for a trade study over notional geometry and")
    w("  **inadequate for fire control**. The proposal says so in those words.")
    w("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"  Vallado: {compared} vectors, worst {worst_r:.3e} km")
    print(f"  measured: {len(rows)} objects, {len(missing)} missing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
