"""Conceptual vortex-breakdown / high-angle validity sensitivity model.

Scope and honesty statement (read before use)
----------------------------------------------
This module does NOT predict vortex breakdown. It provides a transparent,
deliberately low-order SENSITIVITY model for how the M2 Polhamus-style
vortex-lift contribution (and the M3 drag/L-D built on it) would change if
the leading-edge vortex loses some of its lift-augmenting effectiveness
above an assumed, user-declared onset angle. Every input to this model
(onset angle, transition width, retained effectiveness) is an explicit,
illustrative sensitivity PARAMETER -- never a validated prediction for the
generic wing used in this project.

Source audit
------------
- E. C. Polhamus, NASA TN D-3767 (1966) and NASA TN D-4739 (1968) remain the
  sources for the PRE-breakdown vortex-lift and vortex-drag terms (see
  vortex_lift.py and drag.py). Neither report attempts to predict vortex
  breakdown; both are limited to the "flow reattaches on the upper surface"
  regime and explicitly assume that condition holds.
- W. H. Wentz and D. L. Kohlman, "Vortex Breakdown on Slender Sharp-Edged
  Wings," Journal of Aircraft, Vol. 8, No. 3, 1971 (based on their University
  of Kansas wind-tunnel study, NASA CR-98737, 1969). A systematic schlieren
  study of vortex breakdown position over sharp-edged delta wings with
  leading-edge sweep from 45 deg to 85 deg. Key, directly relevant findings:
    * At low angle of attack the leading-edge vortex bursts far downstream
      of the trailing edge; as alpha increases, the burst (breakdown)
      location moves forward over the wing, eventually reaching the
      trailing edge and then the apex.
    * Increased leading-edge sweep DELAYS breakdown (a given burst location
      is reached at a higher alpha for more highly swept wings).
    * For sweep angles above about 75 deg, the breakdown-location-vs-alpha
      behavior becomes nearly independent of sweep.
    * Breakdown location is far more sensitive to planform changes near the
      wing apex than to changes near the trailing edge.
  This establishes that breakdown onset depends strongly on PLANFORM
  (sweep, apex shape) and ANGLE OF ATTACK.
- K. D. Visser and R. C. Nelson (NASA-sponsored study), "An experimental
  analysis of critical factors involved in the breakdown process of
  leading-edge vortex flows" (NASA CR/NTRS 19910014797). Crosswire
  measurements over 70 deg and 75 deg delta wings identify the vortex's own
  circulation and accompanying pressure field (which grow with angle of
  attack) as the dominant factors controlling the onset of breakdown --
  i.e. breakdown is governed by the internal vortex-core flow, not by
  boundary-layer separation from the trailing edge.
- Related NASA vortex-breakdown literature (e.g. NTRS 19920003799,
  "Breaking down the delta wing vortex: The role of vorticity in the
  breakdown process") reinforces that breakdown is an internal
  hydrodynamic-instability process of the concentrated vortex core: an
  adverse pressure gradient along the vortex axis causes a rapid expansion
  of the core (a "bubble"- or "spiral"-type disruption) with a large,
  localized loss of the swirl velocity and the associated upper-surface
  suction -- a fundamentally different mechanism from classical 2-D
  trailing-edge/boundary-layer stall, which is a loss of attached flow on
  the aft portion of an airfoil surface as the adverse pressure gradient
  there overcomes the boundary layer.

What this source audit establishes for Milestone 4
    1. Vortex breakdown is a distinct physical phenomenon from ordinary
       2-D airfoil (trailing-edge/boundary-layer) stall: it is an
       axial-flow instability of the concentrated leading-edge vortex core
       itself, not a separation of the surface boundary layer.
    2. Its onset location/angle depends strongly on planform (especially
       sweep and apex geometry) and on angle of attack, with some studies
       also reporting Reynolds-number sensitivity of secondary-vortex and
       transition behavior even where the primary breakdown location was
       comparatively insensitive to Reynolds number in the range tested.
    3. None of the cited studies characterize the SPECIFIC generic,
       illustrative wing used in this project (this project's geometry was
       never wind-tunnel- or CFD-tested; see geometry.py), so this
       repository has no validated, geometry/Re/Mach-specific data from
       which to derive an exact breakdown-onset angle for its own wing.
    4. Therefore Milestone 4 implements a SENSITIVITY / high-angle-validity
       LIMITING model -- not a predictive breakdown model. Every onset
       angle used below is explicitly labeled an "assumed breakdown onset"
       or a "breakdown-onset sensitivity case," never a prediction.

Model architecture
-------------------
The pre-breakdown M1-M3 model is preserved EXACTLY and is not modified by
this module. A smooth, monotonically non-increasing effectiveness factor
f_b(alpha) in (0, 1] multiplies the M2 vortex-lift term only:

    C_L,vortex,effective(alpha) = C_L,vortex,pre(alpha) * f_b(alpha)
    C_L,total,effective(alpha)  = C_L,attached(alpha) + C_L,vortex,effective(alpha)

f_b is a tanh-based smoothstep, parameterized by an assumed onset angle
alpha_b, a transition width Delta_alpha, and a retained-effectiveness
fraction f_post (the fraction of the pre-breakdown vortex lift assumed
still available well above the transition):

    f_b(alpha) = f_post + (1 - f_post) * 0.5 * (1 - tanh((alpha - alpha_b) / w)),
    w = Delta_alpha / 2

This is C-infinity smooth (no discontinuity or kink at any point), strictly
decreasing in alpha, f_b -> 1 as alpha -> -infinity (i.e. f_b = 1 to
floating-point precision well below alpha_b), and f_b -> f_post as
alpha -> +infinity. No stall spike, oscillation, or hard clip is used.

Default illustrative parameters (NOT predictions; see source audit above):
    alpha_b = 20 deg   -- qualitatively consistent with the Wentz-Kohlman
                          finding that, for sharply-swept (60-70 deg range)
                          sharp-edged delta wings, the vortex burst location
                          begins moving onto the wing (from far downstream)
                          in roughly this angle-of-attack region; NOT a
                          quantitative reproduction of their data for this
                          project's specific generic wing.
    Delta_alpha = 4 deg -- illustrative transition width.
    f_post = 0.45       -- illustrative retained-effectiveness fraction,
                          within the 0.3-0.6 conceptual range.

Drag treatment
--------------
Per the M3 vortex-drag relation (drag.py), C_D,vortex = C_L,vortex*tan(alpha)
is itself a resolution of the vortex LIFT force; this project therefore
applies the same effectiveness factor to that resolved force rather than
inventing a separate post-breakdown drag polar:

    C_D,vortex,effective(alpha) = C_L,vortex,effective(alpha) * tan(alpha)
    C_D,total,effective(alpha)  = C_D0 + C_Di,attached(alpha) + C_D,vortex,effective(alpha)

C_Di,attached and C_D0 are UNCHANGED from drag.py.

No stall model, no post-breakdown drag polar, and no separated-flow drag
augmentation is claimed. This module only asks what happens to the
EXISTING reduced-order lift/drag model if vortex effectiveness degrades
above an assumed, uncertain onset -- it does not claim to model
separated-flow aerodynamics accurately.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import NamedTuple

import numpy as np
from numpy.typing import NDArray

from .attached_flow import A0_THIN_AIRFOIL, attached_flow_CL
from .drag import CD0_DEFAULT, attached_induced_drag_coefficient
from .vortex_lift import KV_REFERENCE, SWEEP_REFERENCE_RAD, vortex_lift_coefficient

#: Illustrative default assumed breakdown-onset angle [rad] (20 deg). See
#: module docstring: qualitatively motivated by Wentz & Kohlman (1971), NOT
#: a validated prediction for this project's generic wing.
ALPHA_B_DEFAULT_RAD = math.radians(20.0)

#: Illustrative default transition width [rad] (4 deg).
TRANSITION_WIDTH_DEFAULT_RAD = math.radians(4.0)

#: Illustrative default retained vortex-effectiveness fraction well above
#: the transition (within the declared 0.3-0.6 conceptual range).
F_POST_DEFAULT = 0.45

#: Angle of attack [deg] beyond which tan(alpha) starts to diverge badly
#: enough that the drag model should not be trusted even formally (same
#: bound as drag.py).
_MAX_SANE_ALPHA_RAD = math.radians(89.0)


@dataclass(frozen=True)
class BreakdownParameters:
    """Explicit, illustrative parameters of the vortex-effectiveness sensitivity model.

    All three parameters are ASSUMED sensitivity inputs, not measured or
    validated quantities for this project's generic wing (see module
    docstring's source audit).
    """

    alpha_b_rad: float = ALPHA_B_DEFAULT_RAD
    transition_width_rad: float = TRANSITION_WIDTH_DEFAULT_RAD
    f_post: float = F_POST_DEFAULT

    def __post_init__(self) -> None:
        if not math.isfinite(self.alpha_b_rad) or not (0.0 < self.alpha_b_rad < _MAX_SANE_ALPHA_RAD):
            raise ValueError(
                f"alpha_b_rad must be finite and within (0, 89 deg) in radians, got {self.alpha_b_rad!r}"
            )
        if not math.isfinite(self.transition_width_rad) or self.transition_width_rad <= 0.0:
            raise ValueError(
                f"transition_width_rad must be positive and finite, got {self.transition_width_rad!r}"
            )
        if not math.isfinite(self.f_post) or not (0.0 < self.f_post <= 1.0):
            raise ValueError(f"f_post must be finite and within (0, 1], got {self.f_post!r}")


DEFAULT_BREAKDOWN_PARAMS = BreakdownParameters()


def _validate_alpha(alpha_rad) -> None:
    arr = np.asarray(alpha_rad, dtype=float)
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"alpha_rad must be finite, got {alpha_rad!r}")
    if np.any(np.abs(arr) >= _MAX_SANE_ALPHA_RAD):
        raise ValueError(
            "alpha_rad must be within (-89 deg, 89 deg) for this reduced-order model, "
            f"got {alpha_rad!r}"
        )


def _to_scalar_or_array(alpha_like, result):
    if isinstance(alpha_like, (int, float)) and not isinstance(alpha_like, bool):
        return float(result)
    return result


def vortex_effectiveness(alpha_rad, params: BreakdownParameters = DEFAULT_BREAKDOWN_PARAMS):
    """Smooth vortex-lift effectiveness factor f_b(alpha) in (0, 1].

        f_b(alpha) = f_post + (1 - f_post) * 0.5 * (1 - tanh((alpha - alpha_b) / w))
        w = transition_width_rad / 2

    f_b == 1 well below alpha_b, decreases smoothly and monotonically
    through the transition region, and approaches f_post well above it. No
    discontinuity, oscillation, or hard clip.
    """
    _validate_alpha(alpha_rad)
    alpha_arr = np.asarray(alpha_rad, dtype=float)
    w = params.transition_width_rad / 2.0
    f_b = params.f_post + (1.0 - params.f_post) * 0.5 * (1.0 - np.tanh((alpha_arr - params.alpha_b_rad) / w))
    return _to_scalar_or_array(alpha_rad, f_b)


def effective_vortex_lift_coefficient(
    alpha_rad,
    sweep_rad: float,
    params: BreakdownParameters = DEFAULT_BREAKDOWN_PARAMS,
    kv_ref: float = KV_REFERENCE,
    sweep_ref_rad: float = SWEEP_REFERENCE_RAD,
):
    """C_L,vortex,effective(alpha) = C_L,vortex,pre(alpha) * f_b(alpha).

    Reduces EXACTLY to the unmodified M2 vortex-lift term wherever
    f_b(alpha) == 1 (i.e. well below alpha_b).
    """
    _validate_alpha(alpha_rad)
    cl_vortex_pre = np.asarray(
        vortex_lift_coefficient(alpha_rad, sweep_rad, kv_ref, sweep_ref_rad), dtype=float
    )
    f_b = np.asarray(vortex_effectiveness(alpha_rad, params), dtype=float)
    result = cl_vortex_pre * f_b
    return _to_scalar_or_array(alpha_rad, result)


class BreakdownAerodynamics(NamedTuple):
    """Full breakdown-limited aerodynamic breakdown (pun intended) at a given alpha."""

    f_b: "float | NDArray[np.floating]"
    cl_attached: "float | NDArray[np.floating]"
    cl_vortex_pre: "float | NDArray[np.floating]"
    cl_vortex_effective: "float | NDArray[np.floating]"
    cl_total: "float | NDArray[np.floating]"
    cd0: float
    cdi_attached: "float | NDArray[np.floating]"
    cd_vortex_effective: "float | NDArray[np.floating]"
    cd_total: "float | NDArray[np.floating]"
    lift_to_drag: "float | NDArray[np.floating]"


def post_breakdown_drag_components(
    alpha_rad,
    aspect_ratio: float,
    e: float,
    sweep_rad: float,
    params: BreakdownParameters = DEFAULT_BREAKDOWN_PARAMS,
    cd0: float = CD0_DEFAULT,
    a0: float = A0_THIN_AIRFOIL,
    kv_ref: float = KV_REFERENCE,
    sweep_ref_rad: float = SWEEP_REFERENCE_RAD,
):
    """(cd0, cdi_attached, cd_vortex_effective, cd_total) using the effective
    vortex lift in place of the pre-breakdown M3 vortex-lift term.

        C_D,vortex,effective = C_L,vortex,effective * tan(alpha)
        C_D,total = C_D0 + C_Di,attached + C_D,vortex,effective

    C_Di,attached and C_D0 are UNCHANGED from drag.py.
    """
    if not math.isfinite(cd0) or cd0 < 0.0:
        raise ValueError(f"C_D0 must be non-negative and finite, got {cd0!r}")
    _validate_alpha(alpha_rad)
    alpha_arr = np.asarray(alpha_rad, dtype=float)
    cdi_attached = attached_induced_drag_coefficient(alpha_rad, aspect_ratio, e, a0)
    cl_vortex_eff = np.asarray(
        effective_vortex_lift_coefficient(alpha_rad, sweep_rad, params, kv_ref, sweep_ref_rad), dtype=float
    )
    cd_vortex_eff = cl_vortex_eff * np.tan(alpha_arr)
    cd_total = cd0 + np.asarray(cdi_attached) + cd_vortex_eff
    return (
        cd0,
        cdi_attached,
        _to_scalar_or_array(alpha_rad, cd_vortex_eff),
        _to_scalar_or_array(alpha_rad, cd_total),
    )


def post_breakdown_aerodynamics(
    alpha_rad,
    aspect_ratio: float,
    e: float,
    sweep_rad: float,
    params: BreakdownParameters = DEFAULT_BREAKDOWN_PARAMS,
    cd0: float = CD0_DEFAULT,
    a0: float = A0_THIN_AIRFOIL,
    kv_ref: float = KV_REFERENCE,
    sweep_ref_rad: float = SWEEP_REFERENCE_RAD,
) -> BreakdownAerodynamics:
    """Full breakdown-limited aerodynamic bundle: f_b, every C_L/C_D component, and L/D.

    L/D is 0.0 at alpha = 0 (by the same convention as drag.lift_to_drag_ratio)
    and is otherwise C_L,total / C_D,total.
    """
    _validate_alpha(alpha_rad)
    f_b = vortex_effectiveness(alpha_rad, params)
    cl_attached = attached_flow_CL(alpha_rad, aspect_ratio, e, a0)
    cl_vortex_pre = vortex_lift_coefficient(alpha_rad, sweep_rad, kv_ref, sweep_ref_rad)
    cl_vortex_eff = effective_vortex_lift_coefficient(alpha_rad, sweep_rad, params, kv_ref, sweep_ref_rad)
    cl_total = np.asarray(cl_attached, dtype=float) + np.asarray(cl_vortex_eff, dtype=float)

    cd0_out, cdi_attached, cd_vortex_eff, cd_total = post_breakdown_drag_components(
        alpha_rad, aspect_ratio, e, sweep_rad, params, cd0, a0, kv_ref, sweep_ref_rad
    )
    cd_total_arr = np.asarray(cd_total, dtype=float)

    zero_cl = cl_total == 0.0
    ld = np.zeros_like(cl_total, dtype=float)
    nonzero = ~zero_cl
    with np.errstate(invalid="ignore", divide="ignore"):
        ld[nonzero] = cl_total[nonzero] / cd_total_arr[nonzero]

    return BreakdownAerodynamics(
        f_b=f_b,
        cl_attached=cl_attached,
        cl_vortex_pre=cl_vortex_pre,
        cl_vortex_effective=cl_vortex_eff,
        cl_total=_to_scalar_or_array(alpha_rad, cl_total),
        cd0=cd0_out,
        cdi_attached=cdi_attached,
        cd_vortex_effective=cd_vortex_eff,
        cd_total=cd_total,
        lift_to_drag=_to_scalar_or_array(alpha_rad, ld),
    )


# ----------------------------------------------------------------------
# Conceptual usable-AoA region (predeclared rule; see DESIGN.md for the
# rationale, written BEFORE the resulting envelope was computed)
# ----------------------------------------------------------------------

#: Predeclared rule, part 1: vortex effectiveness must remain at or above
#: this fraction of its unbroken (f_b=1) value.
USABLE_MIN_EFFECTIVENESS = 0.9

#: Predeclared rule, part 2: breakdown-limited L/D must remain at or above
#: this fraction of the pre-breakdown (M3) reference L/D. The reference is
#: the best-sampled pre-breakdown L/D within the original M1-M3 domain
#: (alpha in [0, 25] deg), NOT the breakdown-limited curve's own maximum.
USABLE_MIN_LD_FRACTION = 0.9

#: Predeclared rule, part 3: the conceptual usable region never extends
#: beyond the original M1-M3 declared validity domain, regardless of what
#: the breakdown model alone would suggest.
USABLE_MAX_ALPHA_RAD = math.radians(25.0)


def usable_alpha_limit(
    aspect_ratio: float,
    e: float,
    sweep_rad: float,
    ld_reference: float,
    params: BreakdownParameters = DEFAULT_BREAKDOWN_PARAMS,
    cd0: float = CD0_DEFAULT,
    a0: float = A0_THIN_AIRFOIL,
    kv_ref: float = KV_REFERENCE,
    sweep_ref_rad: float = SWEEP_REFERENCE_RAD,
    n_grid: int = 2501,
) -> float:
    """Upper edge [rad] of the conceptual usable-AoA region (a "pre-breakdown
    operating region", NOT a "safe flight envelope" or "stall boundary").

    Predeclared rule (see DESIGN.md Sec. 12 for the rationale, written
    before this function's output was inspected): the region is
    alpha in [0, alpha_upper] such that, for every alpha in that interval,
    ALL of the following hold:

        (a) vortex effectiveness f_b(alpha) >= USABLE_MIN_EFFECTIVENESS,
        (b) for alpha at or beyond the breakdown-limited L/D curve's own
            peak (i.e. only on its naturally-descending branch -- L/D
            rising from exactly 0 at alpha=0 is not "degradation" and is
            never penalized): L/D(alpha) >= USABLE_MIN_LD_FRACTION * ld_reference,
        (c) alpha <= USABLE_MAX_ALPHA_RAD (the original M1-M3 domain).

    ``ld_reference`` must be supplied by the caller (typically the
    pre-breakdown/M3 best-sampled L/D over [0, 25] deg) so that this
    function does not silently redefine its own reference after the fact.

    Returns the upper edge alpha_upper [rad] via a fine grid search over
    [0, USABLE_MAX_ALPHA_RAD]; if condition (a) already fails at alpha=0
    (should not occur for any reasonable parameter choice), returns 0.0.
    """
    if not math.isfinite(ld_reference) or ld_reference <= 0.0:
        raise ValueError(f"ld_reference must be positive and finite, got {ld_reference!r}")
    if n_grid < 2:
        raise ValueError(f"n_grid must be >= 2, got {n_grid!r}")

    alphas = np.linspace(0.0, USABLE_MAX_ALPHA_RAD, n_grid)
    f_b = np.asarray(vortex_effectiveness(alphas, params), dtype=float)
    aero = post_breakdown_aerodynamics(alphas, aspect_ratio, e, sweep_rad, params, cd0, a0, kv_ref, sweep_ref_rad)
    ld = np.asarray(aero.lift_to_drag, dtype=float)

    peak_idx = int(np.argmax(ld))
    ld_ok = np.ones_like(ld, dtype=bool)
    ld_ok[peak_idx:] = ld[peak_idx:] >= USABLE_MIN_LD_FRACTION * ld_reference

    meets_rule = (f_b >= USABLE_MIN_EFFECTIVENESS) & ld_ok
    if not meets_rule[0]:
        return 0.0
    # Find the first index (moving up from alpha=0) where the rule fails;
    # the usable region is everything strictly before that.
    violations = np.where(~meets_rule)[0]
    if violations.size == 0:
        return float(alphas[-1])
    first_violation = violations[0]
    return float(alphas[first_violation - 1]) if first_violation > 0 else 0.0
