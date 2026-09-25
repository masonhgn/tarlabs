"""Measure Tranche 0 plane structure and verify the off-plane drift (task D-02).

    python scripts/analyze_constellation.py

Prints the measured plane clustering and the J2 drift reconciliation that backs
analysis/data/constellation_geometry.md. Needs the OMM cache (scripts/fetch_catalog.py)
and, for the drift check, the Space-Track histories (scripts/fetch_orbit_history.py).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from mwsim import catalog, registry  # noqa: E402
from mwsim import constellation_analysis as ca  # noqa: E402

HISTORY = ROOT / "data" / "raw" / "spacetrack"
#: WILDFIRE 3 shares the 2023-133 launch and plane with BB 3 and BB 4, and never
#: manoeuvred — so it is the natural reference for differential drift.
REFERENCE_NORAD = 57758
DRIFTED = {57760: "BB 3", 57757: "BB 4"}


def _series(norad_id: int):
    path = HISTORY / f"gp_history_{norad_id}.json"
    if not path.exists():
        return None
    rows = []
    for r in json.loads(path.read_text(encoding="utf-8"))["records"]:
        try:
            rows.append(
                (
                    np.datetime64(r["EPOCH"][:19], "s"),
                    float(r["RA_OF_ASC_NODE"]),
                    float(r["SEMIMAJOR_AXIS"]),
                    float(r["INCLINATION"]),
                    float(r["ECCENTRICITY"]),
                )
            )
        except (KeyError, TypeError, ValueError):
            continue
    rows.sort()
    return [np.array(c) for c in zip(*rows)] if rows else None


def main() -> int:
    objects = registry.SDA_TRANCHE0_TRANSPORT + registry.SDA_TRANCHE0_TRACKING
    records = catalog.fetch_many([o.norad_id for o in objects], offline=True)
    if not records:
        print("no cached elements; run scripts/fetch_catalog.py", file=sys.stderr)
        return 1

    sats = []
    for obj in objects:
        rec = records.get(obj.norad_id)
        if rec is None:
            continue
        f = rec.fields
        a = (ca.MU_KM3_S2 / (f["MEAN_MOTION"] * 2 * np.pi / 86400.0) ** 2) ** (1 / 3)
        sats.append((obj.name, f["RA_OF_ASC_NODE"], f["INCLINATION"], a - 6371.0))

    print(f"Measured Tranche 0 plane structure ({len(sats)} objects)\n")
    planes = ca.cluster_planes(sats)
    for i, p in enumerate(planes, 1):
        print(
            f"  plane {i}: n={p.count:2d}  RAAN={p.raan_deg:6.1f}  "
            f"incl={p.inclination_deg:5.2f}  alt={p.mean_altitude_km:6.1f} km  "
            f"spread={p.raan_spread_deg:4.1f}"
        )
        print(f"           {', '.join(p.members)}")
    big = [p for p in planes if p.count > 1 and abs(p.inclination_deg - 81.0) < 1.0]
    if len(big) >= 2:
        sep = abs((big[0].raan_deg - big[1].raan_deg + 180) % 360 - 180)
        print(f"\n  polar plane separation: {sep:.1f} deg "
              f"(an even 2-plane Walker would be 90 deg)")

    ref = _series(REFERENCE_NORAD)
    if ref is None:
        print("\n(no cached histories; skipping the J2 drift check)")
        return 0

    r_ep, r_raan, r_a, r_i, r_e = ref
    print("\nJ2 drift reconciliation against WILDFIRE 3 (never manoeuvred)\n")
    print(f"  {'object':8s} {'day':>6s} {'predicted':>12s} {'observed':>12s} {'residual':>10s}")
    for norad_id, name in DRIFTED.items():
        s = _series(norad_id)
        if s is None:
            continue
        ep, raan, a, inc, ecc = s
        pred = ca.predicted_raan_separation(ep, a, inc, ecc, r_ep, r_a, r_i, r_e)
        days = ((ep - ep[0]) / np.timedelta64(1, "D")).astype(float)
        ref_days = ((r_ep - ep[0]) / np.timedelta64(1, "D")).astype(float)
        obs = np.unwrap(raan, period=360) - np.interp(
            days, ref_days, np.unwrap(r_raan, period=360)
        )
        obs = obs - obs[0]
        for d in (347, 500, 800, 1100):
            k = int(np.argmin(np.abs(days - d)))
            print(f"  {name:8s} {days[k]:6.0f} {pred[k]:+11.2f}° {obs[k]:+11.2f}° "
                  f"{pred[k] - obs[k]:+9.2f}°")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
