"""The Li & Zhang (2000) manoeuvring-target benchmark, transcribed from the paper.

Primary source: X. R. Li and Y. M. Zhang, "Multiple-Model Estimation with Variable
Structure — Part V: Likely-Model Set Algorithm", *IEEE Transactions on Aerospace and
Electronic Systems* **36**(2), April 2000, pp. 448-466. Section VI, pp. 457-462.
Local copy: ``data/raw/literature/li_zhang_2000_lms.pdf``.

## Why this module exists

The variable-structure claim in our baseline ladder rests on a single sentence in the Li &
Jilkov survey — that LMS *"substantially outperforms"* fixed-structure IMM. We had been
measuring that claim against a scenario **we invented**: our own model bank, our own noise,
our own adjacency graph. That is not a replication, and a comparison against an invented
scenario cannot confirm or refute anything about the published result.

This module encodes the experiment the paper actually ran, so the comparison is against
the authors' own design rather than ours.

## What the paper specifies, and what it does not

Everything below is transcribed. Two things the paper never states are marked in
`INFERRED` and must be reported as assumptions wherever results are quoted:

* the sampling period ``T`` — inferred as 1 s from the integer time axis of Figs. 4-7 and
  the 1-160 time periods of Table III;
* the track initialisation — inferred as standard two-point differencing from the first
  two measurements.

Neither affects the LMS-versus-IMM *comparison*, which is what we are testing: both
estimators receive identical initial conditions, so an initialisation error moves both
curves together.

## The model set (equation 28)

Thirteen **second-order nearly-constant-velocity models, each with a specified expected
acceleration** — a quantisation of the acceleration mode space onto a grid: the origin,
an inner ring at ±20 m/s², and an outer ring at ±40 m/s². The paper is emphatic that this
beats the more obvious alternatives:

    "the use of (second-order) nearly constant velocity (CV) models with specified expected
    accelerations led to significantly better results than (third-order) nearly constant
    acceleration (CA) models. Also, poor results would be obtained if the accelerations of
    a model were taken as part of the state."

That is why `mwsim.imm.MotionModel` grew an ``offset``: the acceleration enters as a known
deterministic input, not as an estimated state and not as process noise.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .imm import MotionModel

CITATION = (
    "Li, X. R. & Zhang, Y. M. (2000), 'Multiple-Model Estimation with Variable Structure "
    "- Part V: Likely-Model Set Algorithm', IEEE T-AES 36(2), 448-466."
)

# -- the model set, equation (28), m/s^2 -----------------------------------

MODEL_ACCELERATIONS = np.array(
    [
        [0.0, 0.0],      # m1  origin
        [20.0, 0.0],     # m2  inner ring
        [0.0, 20.0],     # m3
        [-20.0, 0.0],    # m4
        [0.0, -20.0],    # m5
        [20.0, 20.0],    # m6  inner diagonals
        [-20.0, 20.0],   # m7
        [-20.0, -20.0],  # m8
        [20.0, -20.0],   # m9
        [40.0, 0.0],     # m10 outer ring
        [0.0, 40.0],     # m11
        [-40.0, 0.0],    # m12
        [0.0, -40.0],    # m13
    ]
)
N_MODELS = len(MODEL_ACCELERATIONS)

# -- adjacency index matrices, equations (31) and (32) ---------------------
#
# The paper's own convention, quoted: "the ith column lists all models that are adjacent
# from model m_i, including m_i itself. The repetitions of the same numbers in a given
# column is made such that a rectangular matrix, rather than a ragged two-dimensional
# array, is obtained." One-based, as printed.

OMEGA_A = np.array(
    [
        [1, 1, 1, 1, 1, 2, 3, 4, 5, 2, 3, 4, 5],
        [2, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
        [3, 9, 6, 7, 8, 3, 4, 5, 2, 10, 11, 12, 13],
        [4, 10, 11, 12, 13, 6, 7, 8, 9, 10, 11, 12, 13],
        [5, 6, 7, 8, 9, 6, 7, 8, 9, 10, 11, 12, 13],
    ]
)

OMEGA_B = np.array(
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3, 4, 5],
        [2, 2, 3, 4, 5, 2, 3, 4, 5, 9, 6, 7, 8],
        [3, 5, 2, 3, 4, 10, 11, 12, 13, 10, 11, 12, 13],
        [4, 9, 6, 7, 8, 6, 7, 8, 9, 6, 7, 8, 9],
        [5, 10, 11, 12, 13, 11, 12, 13, 10, 10, 11, 12, 13],
        [6, 6, 7, 8, 9, 3, 4, 5, 2, 10, 11, 12, 13],
        [7, 3, 4, 5, 2, 6, 7, 8, 9, 10, 11, 12, 13],
        [8, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
        [9, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
    ]
)

# -- transition probability matrices, equations (33) and (34) --------------

_A = 1.0 / 120.0
_B = 1.0 / 30.0
PI_A = np.array(
    [
        [116 * _A, _A, _A, _A, _A, 0, 0, 0, 0, 0, 0, 0, 0],
        [0.02, 0.95, 0, 0, 0, 0.01, 0, 0, 0.01, 0.01, 0, 0, 0],
        [0.02, 0, 0.95, 0, 0, 0.01, 0.01, 0, 0, 0, 0.01, 0, 0],
        [0.02, 0, 0, 0.95, 0, 0, 0.01, 0.01, 0, 0, 0, 0.01, 0],
        [0.02, 0, 0, 0, 0.95, 0, 0, 0.01, 0.01, 0, 0, 0, 0.01],
        [0, _B, _B, 0, 0, 28 * _B, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, _B, _B, 0, 0, 28 * _B, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, _B, _B, 0, 0, 28 * _B, 0, 0, 0, 0, 0],
        [0, _B, 0, 0, _B, 0, 0, 0, 28 * _B, 0, 0, 0, 0],
        [0, 0.1, 0, 0, 0, 0, 0, 0, 0, 0.9, 0, 0, 0],
        [0, 0, 0.1, 0, 0, 0, 0, 0, 0, 0, 0.9, 0, 0],
        [0, 0, 0, 0.1, 0, 0, 0, 0, 0, 0, 0, 0.9, 0],
        [0, 0, 0, 0, 0.1, 0, 0, 0, 0, 0, 0, 0, 0.9],
    ]
)

_C = 1.0 / 360.0
_D = 1.0 / 140.0
_E = 1.0 / 180.0
PI_B = np.array(
    [
        [348 * _C, 2 * _C, 2 * _C, 2 * _C, 2 * _C, _C, _C, _C, _C, 0, 0, 0, 0],
        [2 * _D, 0.95, _D, 0, _D, _D, 0, 0, _D, _D, 0, 0, 0],
        [2 * _D, _D, 0.95, _D, 0, _D, _D, 0, 0, 0, _D, 0, 0],
        [2 * _D, 0, _D, 0.95, _D, 0, _D, _D, 0, 0, 0, _D, 0],
        [2 * _D, _D, 0, _D, 0.95, 0, 0, _D, _D, 0, 0, 0, _D],
        [6 * _E, 2 * _E, 2 * _E, 0, 0, 28 * _B, 0, 0, 0, _E, _E, 0, 0],
        [6 * _E, 0, 2 * _E, 2 * _E, 0, 0, 28 * _B, 0, 0, 0, _E, _E, 0],
        [6 * _E, 0, 0, 2 * _E, 2 * _E, 0, 0, 28 * _B, 0, 0, 0, _E, _E],
        [6 * _E, 2 * _E, 0, 0, 2 * _E, 0, 0, 0, 28 * _B, _E, 0, 0, _E],
        [0, 0.05, 0, 0, 0, 0.025, 0, 0, 0.025, 0.9, 0, 0, 0],
        [0, 0, 0.05, 0, 0, 0.025, 0.025, 0, 0, 0, 0.9, 0, 0],
        [0, 0, 0, 0.05, 0, 0, 0.025, 0.025, 0, 0, 0, 0.9, 0],
        [0, 0, 0, 0, 0.05, 0, 0, 0.025, 0.025, 0, 0, 0, 0.9],
    ]
)

# -- noise and thresholds, Section VI.C and Section IV.A -------------------

Q_MATCHED = 0.003 ** 2   # Q^1, for the no-acceleration model m1
Q_OTHER = 0.008 ** 2     # Q^i, i != 1
R_VARIANCE = 1250.0      # R = rI, r = 1250 m^2 per axis

T_UNLIKELY = 1e-4        # t1, "for all examples considered"
T_PRINCIPAL = 0.3        # t2
K_FLOOR = {"A": 5, "B": 9}          # minimum likely-model-set size
INITIAL_ACTIVE = {"A": 5, "B": 9}   # m1..m5 at 1/5, or m1..m9 at 1/9

MONTE_CARLO_RUNS = 500   # "All simulation results presented in this paper are over 500
                         # Monte Carlo runs."

#: Not stated by the paper. See the module docstring.
INFERRED = {
    "T": 1.0,
    "initialisation": "two-point differencing from the first two measurements",
}

# -- Table III, deterministic scenarios ------------------------------------

_PERIODS = [(1, 30), (31, 45), (46, 55), (56, 80), (81, 98),
            (99, 119), (120, 139), (140, 150), (151, 160)]

_SCENARIO_ACCELERATIONS = {
    1: [(0, 0), (18, 22), (2, 37), (0, 0), (25, 2), (-2, 19), (0, -1), (38, -1), (0, 0)],
    2: [(-20, 0), (22, 22), (-22, 22), (0, 0), (30, 2), (-2, 39), (0, -20), (2, 40), (0, 0)],
}

N_STEPS = _PERIODS[-1][1]


def acceleration_sequence(scenario: int) -> np.ndarray:
    """The true acceleration at each step ``k = 1 .. 160``, ``(160, 2)`` m/s^2.

    Scenario 2 is the harder of the two — the paper notes it "has several large jumps in
    system mode", which is precisely the regime where a variable-structure filter has to
    traverse its model graph rather than simply sitting on the right model.
    """
    if scenario not in _SCENARIO_ACCELERATIONS:
        raise ValueError(f"scenario must be 1 or 2, got {scenario}")
    a = np.zeros((N_STEPS, 2))
    for (lo, hi), accel in zip(_PERIODS, _SCENARIO_ACCELERATIONS[scenario]):
        a[lo - 1:hi] = accel
    return a


# -- kinematics -------------------------------------------------------------

#: Position-only measurement of a ``[x, vx, y, vy]`` state.
H = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]])


def measurement_noise(r: float = R_VARIANCE) -> np.ndarray:
    return np.eye(2) * r


def transition(dt: float = 1.0) -> np.ndarray:
    """Constant-velocity state transition for ``[x, vx, y, vy]``."""
    f = np.eye(4)
    f[0, 1] = dt
    f[2, 3] = dt
    return f


def acceleration_input(accel: np.ndarray, dt: float = 1.0) -> np.ndarray:
    """``G a`` for a two-axis acceleration: the deterministic offset over one step."""
    ax, ay = float(accel[0]), float(accel[1])
    half = 0.5 * dt * dt
    return np.array([half * ax, dt * ax, half * ay, dt * ay])


def build_models(
    dt: float = 1.0, q_matched: float = Q_MATCHED, q_other: float = Q_OTHER
) -> list[MotionModel]:
    """The thirteen models of equation (28) as an IMM bank.

    Each is a nearly-constant-velocity model carrying its acceleration as a deterministic
    input. ``Q^1`` differs from the rest exactly as the paper specifies; both are small,
    because the *true* process noise was set to zero and the model bank — not the process
    noise — is what absorbs manoeuvres.
    """
    f = transition(dt)
    models = []
    for i, accel in enumerate(MODEL_ACCELERATIONS):
        q = (q_matched if i == 0 else q_other) * np.eye(4)
        models.append(
            MotionModel(
                name=f"m{i + 1}",
                transition=f,
                process_noise=q,
                offset=acceleration_input(accel, dt),
            )
        )
    return models


def adjacency(omega: np.ndarray, n_models: int = N_MODELS) -> np.ndarray:
    """Boolean ``(n, n)`` graph from a printed adjacency *index* matrix.

    ``result[i, j]`` is True when model ``j`` is adjacent **from** model ``i`` — i.e. when
    a switch from ``i`` to ``j`` is legitimate in one step. The paper's ``Omega`` stores
    this column-wise and one-based, with padding repeats; both are undone here.
    """
    out = np.zeros((n_models, n_models), dtype=bool)
    for i in range(omega.shape[1]):
        out[i, omega[:, i] - 1] = True
    return out


ADJACENCY_A = adjacency(OMEGA_A)
ADJACENCY_B = adjacency(OMEGA_B)

TOPOLOGIES = {
    "A": {"pi": PI_A, "adjacency": ADJACENCY_A, "k_floor": 5, "n_initial": 5},
    "B": {"pi": PI_B, "adjacency": ADJACENCY_B, "k_floor": 9, "n_initial": 9},
}


# -- scenario generation ----------------------------------------------------


@dataclass(frozen=True)
class Truth:
    """One realisation of the benchmark: true states, measurements, true mode."""

    states: np.ndarray        # (160, 4) [x, vx, y, vy]
    measurements: np.ndarray  # (160, 2)
    accelerations: np.ndarray  # (160, 2) the true system mode s_k

    @property
    def positions(self) -> np.ndarray:
        return self.states[:, [0, 2]]

    @property
    def velocities(self) -> np.ndarray:
        return self.states[:, [1, 3]]


def simulate(
    accelerations: np.ndarray,
    rng: np.random.Generator,
    dt: float = 1.0,
    r: float = R_VARIANCE,
    initial_state: np.ndarray | None = None,
) -> Truth:
    """Propagate the truth and corrupt it with measurement noise.

    The paper: *"The true process noise covariance was set to zero."* So the only
    randomness in a deterministic scenario is the measurement noise, and a Monte Carlo
    average is an average over measurement realisations alone.

    The initial state is arbitrary and unreported. It does not matter: the models and the
    truth are both linear with state-independent dynamics, and the filter is initialised
    from the measurements, so the estimation error is invariant to where the target starts.
    `tests/test_lz2000.py` asserts that invariance rather than assuming it.
    """
    f = transition(dt)
    x = np.zeros(4) if initial_state is None else np.asarray(initial_state, dtype=float)
    states = np.empty((len(accelerations), 4))
    for k, a in enumerate(accelerations):
        x = f @ x + acceleration_input(a, dt)
        states[k] = x
    noise = rng.normal(scale=np.sqrt(r), size=(len(accelerations), 2))
    return Truth(
        states=states,
        measurements=states[:, [0, 2]] + noise,
        accelerations=np.asarray(accelerations, dtype=float),
    )


def two_point_initialisation(
    measurements: np.ndarray, dt: float = 1.0, r: float = R_VARIANCE
) -> tuple[np.ndarray, np.ndarray]:
    """Standard two-point differencing from the first two measurements.

    Inferred, not transcribed — the paper does not state how tracks were initialised. Both
    estimators under comparison get the identical result, so the choice shifts both curves
    together and cannot manufacture a difference between them.
    """
    z0, z1 = measurements[0], measurements[1]
    mean = np.array([z1[0], (z1[0] - z0[0]) / dt, z1[1], (z1[1] - z0[1]) / dt])
    block = np.array([[r, r / dt], [r / dt, 2.0 * r / (dt * dt)]])
    cov = np.zeros((4, 4))
    cov[:2, :2] = block
    cov[2:, 2:] = block
    return mean, cov


def initial_mode_probabilities(topology: str) -> np.ndarray:
    """Equal mass on the first ``n`` models, zero elsewhere.

    The paper: *"To have a fair comparison, all the MM algorithms used the same initial
    assignment of model probabilities. Each of the models m_i for i = 1,2,3,4,5 in topology
    A and for i = 1,...,9 in topology B, has initial probability of 1/5 and 1/9."*

    The zeros are not permanent for the fixed-structure IMM: mixing through ``Pi`` feeds
    probability into the outer models within a step or two.
    """
    n = TOPOLOGIES[topology]["n_initial"]
    mu = np.zeros(N_MODELS)
    mu[:n] = 1.0 / n
    return mu


# -- the random scenario, equations (29) and (30) --------------------------

TAU_MEAN_AT_MAX = 10.0    # tau-bar_M
TAU_MEAN_AT_ZERO = 30.0   # tau-bar_0
P_MAX = 0.1               # P_M
A_MAX = 37.0              # a_max, m/s^2
SIGMA_THETA = np.pi / 12.0


def random_acceleration_sequence(
    rng: np.random.Generator, n_steps: int = N_STEPS
) -> np.ndarray:
    """A semi-Markov acceleration process, ``(n_steps, 2)`` m/s^2.

    The paper's motivation for including it, which is also ours for reproducing it:

        "The use of such a random test scenario reduces the dependence of the performance
        of an MM algorithm on various artifacts of a scenario. With such a random
        scenario, it is difficult to design an MM algorithm with subtle tricks that are
        effective only for certain scenarios."

    Structure, from equations (29) and (30): the acceleration is a magnitude-and-angle
    pair holding constant for a random sojourn time. Harder manoeuvres are held for less
    time — the mean sojourn falls linearly from 30 steps at zero acceleration to 10 at
    ``a_max``. The next magnitude is zero with probability ``P_0``, maximal with
    probability ``P_M``, and uniform in between; the next heading is uniform if the target
    was coasting and a small perturbation of the current heading if it was not.
    """
    accelerations = np.zeros((n_steps, 2))
    magnitude, theta = 0.0, 0.0  # "the initial acceleration a_1 was set to zero"
    k = 0
    while k < n_steps:
        tau_mean = TAU_MEAN_AT_MAX + (
            (A_MAX - magnitude) / A_MAX
        ) * (TAU_MEAN_AT_ZERO - TAU_MEAN_AT_MAX)
        # Truncated at tau > 0, then "rounded to its nearest integer".
        sojourn = 0
        while sojourn < 1:
            draw = rng.normal(tau_mean, tau_mean / 12.0)
            sojourn = int(round(draw)) if draw > 0 else 0

        end = min(k + sojourn, n_steps)
        accelerations[k:end] = [magnitude * np.cos(theta), magnitude * np.sin(theta)]
        k = end

        p_zero = 0.8 if magnitude == A_MAX else 0.6
        u = rng.random()
        previous = magnitude
        if u < p_zero:
            magnitude = 0.0
        elif u < p_zero + P_MAX:
            magnitude = A_MAX
        else:
            magnitude = rng.uniform(0.0, A_MAX)
        # "uniform over 2*pi if a_k = 0, Gaussian with mean theta_k ... if a_k != 0"
        theta = (
            rng.uniform(0.0, 2.0 * np.pi)
            if previous == 0.0
            else rng.normal(theta, SIGMA_THETA)
        )
    return accelerations
