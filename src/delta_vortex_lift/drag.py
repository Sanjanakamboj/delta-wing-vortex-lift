"""Reduced-order, Polhamus-inspired drag-due-to-lift and L/D model.

Scope and honesty statement (read before use)
----------------------------------------------
This module extends the M1 attached-flow lift baseline and the M2
Polhamus-style vortex-lift term (kept unchanged, see attached_flow.py and
vortex_lift.py) with a transparent, reduced-order drag-due-to-lift model.

Primary source for the vortex-drag term
    Edward C. Polhamus, "Application of the Leading-Edge-Suction Analogy of
    Vortex Lift to the Drag Due to Lift of Sharp-Edge Delta Wings," NASA TN
    D-4739, August 1968.

    For a thin, sharp-edge wing with a Kutta-type condition at the leading
    edge (zero leading-edge suction), the resultant aerodynamic force is, by
    construction, perpendicular to the wing-chord plane. Resolving that
    force into wind axes gives a drag-due-to-lift contribution

        Delta C_D = C_L * tan(alpha)                      (Polhamus (1968), eq. 4)

    which he applies to his COMBINED lift coefficient
    C_L = K_p sin(alpha)cos^2(alpha) + K_v cos(alpha)sin^2(alpha) to get his
    eq. (5). His comparisons with experiment (aspect ratios 0.25-2.0) show
    this "zero-leading-edge-suction with vortex lift" assumption predicts
    drag due to lift accurately, and, notably, that for very slender wings
    the vortex-lift-inclusive drag due to lift can be LOWER than the
    classical full-leading-edge-suction (elliptical) induced-drag result.

What is adopted here
    The same geometric argument -- a force with no leading-edge suction
    resolves into a drag-due-to-lift term equal to (that force's lift
    component) x tan(alpha) -- is applied here specifically to the vortex
    LIFT component alone (since the M2 vortex term is, by the same Kutta-
    type/no-suction assumption used to derive it in vortex_lift.py, already
    a force normal to the chord):

        C_D,vortex(alpha, Lambda_LE) = C_L,vortex(alpha, Lambda_LE) * tan(alpha)

What is intentionally simplified/deferred
    Polhamus's own eq. (5) applies the tan(alpha) resolution to his
    COMBINED (potential + vortex) lift coefficient, because in his theory
    BOTH terms already assume zero leading-edge suction. This project keeps
    Milestone 1's classical attached-flow baseline
    (C_L,attached = a*alpha, from ordinary lifting-line theory, which DOES
    assume normal leading-edge suction / elliptical-type loading) unchanged,
    per the project's milestone structure. It would therefore be
    inconsistent to also resolve the attached term via tan(alpha) -- that
    term is not a zero-suction force. Instead, the attached contribution
    uses the classical induced-drag relation

        C_Di,attached = C_L,attached^2 / (pi * e * AR)

    (Prandtl lifting-line theory; e.g. Anderson, "Fundamentals of
    Aerodynamics"), consistent with the same (e, AR) already used for
    C_L,attached in attached_flow.py. This is therefore a HYBRID reduced-
    order model -- NOT Polhamus's own combined drag formula -- and is
    explicitly labeled as such throughout this project. See DESIGN.md.

Total drag model
    C_D,total(alpha) = C_D0 + C_Di,attached(alpha) + C_D,vortex(alpha, Lambda_LE)

    C_D0 is an explicit, illustrative, uncalibrated zero-lift/profile-drag
    constant (default 0.028, within the stated 0.02-0.04 conceptual range)
    representing skin-friction/form/interference drag that is entirely
    outside the scope of this lift-based model. It is NOT fit to any real
    aircraft or dataset.

No stall, no vortex breakdown, and no arbitrary drag rise is included. The
model and all figures/tables in this project are restricted to and only
claimed valid over alpha in [0 deg, 25 deg], matching Milestone 2.
"""

from __future__ import annotations

import math
from typing import NamedTuple, overload

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .attached_flow import A0_THIN_AIRFOIL, attached_flow_CL
from .vortex_lift import KV_REFERENCE, SWEEP_REFERENCE_RAD, vortex_lift_coefficient

#: Illustrative, uncalibrated zero-lift/profile-drag coefficient, within the
#: conceptual 0.02-0.04 range stated for this reduced-order study. Represents
#: skin-friction/form/interference drag NOT modeled elsewhere in this
#: project. Not fit to any real aircraft or experimental dataset.
CD0_DEFAULT = 0.028

#: Angle of attack [deg] beyond which tan(alpha) starts to diverge badly
#: enough that this reduced-order drag model should not be trusted even
#: formally. Well outside the project's declared 0-25 deg study range.
_MAX_SANE_ALPHA_RAD = math.radians(89.0)


def _validate_alpha(alpha_rad) -> None:
    arr = np.asarray(alpha_rad, dtype=float)
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"alpha_rad must be finite, got {alpha_rad!r}")
    if np.any(np.abs(arr) >= _MAX_SANE_ALPHA_RAD):
        raise ValueError(
            "alpha_rad must be within (-89 deg, 89 deg) for tan(alpha) to remain "
            f"well-behaved in this reduced-order drag model, got {alpha_rad!r}"
        )


def _validate_cd0(cd0: float) -> None:
    if not math.isfinite(cd0) or cd0 < 0.0:
        raise ValueError(f"C_D0 must be non-negative and finite, got {cd0!r}")


def _validate_AR_e(aspect_ratio: float, e: float) -> None:
    if not math.isfinite(aspect_ratio) or aspect_ratio <= 0.0:
        raise ValueError(f"aspect_ratio must be positive and finite, got {aspect_ratio!r}")
    if not math.isfinite(e) or e <= 0.0:
        raise ValueError(f"e (span efficiency factor) must be positive and finite, got {e!r}")


def _to_scalar_or_array(alpha_like, result):
    if isinstance(alpha_like, (int, float)) and not isinstance(alpha_like, bool):
        return float(result)
    return result


@overload
def attached_induced_drag_coefficient(
    alpha_rad: float, aspect_ratio: float, e: float, a0: float = ...
) -> float: ...
@overload
def attached_induced_drag_coefficient(
    alpha_rad: ArrayLike, aspect_ratio: float, e: float, a0: float = ...
) -> NDArray[np.floating]: ...


def attached_induced_drag_coefficient(
    alpha_rad,
    aspect_ratio: float,
    e: float,
    a0: float = A0_THIN_AIRFOIL,
):
    """Classical induced drag of the attached-flow contribution.

        C_Di,attached = C_L,attached^2 / (pi * e * AR)

    Prandtl lifting-line theory (see e.g. Anderson, *Fundamentals of
    Aerodynamics*), using the SAME (aspect_ratio, e) already used for
    C_L,attached in attached_flow.py -- no new efficiency parameter is
    introduced.
    """
    _validate_alpha(alpha_rad)
    _validate_AR_e(aspect_ratio, e)
    cl_attached = np.asarray(attached_flow_CL(alpha_rad, aspect_ratio, e, a0), dtype=float)
    result = cl_attached**2 / (math.pi * e * aspect_ratio)
    return _to_scalar_or_array(alpha_rad, result)


@overload
def vortex_drag_coefficient(
    alpha_rad: float,
    sweep_rad: float,
    kv_ref: float = ...,
    sweep_ref_rad: float = ...,
) -> float: ...
@overload
def vortex_drag_coefficient(
    alpha_rad: ArrayLike,
    sweep_rad: float,
    kv_ref: float = ...,
    sweep_ref_rad: float = ...,
) -> NDArray[np.floating]: ...


def vortex_drag_coefficient(
    alpha_rad,
    sweep_rad: float,
    kv_ref: float = KV_REFERENCE,
    sweep_ref_rad: float = SWEEP_REFERENCE_RAD,
):
    """Polhamus-style vortex drag-due-to-lift, C_D,vortex = C_L,vortex * tan(alpha).

    Same normal-force/zero-leading-edge-suction resolution argument as
    Polhamus (1968) eq. (4), applied here to the vortex-lift component only
    (see module docstring for why the attached component is NOT resolved
    this way in this project).
    """
    _validate_alpha(alpha_rad)
    alpha_arr = np.asarray(alpha_rad, dtype=float)
    cl_vortex = np.asarray(
        vortex_lift_coefficient(alpha_arr, sweep_rad, kv_ref, sweep_ref_rad), dtype=float
    )
    result = cl_vortex * np.tan(alpha_arr)
    return _to_scalar_or_array(alpha_rad, result)


class DragComponents(NamedTuple):
    """Named breakdown of the total drag coefficient."""

    cd0: float
    cdi_attached: "float | NDArray[np.floating]"
    cd_vortex: "float | NDArray[np.floating]"
    cd_total: "float | NDArray[np.floating]"


def drag_components(
    alpha_rad,
    aspect_ratio: float,
    e: float,
    sweep_rad: float,
    cd0: float = CD0_DEFAULT,
    a0: float = A0_THIN_AIRFOIL,
    kv_ref: float = KV_REFERENCE,
    sweep_ref_rad: float = SWEEP_REFERENCE_RAD,
) -> DragComponents:
    """Full drag breakdown: (C_D0, C_Di,attached, C_D,vortex, C_D,total).

        C_D,total = C_D0 + C_Di,attached + C_D,vortex

    No clipping, saturation, or stall/drag-rise model is applied.
    """
    _validate_cd0(cd0)
    cdi_attached = attached_induced_drag_coefficient(alpha_rad, aspect_ratio, e, a0)
    cd_vortex = vortex_drag_coefficient(alpha_rad, sweep_rad, kv_ref, sweep_ref_rad)
    cd_total = cd0 + np.asarray(cdi_attached) + np.asarray(cd_vortex)
    cd_total = _to_scalar_or_array(alpha_rad, cd_total)
    return DragComponents(cd0=cd0, cdi_attached=cdi_attached, cd_vortex=cd_vortex, cd_total=cd_total)


def total_drag_coefficient(
    alpha_rad,
    aspect_ratio: float,
    e: float,
    sweep_rad: float,
    cd0: float = CD0_DEFAULT,
    a0: float = A0_THIN_AIRFOIL,
    kv_ref: float = KV_REFERENCE,
    sweep_ref_rad: float = SWEEP_REFERENCE_RAD,
):
    """C_D,total = C_D0 + C_Di,attached + C_D,vortex. See :func:`drag_components`."""
    return drag_components(alpha_rad, aspect_ratio, e, sweep_rad, cd0, a0, kv_ref, sweep_ref_rad).cd_total


def attached_only_drag_coefficient(
    alpha_rad,
    aspect_ratio: float,
    e: float,
    cd0: float = CD0_DEFAULT,
    a0: float = A0_THIN_AIRFOIL,
):
    """Model A (attached-only) drag: C_D = C_D0 + C_Di,attached. No vortex term."""
    _validate_cd0(cd0)
    cdi_attached = attached_induced_drag_coefficient(alpha_rad, aspect_ratio, e, a0)
    result = cd0 + np.asarray(cdi_attached)
    return _to_scalar_or_array(alpha_rad, result)


def lift_to_drag_ratio(cl, cd):
    """L/D = C_L / C_D, elementwise. C_L and C_D may be scalars or arrays of
    matching (broadcastable) shape.

    Returns 0.0 (not NaN/Inf) wherever C_L == 0 exactly (in particular at
    alpha = 0, where C_D = C_D0 != 0 but C_L,total = 0, so L/D = 0 is the
    correct value, not an artifact). Raises if any C_D == 0 while the
    corresponding C_L != 0, since that represents an undefined (infinite)
    L/D within the declared model rather than a meaningful result.
    """
    cl_arr = np.asarray(cl, dtype=float)
    cd_arr = np.asarray(cd, dtype=float)
    if not np.all(np.isfinite(cl_arr)) or not np.all(np.isfinite(cd_arr)):
        raise ValueError("cl and cd must be finite")

    cl_b, cd_b = np.broadcast_arrays(cl_arr, cd_arr)
    zero_cd = cd_b == 0.0
    if np.any(zero_cd & (cl_b != 0.0)):
        raise ValueError("C_D is zero where C_L is nonzero: L/D is undefined (infinite)")

    result = np.zeros_like(cl_b, dtype=float)
    nonzero = ~zero_cd
    with np.errstate(invalid="ignore", divide="ignore"):
        result[nonzero] = cl_b[nonzero] / cd_b[nonzero]

    is_scalar = (
        isinstance(cl, (int, float)) and not isinstance(cl, bool)
    ) and (isinstance(cd, (int, float)) and not isinstance(cd, bool))
    if is_scalar:
        return float(result)
    return result
