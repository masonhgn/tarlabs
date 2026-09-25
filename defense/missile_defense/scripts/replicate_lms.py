"""Replicate Table IV of Li & Zhang (2000) and write the result to JSON.

    python scripts/replicate_lms.py [--runs 500] [--out analysis/validation/lms_table_iv.json]

The question this answers is narrow and specific. Our baseline ladder puts
variable-structure IMM on the top rung on the strength of a survey sentence claiming it
*"substantially outperforms"* fixed-structure IMM. Before building on that, we reproduce
the experiment the claim traces back to, using the authors' own model set, adjacency
graphs, transition matrices, noise levels and scenarios (`mwsim.lz2000`).

Three estimators are compared, exactly as the paper's Table IV does:

* **IMM** — fixed structure, all thirteen models running at every step.
* **LMS** — the Likely-Model Set algorithm of Table I, with AND logic.
* **LMS(lambda)** — the same with the forgetting factor of equations (18)-(20).

Reported per case: RMS position and velocity error averaged over the track (the paper's
equations 22-23), the peak of the per-step RMS, and the mean number of mode-matched
filters actually run. The last stands in for the paper's FLOP ratio, which we do not try
to reproduce: it counts the quadratic mixing arithmetic as well as the filters, so it sits
below the filter-count ratio and is not directly comparable.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mwsim import lz2000 as lz  # noqa: E402
from mwsim.imm import IMMFilter  # noqa: E402
from mwsim.lms import LMSFilter  # noqa: E402

#: Table IV, p. 461. RMS position error, metres.
PAPER_TABLE_IV = {
    ("A", "random"): {"IMM": 39.56, "LMS": 40.10, "LMS(lambda)": 37.83},
    ("A", "1"): {"IMM": 37.15, "LMS": 37.58, "LMS(lambda)": 35.85},
    ("A", "2"): {"IMM": 41.52, "LMS": 42.43, "LMS(lambda)": 37.86},
    ("B", "random"): {"IMM": 36.93, "LMS": 36.94, "LMS(lambda)": 35.79},
    ("B", "1"): {"IMM": 35.28, "LMS": 35.30, "LMS(lambda)": 35.29},
    ("B", "2"): {"IMM": 36.47, "LMS": 36.73, "LMS(lambda)": 36.28},
}

DT = lz.INFERRED["T"]


def build(topology: str):
    spec = lz.TOPOLOGIES[topology]
    models = lz.build_models(DT)
    noise = lz.measurement_noise()
    common = dict(
        t_unlikely=lz.T_UNLIKELY, t_principal=lz.T_PRINCIPAL, k_floor=spec["k_floor"]
    )
    return {
        "IMM": IMMFilter(models, spec["pi"], lz.H, noise),
        "LMS": LMSFilter(models, spec["pi"], lz.H, noise, spec["adjacency"], **common),
        "LMS(lambda)": LMSFilter(
            models, spec["pi"], lz.H, noise, spec["adjacency"],
            forgetting=(0.70, 0.30), dt=DT, **common,
        ),
    }


def track(filt, truth, topology: str):
    """Run one estimator over one realisation; returns per-step errors and filter counts.

    Errors start at ``k = 2`` because two measurements are consumed by the two-point
    initialisation. Every estimator gets the identical initial condition.
    """
    z = truth.measurements
    mean, cov = lz.two_point_initialisation(z, DT, lz.R_VARIANCE)
    state = filt.initial_state(mean, cov, lz.initial_mode_probabilities(topology))

    n = len(z)
    position = np.full(n, np.nan)
    velocity = np.full(n, np.nan)
    filters = np.full(n, np.nan)
    for k in range(2, n):
        state = filt.update(state, z[k])
        x, _ = state.combined()
        position[k] = np.hypot(x[0] - truth.states[k, 0], x[2] - truth.states[k, 2])
        velocity[k] = np.hypot(x[1] - truth.states[k, 1], x[3] - truth.states[k, 3])
        filters[k] = getattr(state, "n_filters_run", lz.N_MODELS)
    return position, velocity, filters


def evaluate(topology: str, scenario: str, runs: int) -> dict:
    estimators = build(topology)
    fixed = None if scenario == "random" else lz.acceleration_sequence(int(scenario))

    collected = {name: ([], [], []) for name in estimators}
    for i in range(runs):
        # One seed per run, shared across estimators: the comparison is paired, so every
        # estimator sees the identical truth and the identical measurement noise.
        rng = np.random.default_rng(i)
        accelerations = (
            fixed if fixed is not None else lz.random_acceleration_sequence(rng)
        )
        truth = lz.simulate(accelerations, rng, DT, lz.R_VARIANCE)
        for name, filt in estimators.items():
            p, v, f = track(filt, truth, topology)
            collected[name][0].append(p)
            collected[name][1].append(v)
            collected[name][2].append(f)

    out = {}
    for name, (p, v, f) in collected.items():
        # Equation (22): rms over the Monte Carlo runs at each k. Equation (23): the
        # average of those over the track.
        # Drop the two steps consumed by initialisation rather than nan-averaging them.
        p = np.asarray(p)[:, 2:]
        v = np.asarray(v)[:, 2:]
        f = np.asarray(f)[:, 2:]
        rms_p = np.sqrt(np.mean(np.square(p), axis=0))
        rms_v = np.sqrt(np.mean(np.square(v), axis=0))
        out[name] = {
            "RMSPE": float(np.mean(rms_p)),
            "RMSVE": float(np.mean(rms_v)),
            "MAXPE": float(np.max(rms_p)),
            "MAXVE": float(np.max(rms_v)),
            "filters_per_step": float(np.mean(f)),
            "paper_RMSPE": PAPER_TABLE_IV[(topology, scenario)][name],
        }
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=lz.MONTE_CARLO_RUNS)
    parser.add_argument(
        "--out", type=Path,
        default=Path(__file__).resolve().parent.parent
        / "analysis" / "validation" / "lms_table_iv.json",
    )
    args = parser.parse_args()

    print(f"{lz.CITATION}\n")
    print(f"Monte Carlo runs: {args.runs} (paper: {lz.MONTE_CARLO_RUNS})")
    print(f"Inferred, not transcribed: {lz.INFERRED}\n")
    header = (
        f"{'case':<20}{'estimator':<14}{'RMSPE':>8}{'paper':>8}{'delta':>8}"
        f"{'vs IMM':>9}{'paper':>9}{'filters':>9}"
    )
    print(header)
    print("-" * len(header))

    results = {}
    for topology in ("A", "B"):
        for scenario in ("random", "1", "2"):
            case = evaluate(topology, scenario, args.runs)
            results[f"{topology}/{scenario}"] = case
            reference = PAPER_TABLE_IV[(topology, scenario)]
            label = f"topology {topology}, {scenario}"
            for name in ("IMM", "LMS", "LMS(lambda)"):
                d = case[name]
                delta = 100.0 * (d["RMSPE"] / d["paper_RMSPE"] - 1.0)
                print(
                    f"{label:<20}{name:<14}{d['RMSPE']:>8.2f}{d['paper_RMSPE']:>8.2f}"
                    f"{delta:>7.1f}%{d['RMSPE'] / case['IMM']['RMSPE']:>9.4f}"
                    f"{reference[name] / reference['IMM']:>9.4f}"
                    f"{d['filters_per_step']:>9.2f}"
                )
                label = ""
            print()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(
            {
                "source": lz.CITATION,
                "table": "IV",
                "monte_carlo_runs": args.runs,
                "inferred_parameters": lz.INFERRED,
                "results": results,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"written: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
