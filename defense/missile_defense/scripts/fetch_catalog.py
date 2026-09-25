"""Pull and cache the public orbital elements we seed the simulation with (task S-02).

    python scripts/fetch_catalog.py            # refresh anything older than 12 h
    python scripts/fetch_catalog.py --force    # refetch everything
    python scripts/fetch_catalog.py --report   # print the cache, fetch nothing

Everything retrieved here is publicly catalogued basic SSA data. USSPACECOM grants blanket
approval to redistribute it with citation; per the repo data policy the raw cache stays out
of any public repository and only derived products are published.
"""

from __future__ import annotations

import argparse
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mwsim import catalog, propagate, registry  # noqa: E402


def _print_table(records: dict[int, catalog.OmmRecord]) -> None:
    header = f"{'NORAD':>6}  {'layer':<10} {'name':<26} {'epoch':<20} {'age':>8}  {'rev/day':>8}  {'incl':>7}"
    print(header)
    print("-" * len(header))
    for obj in registry.ALL:
        record = records.get(obj.norad_id)
        if record is None:
            print(f"{obj.norad_id:>6}  {obj.layer:<10} {obj.name:<26} {'-- not retrieved --':<20}")
            continue
        sat = propagate.satrec_from_omm(record)
        rate = propagate.revs_per_day({obj.norad_id: sat})[obj.norad_id]
        incl = propagate.inclination_deg({obj.norad_id: sat})[obj.norad_id]
        age_days = record.age.total_seconds() / 86400.0
        print(
            f"{obj.norad_id:>6}  {obj.layer:<10} {obj.name:<26} "
            f"{record.epoch.strftime('%Y-%m-%d %H:%M'):<20} {age_days:>7.1f}d  "
            f"{rate:>8.4f}  {incl:>6.2f}d"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="refetch regardless of cache age")
    parser.add_argument("--report", action="store_true", help="print the cache without fetching")
    parser.add_argument(
        "--max-age-hours", type=float, default=12.0, help="cache freshness threshold"
    )
    args = parser.parse_args()

    ids = registry.norad_ids(registry.ALL)

    if args.report:
        records = catalog.fetch_many(ids, offline=True)
    else:
        max_age = timedelta(0) if args.force else timedelta(hours=args.max_age_hours)
        print(f"fetching {len(ids)} objects from CelesTrak ...", file=sys.stderr)
        records = catalog.fetch_many(ids, max_age=max_age)

    _print_table(records)

    missing = [i for i in ids if i not in records]
    print()
    print(f"{len(records)}/{len(ids)} objects available; cache at {catalog.OMM_CACHE}")
    if missing:
        names = ", ".join(f"{registry.by_id(i).name} ({i})" for i in missing)
        print(f"MISSING: {names}", file=sys.stderr)
        # Not an error: a satellite can decay or be renumbered, and one absent object
        # should not fail an analysis run. The tests assert on what is actually needed.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
