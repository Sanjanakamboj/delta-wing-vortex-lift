"""Conceptual reduced-order pitching-moment / center-of-pressure model.

Scope and honesty statement (read before use)
----------------------------------------------
This module answers a narrow, isolated-wing question:

    "How does the nonlinear vortex-lift contribution alter the center of
    pressure and pitching moment of this generic delta wing as angle of
    attack increases?"

It is a conceptual, force-location aerodynamic model ONLY. It does NOT
include a tail, elevator, trim solution, CG sizing, control laws, a
fuselage, propulsion moments, or any dynamic-stability derivative, and it
must never be described as a complete-aircraft stability analysis. Where
this project discusses dC_m/d(alpha) about the chosen reference point, that
is called the wing's "isolated-wing static pitching tendency about the
chosen reference point" -- never "aircraft longitudinal stability."

Source audit
------------
- M. H. Snyder, Jr. and J. E. Lamar, "Application of the Leading-Edge-
  Suction Analogy to Prediction of Longitudinal Load Distribution and
  Pitching Moments for Sharp-Edged Delta Wings," NASA TN D-6994, October
  1972. Directly relevant primary source, extending Polhamus's leading-
  edge-suction analogy (already used for M2/M3) to the CHORDWISE
  (longitudinal) distribution of both the potential-flow and vortex lift,
  and to pitching moment. Key findings used here:
    * They nondimensionalize pitching moment about the HALF-ROOT-CHORD,
      x_ref = c_r/2, and use a reference chord c_bar = (2/3) c_r -- which
      is exactly the analytical MAC of a pure (zero-taper-ratio) triangular
      planform (see geometry.py's mean_aerodynamic_chord, independently
      derived and verified in this project). Both choices are adopted
      directly here: x_ref/c_r = 0.5, c_ref = MAC.
    * For delta wings with aspect ratio <= 2 (this project's representative
      wing has AR = 1.87, squarely in this range), they find that the
      longitudinal (chordwise) load distributions of the potential-flow
      and vortex-lift contributions have SIMILAR SHAPE, with "slightly
      different centroids," and that the vortex-lift longitudinal loading
      grows MORE RAPIDLY with alpha than the potential-flow loading.
    * They report that the vortex-lift contribution "produces a
      stabilizing moment and becomes the larger contributor at the high
      angles of attack" -- i.e. a nose-down-tending pitching increment that
      grows with alpha (in the C_m,alpha < 0 sense used for classical
      static-tendency language), consistent with a vortex-force centroid
      located aft of their x_ref = c_r/2.
    * Neither this report nor Polhamus's own reports assign a single
      universal chordwise fraction to the vortex-lift force location; the
      report's OWN central finding is that it is close to (but not
      identical to) the potential-flow centroid for wings in our AR range.
- R. T. Jones, "Properties of Low-Aspect-Ratio Pointed Wings at Speeds
  Below and Above the Speed of Sound," NACA Report 835, 1946. Foundational
  slender-wing-theory result used here: for a slender, pointed planform,
  sectional lift growth is tied to the local rate of increase of section
  width, with "sections behind the [maximum-width] section developing no
  lift." For a pure triangular (delta) planform, local span (width)
  increases monotonically all the way to the trailing edge (which is where
  the maximum width occurs), so the entire wing lifts, and slender-wing
  theory gives sectional loading dC_N/d(x/c_r) growing linearly in x. This
  project INDEPENDENTLY integrates that linear sectional-loading law (a
  short calculus derivation, not copied from any source) to obtain the
  potential-flow force-location centroid:

    Assume dC_N/d(x_hat) proportional to x_hat, x_hat = x/c_r in [0,1].
    Centroid: x_hat_bar = integral_0^1 x_hat * x_hat dx_hat
                          / integral_0^1 x_hat dx_hat
                        = (1/3) / (1/2) = 2/3

  giving x_attached/c_r = 2/3. This is the classical "two-thirds root
  chord" result frequently cited for slender/delta-wing potential-flow
  aerodynamic centers, reproduced here from first principles rather than
  asserted from memory (see tests/test_pitching_moment.py for the
  standalone numeric integration check of this same calculus result).

What this project adopts as its NOMINAL, explicitly conceptual model
    x_attached/c_r = 2/3   (Jones 1946 slender-wing sectional-loading
                            centroid, derived above)
    x_vortex/c_r   = 2/3   (nominal, EQUAL to x_attached -- directly
                            motivated by Snyder & Lamar's central finding,
                            for AR <= 2, that the two chordwise load
                            distributions have similar shape/centroid)
    x_ref/c_r      = 0.5   (matches the NASA TN D-6994 moment reference)
    c_ref          = MAC = (2/3) c_r  (matches the NASA TN D-6994
                            reference chord, independently derived/verified
                            in geometry.py)
    C_m0           = 0    (symmetric, uncambered conceptual wing; no
                            source justifies a nonzero offset)

Because the source material explicitly states the two centroids are only
"slightly different" (not identical) and that the vortex-lift loading's
centroid effectively shifts (grows faster with alpha) rather than staying
exactly co-located with the potential-flow centroid, x_vortex/c_r is
treated as an EXPLICIT, ILLUSTRATIVE parameter and is varied +/-0.10 in a
dedicated sensitivity study (see scripts/pitching_moment_study.py and
DESIGN.md) rather than being presented as a single validated value. The
qualitative "vortex lift produces a stabilizing [nose-down-tending]
moment" behavior found by Snyder & Lamar is reproduced by this project's
model whenever x_vortex is aft of x_ref, which holds throughout the
sensitivity range explored here (see DESIGN.md for the resulting numbers)
-- this project does not force that conclusion; it falls out of the
adopted, source-motivated nominal locations.

Sign convention (derived, not guessed)
---------------------------------------
x is measured from the wing apex, positive aft (same convention as
geometry.py). Lift L acts upward (positive). Consider the torque of an
upward force L located at x_force about a reference point x_ref: if the
force is AFT of the reference (x_force > x_ref), an upward force there
rotates the nose DOWN about that reference (see-saw intuition -- pushing
up at the back tips the front down). Using the standard aerospace
convention that a NOSE-UP moment about the reference is POSITIVE, this
gives

    M = -L * (x_force - x_ref)

which is negative (nose-down) when x_force > x_ref and L > 0, and positive
(nose-up) when x_force < x_ref and L > 0 -- matching the physical
description above. Dividing by q*S*c_ref gives the coefficient form used
throughout this module:

    C_m = -C_L * (x_force - x_ref) / c_ref

Breakdown coupling
-------------------
This module uses the M4 EFFECTIVE vortex lift, C_L,vortex,effective =
C_L,vortex,pre * f_b(alpha), directly from breakdown.py (never
reimplemented or duplicated here). Vortex breakdown therefore changes
total lift, x_cp, and C_m purely through its existing effect on
C_L,vortex,effective -- there is no separate, independent pitching-moment
breakdown multiplier. Below the M4 transition (f_b == 1 to floating-point
precision), this module's outputs reduce exactly to the pre-breakdown
(M2-consistent) moment model.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import NamedTuple

import numpy as np
from numpy.typing import NDArray

from .attached_flow import A0_THIN_AIRFOIL, attached_flow_CL
from .breakdown import (
    DEFAULT_BREAKDOWN_PARAMS,
    BreakdownParameters,
    effective_vortex_lift_coefficient,
    vortex_effectiveness,
)
from .vortex_lift import KV_REFERENCE, SWEEP_REFERENCE_RAD, vortex_lift_coefficient

#: Nominal potential-flow (attached) force-application location, x/c_r.
#: Derived from R.T. Jones (1946) slender-wing sectional-loading theory --
#: see module docstring for the independent calculus derivation.
X_ATTACHED_HAT_DEFAULT = 2.0 / 3.0

#: Nominal vortex-lift force-application location, x/c_r. Set EQUAL to
#: X_ATTACHED_HAT_DEFAULT as a documented, source-motivated nominal (Snyder
#: & Lamar 1972 find similar chordwise-load-distribution shape/centroid for
#: AR <= 2); varied explicitly in the dedicated sensitivity study.
X_VORTEX_HAT_DEFAULT = 2.0 / 3.0

#: Nominal moment reference point, x_ref/c_r. Matches the NASA TN D-6994
#: convention (moment reference at half the root chord).
X_REF_HAT_DEFAULT = 0.5

#: Nominal reference chord for C_m nondimensionalization, expressed as a
#: fraction of c_r: MAC/c_r = 2/3 for this triangular planform (matches
#: geometry.DeltaWingGeometry.mean_aerodynamic_chord and the NASA TN D-6994
#: reference chord c_bar).
C_REF_HAT_DEFAULT = 2.0 / 3.0

#: Default symmetric-wing zero-lift/offset moment coefficient. No source
#: justifies a nonzero value for this uncambered conceptual wing.
CM0_DEFAULT = 0.0


@dataclass(frozen=True)
class PitchingMomentParameters:
    """Explicit, documented force-location and reference parameters, all as
    fractions of the root chord c_r (dimensionless, so this module never
    needs the absolute wing size).

    See the module docstring for the source-motivated nominal values and
    exactly what is/is not adopted from the literature.
    """

    x_attached_hat: float = X_ATTACHED_HAT_DEFAULT
    x_vortex_hat: float = X_VORTEX_HAT_DEFAULT
    x_ref_hat: float = X_REF_HAT_DEFAULT
    c_ref_hat: float = C_REF_HAT_DEFAULT
    cm0: float = CM0_DEFAULT

    def __post_init__(self) -> None:
        for name in ("x_attached_hat", "x_vortex_hat", "x_ref_hat"):
            value = getattr(self, name)
            if not math.isfinite(value) or not (0.0 <= value <= 1.0):
                raise ValueError(
                    f"{name} must be finite and within [0, 1] (a fraction of the root "
                    f"chord between the apex and trailing edge), got {value!r}"
                )
        if not math.isfinite(self.c_ref_hat) or self.c_ref_hat <= 0.0:
            raise ValueError(f"c_ref_hat must be positive and finite, got {self.c_ref_hat!r}")
        if not math.isfinite(self.cm0):
            raise ValueError(f"cm0 must be finite, got {self.cm0!r}")


DEFAULT_MOMENT_PARAMS = PitchingMomentParameters()


def _to_scalar_or_array(like, result):
    if isinstance(like, (int, float)) and not isinstance(like, bool):
        return float(result)
    return result


def attached_moment_coefficient(cl_attached, params: PitchingMomentParameters = DEFAULT_MOMENT_PARAMS):
    """C_m,attached = -C_L,attached * (x_attached_hat - x_ref_hat) / c_ref_hat.

    See module docstring for the derived sign convention.
    """
    cl_arr = np.asarray(cl_attached, dtype=float)
    result = -cl_arr * (params.x_attached_hat - params.x_ref_hat) / params.c_ref_hat
    return _to_scalar_or_array(cl_attached, result)


def vortex_moment_coefficient(cl_vortex_effective, params: PitchingMomentParameters = DEFAULT_MOMENT_PARAMS):
    """C_m,vortex = -C_L,vortex,effective * (x_vortex_hat - x_ref_hat) / c_ref_hat."""
    cl_arr = np.asarray(cl_vortex_effective, dtype=float)
    result = -cl_arr * (params.x_vortex_hat - params.x_ref_hat) / params.c_ref_hat
    return _to_scalar_or_array(cl_vortex_effective, result)


def total_moment_coefficient(
    cl_attached, cl_vortex_effective, params: PitchingMomentParameters = DEFAULT_MOMENT_PARAMS
):
    """C_m,total = C_m0 + C_m,attached + C_m,vortex."""
    cm_a = np.asarray(attached_moment_coefficient(cl_attached, params), dtype=float)
    cm_v = np.asarray(vortex_moment_coefficient(cl_vortex_effective, params), dtype=float)
    result = params.cm0 + cm_a + cm_v
    return _to_scalar_or_array(cl_attached, result)


def center_of_pressure_hat(
    cl_attached, cl_vortex_effective, params: PitchingMomentParameters = DEFAULT_MOMENT_PARAMS
):
    """Combined center-of-pressure location x_cp/c_r (force-location model, C_m0=0 part only).

        x_cp_hat = (C_L,attached * x_attached_hat + C_L,vortex,eff * x_vortex_hat) / C_L,total

    Undefined (returns NaN) wherever C_L,total == 0 exactly (in particular
    at alpha=0, where both lift contributions are exactly zero) -- no
    center of pressure is fabricated for zero total lift.
    """
    cl_a = np.asarray(cl_attached, dtype=float)
    cl_v = np.asarray(cl_vortex_effective, dtype=float)
    cl_total = cl_a + cl_v

    result = np.full_like(cl_total, np.nan, dtype=float)
    nonzero = cl_total != 0.0
    result[nonzero] = (
        cl_a[nonzero] * params.x_attached_hat + cl_v[nonzero] * params.x_vortex_hat
    ) / cl_total[nonzero]

    return _to_scalar_or_array(cl_attached, result)


def moment_from_center_of_pressure(
    cl_total, x_cp_hat, params: PitchingMomentParameters = DEFAULT_MOMENT_PARAMS
):
    """C_m reconstructed from the combined center of pressure (a load-bearing identity):

        C_m,total = C_m0 - C_L,total * (x_cp_hat - x_ref_hat) / c_ref_hat

    This must equal :func:`total_moment_coefficient` exactly (to floating-
    point precision) for any alpha where C_L,total != 0, since x_ref cancels
    out of the underlying weighted-average derivation -- see module
    docstring and tests/test_pitching_moment.py.
    """
    cl_arr = np.asarray(cl_total, dtype=float)
    xcp_arr = np.asarray(x_cp_hat, dtype=float)
    result = params.cm0 - cl_arr * (xcp_arr - params.x_ref_hat) / params.c_ref_hat
    return _to_scalar_or_array(cl_total, result)


class PitchingMomentAerodynamics(NamedTuple):
    """Full pitching-moment bundle at a given alpha, built on the unchanged
    M1 attached-flow lift and the M4 effective (breakdown-limited) vortex
    lift -- see module docstring for what is/is not duplicated from M2/M4.
    """

    f_b: "float | NDArray[np.floating]"
    cl_attached: "float | NDArray[np.floating]"
    cl_vortex_pre: "float | NDArray[np.floating]"
    cl_vortex_effective: "float | NDArray[np.floating]"
    cl_total: "float | NDArray[np.floating]"
    x_cp_hat: "float | NDArray[np.floating]"
    cm_attached: "float | NDArray[np.floating]"
    cm_vortex: "float | NDArray[np.floating]"
    cm_total: "float | NDArray[np.floating]"


def pitching_moment_aerodynamics(
    alpha_rad,
    aspect_ratio: float,
    e: float,
    sweep_rad: float,
    moment_params: PitchingMomentParameters = DEFAULT_MOMENT_PARAMS,
    breakdown_params: BreakdownParameters = DEFAULT_BREAKDOWN_PARAMS,
    a0: float = A0_THIN_AIRFOIL,
    kv_ref: float = KV_REFERENCE,
    sweep_ref_rad: float = SWEEP_REFERENCE_RAD,
) -> PitchingMomentAerodynamics:
    """Full pitching-moment/center-of-pressure bundle at the given alpha(s).

    Uses attached_flow.attached_flow_CL (M1, unchanged) and
    breakdown.effective_vortex_lift_coefficient (M4, unchanged, using its
    own vortex_effectiveness -- not reimplemented here) for the two lift
    contributions, so this reduces EXACTLY to the pre-breakdown (M2-
    consistent) moment model wherever f_b == 1.
    """
    f_b = vortex_effectiveness(alpha_rad, breakdown_params)
    cl_attached = attached_flow_CL(alpha_rad, aspect_ratio, e, a0)
    cl_vortex_pre = vortex_lift_coefficient(alpha_rad, sweep_rad, kv_ref, sweep_ref_rad)
    cl_vortex_eff = effective_vortex_lift_coefficient(
        alpha_rad, sweep_rad, breakdown_params, kv_ref, sweep_ref_rad
    )
    cl_total = np.asarray(cl_attached, dtype=float) + np.asarray(cl_vortex_eff, dtype=float)

    x_cp_hat = center_of_pressure_hat(cl_attached, cl_vortex_eff, moment_params)
    cm_attached = attached_moment_coefficient(cl_attached, moment_params)
    cm_vortex = vortex_moment_coefficient(cl_vortex_eff, moment_params)
    cm_total = total_moment_coefficient(cl_attached, cl_vortex_eff, moment_params)

    return PitchingMomentAerodynamics(
        f_b=f_b,
        cl_attached=cl_attached,
        cl_vortex_pre=cl_vortex_pre,
        cl_vortex_effective=cl_vortex_eff,
        cl_total=_to_scalar_or_array(alpha_rad, cl_total),
        x_cp_hat=x_cp_hat,
        cm_attached=cm_attached,
        cm_vortex=cm_vortex,
        cm_total=cm_total,
    )
