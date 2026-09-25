"""Pull historical GP element sets from Space-Track (task D-14).

    python scripts/fetch_orbit_history.py            # tracking layer + HBTSS
    python scripts/fetch_orbit_history.py --all      # every registry object
    python scripts/fetch_orbit_history.py --refresh  # ignore the cache

CelesTrak serves only the current element set. Distinguishing a commanded manoeuvre from
secular decay needs the whole series, which is what `gp_history` provides.

Cached under data/raw/spacetrack/, which is gitignored: USSPACECOM's blanket approval
covers redistributing basic SSA data with citation, but our policy is to publish derived
products and never mirror bulk raw pulls.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from mwsim import registry  # noqa: E402
from mwsim.spacetrack import SpaceTrackClient, SpaceTrackError  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="every object in the registry")
    parser.add_argument("--refresh", action="store_true", help="refetch, ignoring the cache")
    args = parser.parse_args()

    if args.all:
        objects = registry.ALL
    else:
        objects = registry.SDA_TRANCHE0_TRACKING + registry.HBTSS

    print(f"pulling gp_history for {len(objects)} objects", file=sys.stderr)

    try:
        with SpaceTrackClient() as client:
            total = 0
            for obj in objects:
                try:
                    records = client.gp_history(obj.norad_id, refresh=args.refresh)
                except SpaceTrackError as exc:
                    print(f"  {obj.name:<16} FAILED: {exc}", file=sys.stderr)
                    continue
                total += len(records)
                span = ""
                if records:
                    span = f"{records[0]['EPOCH'][:10]} .. {records[-1]['EPOCH'][:10]}"
                print(f"  {obj.name:<16} {len(records):>6} records   {span}")
            print(f"\n{total} records total")
    except SpaceTrackError as exc:
        print(f"Space-Track unavailable: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
