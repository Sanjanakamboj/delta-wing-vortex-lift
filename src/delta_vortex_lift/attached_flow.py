"""Deliberately simple attached-flow lift baseline for the delta wing.

Scope and limitations (read before use)
----------------------------------------
This module implements the classical incompressible finite-wing (lifting-line)
lift-curve-slope correction:

    a = a0 / (1 + a0 / (pi * e * AR))

with a0 = 2*pi [1/rad] the thin-airfoil 2D lift-curve slope by default, e an
explicitly declared span-efficiency factor, and AR the wing aspect ratio. The
attached-flow lift coefficient is then the small-angle linear relation

    C_L,attached(alpha) = a * alpha        (alpha in radians)

This finite-wing relation was derived for moderate-to-high aspect ratio,
attached-flow wings. A highly swept, low-aspect-ratio delta wing like the one
used in this project does NOT satisfy those assumptions: at even modest angle
of attack, a delta wing develops separated leading-edge vortices that add a
large, nonlinear "vortex lift" contribution not captured by this formula.

Therefore, everywhere in this project, C_L,attached computed here is used
only as a transparent, textbook baseline / reference curve -- explicitly NOT
a high-fidelity prediction of delta-wing lift. Vortex lift is added in a
later milestone; it is intentionally absent from this module.

No stall model, no sweep correction, and no vortex-lift term is included
here. See DESIGN.md for the full derivation, source audit, and the
reconciliation of sign/angle conventions against the cited references.
"""

from __future__ import annotations

import math
from typing import overload

import numpy as np
from numpy.typing import ArrayLike, NDArray

#: Default 2D (infinite-span) thin-airfoil lift-curve slope [1/rad].
A0_THIN_AIRFOIL = 2.0 * math.pi


def _validate_AR_e(aspect_ratio: float, e: float) -> None:
    if not math.isfinite(aspect_ratio) or aspect_ratio <= 0.0:
        raise ValueError(f"aspect_ratio must be positive and finite, got {aspect_ratio!r}")
    if not math.isfinite(e) or e <= 0.0:
        raise ValueError(f"e (span efficiency factor) must be positive and finite, got {e!r}")


def finite_wing_lift_curve_slope(
    aspect_ratio: float,
    e: float,
    a0: float = A0_THIN_AIRFOIL,
) -> float:
    """Finite-wing lift-curve slope a [1/rad] from the classical lifting-line correction.

    a = a0 / (1 + a0 / (pi * e * AR))

    Parameters
    ----------
    aspect_ratio : AR = b^2/S [-], must be > 0.
    e : span efficiency factor [-], must be > 0. Documented, not calibrated.
    a0 : 2D lift-curve slope [1/rad], default 2*pi (thin-airfoil theory).
    """
    _validate_AR_e(aspect_ratio, e)
    if not math.isfinite(a0) or a0 <= 0.0:
        raise ValueError(f"a0 must be positive and finite, got {a0!r}")
    return a0 / (1.0 + a0 / (math.pi * e * aspect_ratio))


@overload
def attached_flow_CL(alpha_rad: float, aspect_ratio: float, e: float, a0: float = ...) -> float: ...
@overload
def attached_flow_CL(
    alpha_rad: ArrayLike, aspect_ratio: float, e: float, a0: float = ...
) -> NDArray[np.floating]: ...


def attached_flow_CL(alpha_rad, aspect_ratio: float, e: float, a0: float = A0_THIN_AIRFOIL):
    """Attached-flow lift coefficient C_L,attached = a * alpha.

    ``alpha_rad`` may be a scalar or an array-like (radians). Returns the same
    kind of shape (a Python float for scalar input, an ndarray otherwise).

    This is a linear, small-angle baseline; it is evaluated formally at any
    alpha given, but is only physically defensible near alpha = 0 for a
    highly swept delta wing (see module docstring).
    """
    a = finite_wing_lift_curve_slope(aspect_ratio, e, a0)
    alpha_arr = np.asarray(alpha_rad, dtype=float)
    result = a * alpha_arr
    if np.isscalar(alpha_rad) or (isinstance(alpha_rad, (int, float)) and not isinstance(alpha_rad, bool)):
        return float(result)
    return result


def attached_flow_CL_deg(alpha_deg, aspect_ratio: float, e: float, a0: float = A0_THIN_AIRFOIL):
    """Same as :func:`attached_flow_CL` but with alpha given in degrees."""
    alpha_deg_arr = np.asarray(alpha_deg, dtype=float)
    alpha_rad = np.radians(alpha_deg_arr)
    result = attached_flow_CL(alpha_rad, aspect_ratio, e, a0)
    return result


# ----------------------------------------------------------------------
# Secondary: dimensional lift helper (kept separate from the C_L model)
# ----------------------------------------------------------------------


def dynamic_pressure(rho_inf: float, V_inf: float) -> float:
    """q_inf = 0.5 * rho_inf * V_inf^2 [Pa]."""
    if not math.isfinite(rho_inf) or rho_inf <= 0.0:
        raise ValueError(f"rho_inf must be positive and finite, got {rho_inf!r}")
    if not math.isfinite(V_inf) or V_inf < 0.0:
        raise ValueError(f"V_inf must be non-negative and finite, got {V_inf!r}")
    return 0.5 * rho_inf * V_inf**2


def dimensional_lift(C_L: float, q_inf: float, S: float) -> float:
    """L = q_inf * S * C_L [N].

    Secondary/dimensional helper, kept separate from the dimensionless
    C_L,attached model above. Not required to evaluate C_L.
    """
    if not math.isfinite(q_inf) or q_inf < 0.0:
        raise ValueError(f"q_inf must be non-negative and finite, got {q_inf!r}")
    if not math.isfinite(S) or S <= 0.0:
        raise ValueError(f"S must be positive and finite, got {S!r}")
    return q_inf * S * C_L
