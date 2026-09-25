"""Access geometry and stereo coverage (task S-05).

Answers, for a target at a given place and time: **which satellites can see it, and is the
geometry good enough to fix its position in three dimensions?**

Three Phase D findings shape this module, and each one changes what gets computed:

**Stereo is scored by achieved convergence angle, not by sensor count (DEC-24).** Two
satellites in view with 5° between them are nearly useless — angles-only position error
scales as 1/sin(α), so at 5° the error is ten times the 90° optimum. Counting them as
"stereo coverage" would score a near-blind constellation identically to a good one. The
optimum is broad, though: 45° costs only 34% over 90°, so the requirement is *enough*
convergence, not ideal geometry.

**Field of regard is the dominant lever, and 120° is near a hard limit (D-09, D-17).** CSIS
found a 91-satellite constellation gives persistent global stereo at 120° FOR and fails
entirely at 110°. Geometry gives a maximum of about 121° for a 45 km target seen from
1,000 km, beyond which the line of sight is tangent to the target's shell.

**A wide field of regard means near-horizontal viewing.** At 120° FOR the target is seen
84° from its own zenith. Attenuation turns out not to matter there (DEC-33), but slant
range and look angle very much do, and both are computed rather than assumed.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import limb_geometry as lg
from . import observability as obs

RE_KM = 6378.137


@dataclass(frozen=True)
class AccessResult:
    """Which satellites see a target, and how well, at one instant."""

    visible: np.ndarray            # (n_sat,) bool
    slant_range_km: np.ndarray     # (n_sat,)
    off_nadir_deg: np.ndarray      # (n_sat,)
    target_zenith_deg: np.ndarray  # (n_sat,)
    convergence_deg: float
    n_visible: int

    @property
    def has_stereo(self) -> bool:
        """At least two sensors in view — necessary but *not* sufficient (DEC-24)."""
        return self.n_visible >= 2


def _unit(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return np.divide(v, n, out=np.zeros_like(v), where=n > 0)


def access(
    satellite_positions_km: np.ndarray,
    target_position_km: np.ndarray,
    *,
    field_of_regard_deg: float = 120.0,
    min_grazing_deg: float = 5.0,
) -> AccessResult:
    """Which satellites can see a target, with the geometry of each look.

    Three conditions must all hold:

    1. **Within the field of regard** — the target lies inside the sensor's cone about nadir.
    2. **Above the local horizon** — the target is on the satellite's side of the Earth.
    3. **Clear of a grazing path** — the line of sight does not skim the limb below
       ``min_grazing_deg``. Rays that clear the surface by only a few kilometres are
       geometrically valid and radiometrically doubtful, and D-08 showed that intuition
       about which rays are blocked is unreliable, so the cut is explicit.
    """
    sats = np.atleast_2d(np.asarray(satellite_positions_km, dtype=float))
    target = np.asarray(target_position_km, dtype=float).reshape(3)

    to_target = target - sats
    slant = np.linalg.norm(to_target, axis=-1)

    # Off-nadir: angle at the satellite between its nadir direction and the target.
    nadir = _unit(-sats)
    los = _unit(to_target)
    cosang = np.clip(np.einsum("ij,ij->i", nadir, los), -1.0, 1.0)
    off_nadir = np.degrees(np.arccos(cosang))

    # Zenith angle at the target, between its local vertical and the satellite.
    up = _unit(np.tile(target, (len(sats), 1)))
    cos_z = np.clip(np.einsum("ij,ij->i", up, -los), -1.0, 1.0)
    zenith = np.degrees(np.arccos(cos_z))

    within_for = off_nadir <= field_of_regard_deg / 2.0

    # Grazing: the closest approach of the sight line to the Earth's centre, clamped to
    # the segment, must clear the surface by the required margin.
    d = target - sats
    denom = np.einsum("ij,ij->i", d, d)
    s = np.divide(-np.einsum("ij,ij->i", sats, d), denom,
                  out=np.zeros(len(sats)), where=denom > 0)
    closest = sats + np.clip(s, 0.0, 1.0)[:, None] * d
    tangent_alt = np.linalg.norm(closest, axis=-1) - RE_KM
    target_alt = float(np.linalg.norm(target)) - RE_KM
    # A ray that reaches the target without dipping more than min_grazing below it.
    clears = tangent_alt >= min(target_alt, 0.0) - 1e-9
    above_horizon = zenith <= 90.0 + np.degrees(np.arccos(np.clip(RE_KM / np.linalg.norm(sats, axis=-1), -1, 1)))

    visible = within_for & clears & above_horizon
    # Grazing-angle cut, expressed at the target: 90 deg zenith is horizontal.
    visible &= zenith <= (90.0 - min_grazing_deg) + 90.0

    conv = (
        obs.convergence_angle_deg(sats[visible], target)
        if visible.sum() >= 2
        else 0.0
    )
    return AccessResult(
        visible=visible,
        slant_range_km=slant,
        off_nadir_deg=off_nadir,
        target_zenith_deg=zenith,
        convergence_deg=float(conv),
        n_visible=int(visible.sum()),
    )


def useful_stereo(
    result: AccessResult,
    *,
    angular_sigma_rad: float,
    required_accuracy_km: float,
) -> bool:
    """Is the geometry good enough to fix the target to the required accuracy?

    **This is the coverage criterion, replacing "two satellites are in view" (DEC-24).**
    It asks the question that matters — can we locate the target well enough — rather than
    the proxy question of how many sensors happen to be looking.
    """
    if result.n_visible < 2:
        return False
    needed = obs.required_convergence_deg(
        float(np.median(result.slant_range_km[result.visible])),
        angular_sigma_rad,
        required_accuracy_km,
    )
    if needed is None:
        return False
    # The dilution curve is symmetric about 90 degrees: position error scales as
    # 1/sin(alpha), so 150 degrees is exactly as good as 30, and 175 is as bad as 5.
    # The adequate band is therefore [needed, 180 - needed] and NOT "anything above
    # needed" — a one-sided test silently accepts the near-antiparallel geometries where
    # the two sight lines are almost collinear again.
    return needed <= result.convergence_deg <= 180.0 - needed


def coverage_over_time(
    satellite_positions_km: np.ndarray,
    target_position_km: np.ndarray,
    *,
    field_of_regard_deg: float = 120.0,
    angular_sigma_rad: float = 50e-6,
    required_accuracy_km: float = 1.0,
    min_grazing_deg: float = 5.0,
) -> dict[str, np.ndarray | float]:
    """Coverage statistics for a fixed target over a propagated constellation.

    ``satellite_positions_km`` is ``(n_sat, n_time, 3)``; the target is fixed in the same
    inertial frame. Reports both the naive sensor count and the useful-stereo fraction, so
    the gap between them is visible rather than hidden — that gap is the whole point of
    DEC-24.
    """
    pos = np.asarray(satellite_positions_km, dtype=float)
    n_time = pos.shape[1]

    n_visible = np.zeros(n_time, dtype=int)
    convergence = np.zeros(n_time)
    useful = np.zeros(n_time, dtype=bool)

    for k in range(n_time):
        r = access(
            pos[:, k, :], target_position_km,
            field_of_regard_deg=field_of_regard_deg,
            min_grazing_deg=min_grazing_deg,
        )
        n_visible[k] = r.n_visible
        convergence[k] = r.convergence_deg
        useful[k] = useful_stereo(
            r, angular_sigma_rad=angular_sigma_rad,
            required_accuracy_km=required_accuracy_km,
        )

    return {
        "n_visible": n_visible,
        "convergence_deg": convergence,
        "useful_stereo": useful,
        "any_coverage_fraction": float((n_visible >= 1).mean()),
        "naive_stereo_fraction": float((n_visible >= 2).mean()),
        "useful_stereo_fraction": float(useful.mean()),
        "mean_visible": float(n_visible.mean()),
    }


def max_field_of_regard_deg(satellite_altitude_km: float, target_altitude_km: float) -> float:
    """Largest usable field of regard before the sight line misses the target's shell.

    Reproduces CSIS's statement that Earth curvature limits field of regard beyond about
    120°: geometry gives 121° for a 45 km target from 1,000 km.
    """
    return 2.0 * lg.max_off_nadir_deg(
        satellite_altitude_km=satellite_altitude_km,
        target_altitude_km=target_altitude_km,
    )
