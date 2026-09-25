"""Characterise the GOES ABI infrared background (task D-05).

    python scripts/analyze_goes_background.py           # use the cache
    python scripts/analyze_goes_background.py --fetch   # pull fresh frames first

Backs analysis/data/ir_background.md. Needs netCDF4.
"""

from __future__ import annotations

import argparse
import glob
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from mwsim import goes  # noqa: E402

BUCKET = "noaa-goes19"
BAND = "07"
N_FRAMES = 4


def _fetch_recent(n: int = N_FRAMES) -> None:
    """Pull the most recent available mesoscale Band-7 frames.

    Walks back an hour at a time: the current UTC hour is usually incomplete, and a day
    only a few hours old has no later hours at all.
    """
    now = datetime.now(timezone.utc)
    for back in range(0, 12):
        t = now - timedelta(hours=back)
        prefix = (
            f"ABI-L1b-RadM/{t.year}/{t.timetuple().tm_yday:03d}/{t.hour:02d}/"
            f"OR_ABI-L1b-RadM1-M6C{BAND}"
        )
        try:
            keys = goes.list_keys(BUCKET, prefix, max_keys=n)
        except Exception as exc:  # network or listing failure is not fatal
            print(f"  listing failed for {prefix}: {exc}", file=sys.stderr)
            continue
        if len(keys) >= 2:
            for key, size in keys[:n]:
                path = goes.fetch(BUCKET, key)
                print(f"  {size / 1e6:5.2f} MB  {path.name}")
            return
    print("  no frames found in the last 12 hours", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fetch", action="store_true", help="download fresh frames first")
    args = ap.parse_args()

    if args.fetch:
        print(f"fetching Band {BAND} frames from {BUCKET} ...", file=sys.stderr)
        _fetch_recent()

    paths = sorted(glob.glob(str(goes.GOES_CACHE / f"*C{BAND}*.nc")))
    if not paths:
        print("no cached scenes; rerun with --fetch", file=sys.stderr)
        return 1

    scenes = [goes.load_scene(Path(p)) for p in paths]
    s = scenes[0]
    print(f"\n{s.platform} ABI band {s.band_id} @ {s.wavelength_um:.2f} um, "
          f"{s.resolution}, {s.scene_id}")
    print(f"first frame {s.time_coverage_start}, {len(scenes)} frames\n")

    stats = goes.background_statistics(s)
    print("background:")
    print(f"  mean spectral radiance   {stats['mean_radiance_W_m2_sr_um']:8.4f} "
          f"W m-2 sr-1 um-1")
    print(f"  brightness temperature   {stats['tb_min_k']:.1f} - {stats['tb_max_k']:.1f} K "
          f"(mean {stats['tb_mean_k']:.1f}, sd {stats['tb_std_k']:.1f})")
    print(f"  scene variability        {stats['std_over_mean']:8.3f}  (sd/mean radiance)")
    print(f"  BACKGROUND-EQUIVALENT    {stats['background_equivalent_intensity_kW_sr']:8.1f} "
          f"kW/sr  <- target must exceed this to matter in one frame")

    if len(scenes) >= 2:
        floor = goes.differencing_floor(scenes)
        print(f"\ntemporal differencing ({int(floor['n_differences'])} consecutive pairs, "
              f"{int(floor['sigma_multiple'])}-sigma):")
        print(f"  plain sigma              {floor['floor_plain_kW_sr']:8.1f} kW/sr")
        print(f"  robust (MAD) sigma       {floor['floor_robust_kW_sr']:8.1f} kW/sr")
        gain = stats["background_equivalent_intensity_kW_sr"] / floor["floor_robust_kW_sr"]
        print(f"  improvement over single frame: {gain:.0f}x")
        print("\n  Differencing is the enabling step, not an optimisation: a target of tens")
        print("  of kW/sr is invisible against a 159 kW/sr background in one frame and")
        print("  clearly detectable in a difference.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
