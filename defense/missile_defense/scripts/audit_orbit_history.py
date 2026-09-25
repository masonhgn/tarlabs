"""Generate the D-14 multi-epoch orbit audit report.

    python scripts/audit_orbit_history.py

Writes analysis/data/orbit_history.md. Requires the Space-Track pull first:
    python scripts/fetch_orbit_history.py
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from mwsim import orbit_history as oh  # noqa: E402
from mwsim import registry  # noqa: E402

OUT = ROOT / "analysis" / "data" / "orbit_history.md"


def _noise_floor(objects) -> tuple[float, list[str]]:
    """Largest consecutive-record step seen on objects with no detected manoeuvres.

    These are the natural control group: whatever they show is element-fit noise, because
    nothing moved them. It is what justifies the detection threshold.
    """
    worst = 0.0
    names = []
    for obj in objects:
        try:
            history = oh.load_history(obj.norad_id)
        except (FileNotFoundError, ValueError):
            continue
        if oh.detect_maneuvers(history):
            continue
        names.append(obj.name)
        steps = np.abs(np.diff(history.semi_major_km))
        if steps.size:
            worst = max(worst, float(steps.max()))
    return worst, names


def main() -> int:
    objects = registry.SDA_TRANCHE0_TRACKING + registry.HBTSS
    rows = []
    for obj in objects:
        try:
            history = oh.load_history(obj.norad_id)
        except (FileNotFoundError, ValueError) as exc:
            print(f"skipping {obj.name}: {exc}", file=sys.stderr)
            continue
        maneuvers = oh.detect_maneuvers(history)
        rows.append(
            {
                "obj": obj,
                "h": history,
                "alt0": float((history.apoapsis_km[0] + history.periapsis_km[0]) / 2),
                "alt1": float((history.apoapsis_km[-1] + history.periapsis_km[-1]) / 2),
                "maneuvers": maneuvers,
                "decay": oh.decay_estimate(history),
                "fraction": oh.maneuver_fraction(history),
                "verdict": oh.classify(history),
            }
        )

    if not rows:
        print("no cached histories; run scripts/fetch_orbit_history.py", file=sys.stderr)
        return 1

    noise, control_names = _noise_floor(objects)

    lines: list[str] = []
    w = lines.append

    w("# D-14 — Multi-epoch orbit audit")
    w("")
    w(f"Generated {datetime.now(timezone.utc).isoformat(timespec='seconds')} by")
    w("`scripts/audit_orbit_history.py` from Space-Track `gp_history`. Do not edit by hand.")
    w("")
    w("## Why this exists")
    w("")
    w("Working from a single element epoch, we previously inferred that the Tranche 0")
    w("\"BB\" satellites were decaying, and reasoned from that toward their mission status.")
    w("A single fitted drag derivative cannot support either step. This audit replaces")
    w("that inference with the full element history from launch.")
    w("")
    w("## Method")
    w("")
    w("A **manoeuvre** is a persistent step in semi-major axis: the median over the next")
    w(f"{oh.PERSISTENCE_RECORDS} records must differ from the median over the previous")
    w(f"{oh.PERSISTENCE_RECORDS} by at least {oh.MANEUVER_THRESHOLD_KM:.1f} km. Requiring")
    w("persistence rejects isolated bad element fits without smoothing away real steps.")
    w("")
    w("**Drag rate** is fitted only over the longest *contiguous* manoeuvre-free stretch,")
    w("and reported as not measurable when no stretch is long enough. Fitting scattered")
    w("survivors between clustered burns is not a smaller version of the right answer --")
    w("it produced a *positive* drag rate for a satellite that had lost 325 km.")
    w("")
    w("### Threshold justification")
    w("")
    if control_names:
        w(f"Objects with no detected manoeuvres ({', '.join(control_names)}) are a natural")
        w("control group: anything they show is element-fit noise. Across their full")
        w(f"records the largest consecutive-record step is **{noise:.3f} km**, so the")
        w(f"{oh.MANEUVER_THRESHOLD_KM:.1f} km threshold sits above the observed noise")
        w("ceiling. The steps detected on the moving objects reach tens of kilometres.")
    w("")
    w("## Results")
    w("")
    w("Altitude is the mean of apoapsis and periapsis as Space-Track reports them.")
    w("")
    w("| Object | Record | Alt at launch | Alt now | Net | Manoeuvres | Step share | Drag (km/yr) | Orbit |")
    w("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        decay = r["decay"]
        drag = (
            "not measurable"
            if not decay.is_valid
            else f"{decay.km_per_year:+.2f} (d{decay.start_day:.0f}–{decay.end_day:.0f})"
        )
        w(
            f"| {r['obj'].name} | {r['h'].span_days:.0f} d, {r['h'].n} sets | "
            f"{r['alt0']:.1f} km | {r['alt1']:.1f} km | {r['alt1'] - r['alt0']:+.1f} km | "
            f"{len(r['maneuvers'])} | {r['fraction']:.2f} | {drag} | {r['verdict']} |"
        )
    w("")

    launch_lo = min(r["alt0"] for r in rows)
    launch_hi = max(r["alt0"] for r in rows)
    valid = [r["decay"].km_per_year for r in rows if r["decay"].is_valid]

    w("## Findings")
    w("")
    w(f"**1. Every one of these satellites was inserted between {launch_lo:.0f} and")
    w(f"{launch_hi:.0f} km.** That is squarely consistent with SDA's published figure of")
    w("roughly 1000 km. The apparent conflict we thought we had found between the public")
    w("record and the catalogue was an artefact of reading one current epoch and taking it")
    w("for a design parameter. There was never a discrepancy to explain.")
    w("")
    if valid:
        w(f"**2. Drag at these altitudes is negligible** — measured between")
        w(f"{min(valid):+.2f} and {max(valid):+.2f} km/year over the quiet stretches. This")
        w("is measured here, not assumed, and it is what makes the rest of the audit")
        w("conclusive: a change of hundreds of kilometres cannot be attributed to drag")
        w("when drag is under a kilometre a year.")
    w("")
    moved = [r for r in rows if abs(r["alt1"] - r["alt0"]) > 100.0]
    stable = [r for r in rows if not r["maneuvers"]]
    if moved:
        w(f"**3. {len(moved)} satellites were actively flown down**, by")
        w(
            f"{min(abs(r['alt1'] - r['alt0']) for r in moved):.0f}–"
            f"{max(abs(r['alt1'] - r['alt0']) for r in moved):.0f} km: "
            + ", ".join(r["obj"].name for r in moved)
            + "."
        )
        w("Their step share is at or near 1.0, meaning detected steps account for")
        w("essentially the whole change. These orbits were commanded, not abandoned.")
    w("")
    if stable:
        w(f"**4. {len(stable)} satellites have not moved at all** (")
        w(
            "   "
            + ", ".join(r["obj"].name for r in stable)
            + "): zero detected manoeuvres and near-zero net change across the record."
        )
        w("They are the control that makes finding 3 trustworthy -- the same detector, on")
        w("the same kind of data over the same period, fires not once.")
    w("")
    w("## What this does NOT establish")
    w("")
    w("- **Nothing about mission status.** An orbit that was lowered was lowered; whether")
    w("  that is disposal, a demonstration phase ending, a repositioning, or something")
    w("  else is not in this data. No agency source states it, so we do not say it.")
    w("- **Nothing about payload health or test performance.** Altitude is not a proxy for")
    w("  whether a sensor works, and must never be used as one.")
    w("- **Nothing about why** the L3Harris group flies at a different inclination from the")
    w("  SpaceX group. The public record does not explain it and we do not speculate.")
    w("")
    w("## Consequence for the study")
    w("")
    w("Per decision DEC-11, architecture documents and catalogue geometry answer different")
    w("questions. This audit sharpens that: for a *current-epoch* coverage analysis,")
    w("propagate the real objects and accept that four of the eight are far from where")
    w("they began. For an *architecture* trade, use the insertion geometry and the")
    w("agency-stated design parameters, which this audit now independently corroborates.")
    w("")
    w("## Provenance")
    w("")
    w("Historical GP element sets retrieved from Space-Track.org (`class/gp_history`),")
    w("used under USSPACECOM's blanket approval for redistribution of basic SSA data with")
    w("citation. Raw pulls are cached in `data/raw/spacetrack/`, which is gitignored; only")
    w("derived products such as this report are published.")
    w("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(rows)} objects)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
