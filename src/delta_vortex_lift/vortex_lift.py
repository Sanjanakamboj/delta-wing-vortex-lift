"""Reduced-order, Polhamus-inspired vortex-lift contribution for a sharp-edged delta wing.

Scope and honesty statement (read before use)
----------------------------------------------
This module implements a **reduced-order, Polhamus-inspired** vortex-lift
term. It is NOT a re-implementation of the full original theory of

    Edward C. Polhamus, "A Concept of the Vortex Lift of Sharp-Edge Delta
    Wings Based on a Leading-Edge-Suction Analogy," NASA TN D-3767, 1966.

What is adopted directly from Polhamus (1966)
    The functional FORM of the vortex-lift term, his equation (12):

        C_L,v = K_v * cos(alpha) * sin^2(alpha)

    This form falls directly out of his leading-edge-suction analogy: the
    leading-edge suction force that would exist for attached potential flow
    is instead assumed to be recovered as extra normal force from the
    separated, reattaching leading-edge vortex. K_v is "a constant of
    proportionality in the vortex lift equation" (Polhamus's own symbol and
    definition), and his equation (13) gives

        K_v = (K_p - K_p^2 * K_i) / cos(Lambda_LE)

    i.e. K_v scales with 1/cos(Lambda_LE) once the planform-dependent
    prefactor (K_p - K_p^2 K_i) is held fixed. Polhamus's own numerical
    study (his fig. 9) found K_v varies only slowly with aspect ratio -- from
    about 3.14 at AR=0 to about 3.45 at AR=4 -- for the family of wings he
    studied.

What is intentionally simplified/deferred here
    Computing K_p and K_i exactly requires a full numerical lifting-surface
    solution (Polhamus used a modified Multhopp method). That computation is
    out of scope for this reduced-order portfolio milestone. Instead:

    - K_v is treated as an explicit, illustrative reference coefficient
      (`KV_REFERENCE`), chosen within the numerical range Polhamus himself
      reports (~3.14-3.45), NOT re-derived from Multhopp lifting-surface
      theory or fitted to any specific experimental dataset.
    - The explicit, analytically-derived sweep dependence from Polhamus's
      eq. (13), K_v proportional to 1/cos(Lambda_LE), IS used here to scale
      the reference coefficient to other sweep angles, holding the
      planform-dependent prefactor fixed at its reference value. This is a
      documented approximation, not the full theory.
    - Polhamus's own attached/potential term (his eq. (5),
      C_L,p = K_p sin(alpha) cos^2(alpha)) is NOT used here. This project's
      Milestone 1 attached-flow baseline (classical finite-wing lifting-line
      slope, C_L,attached = a*alpha) is kept unchanged and used as the
      "attached" contribution instead, per the project's milestone
      structure. The vortex term from Polhamus is added on top of that
      *linear* baseline rather than on top of Polhamus's own nonlinear
      potential term. This is a deliberate simplification of the original
      combined theory and is called out explicitly here and in DESIGN.md.

This is therefore called a "Polhamus-style" or "Polhamus-inspired" reduced
order vortex-lift model throughout this project -- explicitly NOT a full,
validated Polhamus aerodynamic prediction.

No vortex-breakdown or stall model is included. The vortex-lift term used
here grows monotonically with alpha only up to alpha = arctan(sqrt(2)) =~
54.7 deg (a property of the sin^2(alpha)cos(alpha) functional form itself);
this project only evaluates and plots it over a much smaller conceptual
range (0-25 deg) and explicitly does not claim validity beyond that range,
nor does it model the physical vortex-breakdown/stall process that would
actually limit real delta-wing lift at high alpha.
"""

from __future__ import annotations

import math
from typing import overload

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .attached_flow import A0_THIN_AIRFOIL, attached_flow_CL

#: Illustrative reference vortex-lift coefficient, chosen within the
#: numerical range Polhamus (1966, fig. 9) reports for delta wings
#: (K_v ~ 3.14 to 3.45 over aspect ratios 0 to 4). NOT fitted to any
#: specific experimental dataset or recomputed via Multhopp theory here.
KV_REFERENCE = 3.30

#: Reference leading-edge sweep [rad] at which KV_REFERENCE is declared to
#: apply -- the sweep of this project's representative geometry (65 deg).
SWEEP_REFERENCE_RAD = math.radians(65.0)


def _validate_alpha(alpha_rad) -> None:
    arr = np.asarray(alpha_rad, dtype=float)
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"alpha_rad must be finite, got {alpha_rad!r}")


def _validate_sweep(sweep_rad: float, name: str = "sweep_rad") -> None:
    if not math.isfinite(sweep_rad) or not (0.0 < sweep_rad < math.pi / 2.0):
        raise ValueError(
            f"{name} must be finite and strictly between 0 and pi/2 rad, got {sweep_rad!r}"
        )


def _validate_kv(kv_ref: float) -> None:
    if not math.isfinite(kv_ref) or kv_ref <= 0.0:
        raise ValueError(f"kv_ref must be positive and finite, got {kv_ref!r}")


def kv_of_sweep(
    sweep_rad: float,
    kv_ref: float = KV_REFERENCE,
    sweep_ref_rad: float = SWEEP_REFERENCE_RAD,
) -> float:
    """Sweep-scaled vortex-lift coefficient K_v(Lambda_LE).

    Uses the 1/cos(Lambda_LE) scaling that falls directly out of Polhamus's
    eq. (13), K_v = (K_p - K_p^2 K_i) / cos(Lambda_LE), while holding the
    planform-dependent prefactor (K_p - K_p^2 K_i) fixed at the value
    implied by (kv_ref, sweep_ref_rad):

        K_v(Lambda) = kv_ref * cos(sweep_ref_rad) / cos(Lambda)

    This is a documented simplification (see module docstring) -- the
    prefactor in reality depends weakly on planform/aspect ratio too, per
    Polhamus's fig. 9, but that dependence is not re-derived here.
    """
    _validate_kv(kv_ref)
    _validate_sweep(sweep_rad)
    _validate_sweep(sweep_ref_rad, name="sweep_ref_rad")
    return kv_ref * math.cos(sweep_ref_rad) / math.cos(sweep_rad)


@overload
def vortex_lift_coefficient(
    alpha_rad: float,
    sweep_rad: float,
    kv_ref: float = ...,
    sweep_ref_rad: float = ...,
) -> float: ...
@overload
def vortex_lift_coefficient(
    alpha_rad: ArrayLike,
    sweep_rad: float,
    kv_ref: float = ...,
    sweep_ref_rad: float = ...,
) -> NDArray[np.floating]: ...


def vortex_lift_coefficient(
    alpha_rad,
    sweep_rad: float,
    kv_ref: float = KV_REFERENCE,
    sweep_ref_rad: float = SWEEP_REFERENCE_RAD,
):
    """Polhamus-style vortex-lift coefficient, C_L,v = K_v * cos(alpha) * sin^2(alpha).

    This is Polhamus's eq. (12) exactly, with K_v obtained from
    :func:`kv_of_sweep`. See the module docstring for what is and is not
    adopted from the original theory.

    ``alpha_rad`` may be a scalar or array-like (radians, no restriction to
    positive values is enforced here, but the model is only claimed to be
    meaningful over the conceptual small-to-moderate positive-alpha range
    documented in DESIGN.md/README.md). Returns the same kind of shape as
    :func:`delta_vortex_lift.attached_flow.attached_flow_CL`.
    """
    _validate_alpha(alpha_rad)
    kv = kv_of_sweep(sweep_rad, kv_ref, sweep_ref_rad)
    alpha_arr = np.asarray(alpha_rad, dtype=float)
    result = kv * np.cos(alpha_arr) * np.sin(alpha_arr) ** 2
    if isinstance(alpha_rad, (int, float)) and not isinstance(alpha_rad, bool):
        return float(result)
    return result


def vortex_lift_coefficient_deg(
    alpha_deg,
    sweep_deg: float,
    kv_ref: float = KV_REFERENCE,
    sweep_ref_deg: float = 65.0,
):
    """Same as :func:`vortex_lift_coefficient` but alpha and sweep in degrees."""
    alpha_rad = np.radians(np.asarray(alpha_deg, dtype=float))
    sweep_rad = math.radians(sweep_deg)
    sweep_ref_rad = math.radians(sweep_ref_deg)
    result = vortex_lift_coefficient(alpha_rad, sweep_rad, kv_ref, sweep_ref_rad)
    if isinstance(alpha_deg, (int, float)) and not isinstance(alpha_deg, bool):
        return float(result)
    return result


def total_lift_coefficient(
    alpha_rad,
    aspect_ratio: float,
    e: float,
    sweep_rad: float,
    a0: float = A0_THIN_AIRFOIL,
    kv_ref: float = KV_REFERENCE,
    sweep_ref_rad: float = SWEEP_REFERENCE_RAD,
):
    """Total lift coefficient: the SUM of the unchanged M1 attached-flow term
    and the Polhamus-style vortex-lift term, and nothing else.

        C_L,total(alpha) = C_L,attached(alpha) + C_L,vortex(alpha, Lambda_LE)

    No clipping, saturation, or stall model is applied.
    """
    cl_attached = attached_flow_CL(alpha_rad, aspect_ratio, e, a0)
    cl_vortex = vortex_lift_coefficient(alpha_rad, sweep_rad, kv_ref, sweep_ref_rad)
    return cl_attached + cl_vortex


def total_lift_coefficient_deg(
    alpha_deg,
    aspect_ratio: float,
    e: float,
    sweep_deg: float,
    a0: float = A0_THIN_AIRFOIL,
    kv_ref: float = KV_REFERENCE,
    sweep_ref_deg: float = 65.0,
):
    """Same as :func:`total_lift_coefficient` but alpha and sweep in degrees."""
    alpha_rad = np.radians(np.asarray(alpha_deg, dtype=float))
    sweep_rad = math.radians(sweep_deg)
    sweep_ref_rad = math.radians(sweep_ref_deg)
    result = total_lift_coefficient(alpha_rad, aspect_ratio, e, sweep_rad, a0, kv_ref, sweep_ref_rad)
    if isinstance(alpha_deg, (int, float)) and not isinstance(alpha_deg, bool):
        return float(result)
    return result


def vortex_fraction(
    alpha_rad,
    aspect_ratio: float,
    e: float,
    sweep_rad: float,
    a0: float = A0_THIN_AIRFOIL,
    kv_ref: float = KV_REFERENCE,
    sweep_ref_rad: float = SWEEP_REFERENCE_RAD,
):
    """Vortex-lift fraction f_v = C_L,vortex / C_L,total.

    At alpha = 0, both C_L,vortex and C_L,total are exactly zero; f_v is
    defined to be exactly 0.0 there (by continuity: f_v -> 0 as alpha -> 0,
    since C_L,vortex ~ alpha^2 while C_L,attached ~ alpha), rather than
    raising a division warning or returning NaN.
    """
    _validate_alpha(alpha_rad)
    alpha_arr = np.asarray(alpha_rad, dtype=float)
    cl_attached = np.asarray(attached_flow_CL(alpha_arr, aspect_ratio, e, a0), dtype=float)
    cl_vortex = np.asarray(vortex_lift_coefficient(alpha_arr, sweep_rad, kv_ref, sweep_ref_rad), dtype=float)
    cl_total = cl_attached + cl_vortex

    nonzero = cl_total != 0.0
    fraction = np.zeros_like(cl_total)
    with np.errstate(invalid="ignore", divide="ignore"):
        fraction[nonzero] = cl_vortex[nonzero] / cl_total[nonzero]

    if isinstance(alpha_rad, (int, float)) and not isinstance(alpha_rad, bool):
        return float(fraction)
    return fraction
