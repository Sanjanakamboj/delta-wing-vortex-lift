#!/usr/bin/env python3
"""Milestone 3 engineering study: drag-due-to-lift, aerodynamic polar, and L/D.

Prints a deterministic engineering table plus geometry, drag-model
coefficients, an independent cross-check, an attached-only vs.
attached+vortex comparison, best sampled L/D, and a C_D0/K_v sensitivity
study.

    STALL AND VORTEX BREAKDOWN ARE NOT MODELED. Do not extrapolate the
    curves below alpha = 0 deg or above alpha = 25 deg. Any "best sampled
    L/D" reported below is exactly that -- the best value found on the
    sampled alpha grid within the declared conceptual range -- NOT a claimed
    aerodynamic optimum.
"""

import math

import numpy as np

from delta_vortex_lift.attached_flow import attached_flow_CL_deg, finite_wing_lift_curve_slope
from delta_vortex_lift.drag import (
    CD0_DEFAULT,
    attached_only_drag_coefficient,
    drag_components,
    lift_to_drag_ratio,
)
from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.vortex_lift import KV_REFERENCE, total_lift_coefficient_deg, vortex_lift_coefficient_deg

E_EFFICIENCY = 0.9
STUDY_ALPHAS_DEG = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0]
COMPARISON_ALPHAS_DEG = [5.0, 10.0, 15.0, 20.0]
CD0_SENSITIVITY = [0.02, 0.03, 0.04]
KV_SENSITIVITY_FRACTIONS = [0.8, 1.0, 1.2]

# Fine grid used for "best sampled L/D" search over the declared conceptual range.
FINE_ALPHA_DEG = np.linspace(0.01, 25.0, 500)  # avoid alpha=0 exactly for L/D search cosmetics


def _model_a(alpha_deg, AR, e, cd0):
    """Attached-only model: CL = CL,attached, CD = CD0 + CDi,attached."""
    cl = attached_flow_CL_deg(alpha_deg, AR, e)
    cd = attached_only_drag_coefficient(np.radians(alpha_deg), AR, e, cd0=cd0)
    return cl, cd


def _model_b(alpha_deg, AR, e, sweep_deg, cd0, kv_ref=KV_REFERENCE):
    """Attached+vortex model: CL = CL,total, CD = CD0 + CDi,attached + CD,vortex."""
    cl = total_lift_coefficient_deg(alpha_deg, AR, e, sweep_deg, kv_ref=kv_ref)
    dc = drag_components(np.radians(alpha_deg), AR, e, math.radians(sweep_deg), cd0=cd0, kv_ref=kv_ref)
    return cl, dc.cd_total


def main() -> None:
    wing = representative_geometry()
    AR = wing.aspect_ratio
    sweep_deg = wing.sweep_LE_deg
    cd0 = CD0_DEFAULT

    print("=" * 82)
    print("MILESTONE 3 -- DRAG-DUE-TO-LIFT AND L/D STUDY")
    print("Reduced-order / conceptual model. Stall and vortex breakdown are")
    print("NOT modeled. Do not extrapolate beyond alpha = 0-25 deg.")
    print("=" * 82)

    print("\n-- Geometry (unchanged from Milestone 1) --")
    print(f"  planform area S       = {wing.area:.4f} m^2")
    print(f"  aspect ratio AR       = {AR:.4f}")
    print(f"  LE sweep Lambda_LE    = {sweep_deg:.4f} deg")
    print(f"  span efficiency e     = {E_EFFICIENCY} (unchanged from M1)")

    a_rad = finite_wing_lift_curve_slope(AR, E_EFFICIENCY)
    print(f"\n-- Drag-model equation --")
    print(f"  C_Di,attached = C_L,attached^2 / (pi*e*AR)          [classical lifting-line induced drag]")
    print(f"  C_D,vortex    = C_L,vortex * tan(alpha)             [Polhamus (1968) eq.4 form, applied to vortex term only]")
    print(f"  C_D,total     = C_D0 + C_Di,attached + C_D,vortex")
    print(f"  C_D0 (illustrative, uncalibrated) = {cd0}")
    print(f"  attached-flow slope a = {a_rad:.6f} 1/rad")
    print(f"  K_v reference          = {KV_REFERENCE:.4f}")

    print(f"\n-- Full decomposition table (Lambda_LE = {sweep_deg:.1f} deg, C_D0 = {cd0}) --")
    header = (
        f"{'a[deg]':>7} {'CLa':>9} {'CLv':>9} {'CLt':>9} {'CD0':>7} "
        f"{'CDia':>9} {'CDv':>9} {'CDt':>9} {'L/D':>8}"
    )
    print(header)
    print("-" * len(header))
    rows = {}
    for alpha_deg in STUDY_ALPHAS_DEG:
        cl_a = attached_flow_CL_deg(alpha_deg, AR, E_EFFICIENCY)
        cl_v = vortex_lift_coefficient_deg(alpha_deg, sweep_deg)
        cl_t = cl_a + cl_v
        dc = drag_components(math.radians(alpha_deg), AR, E_EFFICIENCY, math.radians(sweep_deg), cd0=cd0)
        ld = lift_to_drag_ratio(cl_t, dc.cd_total)
        rows[alpha_deg] = (cl_a, cl_v, cl_t, dc.cd0, dc.cdi_attached, dc.cd_vortex, dc.cd_total, ld)
        print(
            f"{alpha_deg:>7.1f} {cl_a:>9.5f} {cl_v:>9.5f} {cl_t:>9.5f} {dc.cd0:>7.3f} "
            f"{dc.cdi_attached:>9.5f} {dc.cd_vortex:>9.5f} {dc.cd_total:>9.5f} {ld:>8.3f}"
        )

    # Independent numerical cross-check at alpha = 15 deg, hand-derived from
    # the documented formulas without calling the drag_components function
    # for this specific value.
    check_alpha_deg = 15.0
    alpha_rad = math.radians(check_alpha_deg)
    a0 = 2.0 * math.pi
    a_hand = a0 / (1.0 + a0 / (math.pi * E_EFFICIENCY * AR))
    cl_attached_hand = a_hand * alpha_rad
    cdi_hand = cl_attached_hand**2 / (math.pi * E_EFFICIENCY * AR)
    kv_hand = KV_REFERENCE * math.cos(math.radians(65.0)) / math.cos(math.radians(sweep_deg))
    cl_vortex_hand = kv_hand * math.cos(alpha_rad) * math.sin(alpha_rad) ** 2
    cd_vortex_hand = cl_vortex_hand * math.tan(alpha_rad)
    cd_total_hand = cd0 + cdi_hand + cd_vortex_hand
    cd_total_module = rows[check_alpha_deg][6]
    print(f"\n-- Independent hand cross-check at alpha = {check_alpha_deg} deg --")
    print(f"  hand-computed   C_D,total = {cd_total_hand:.10f}")
    print(f"  module-computed C_D,total = {cd_total_module:.10f}")
    print(f"  residual                  = {cd_total_hand - cd_total_module:.3e}")

    # Attached-only vs attached+vortex comparison.
    print(f"\n-- Model A (attached-only) vs. Model B (attached+vortex) --")
    header2 = (
        f"{'a[deg]':>7} {'CLa_A':>8} {'CLa_B':>8} {'CDa_A':>8} {'CDa_B':>8} "
        f"{'LD_A':>7} {'LD_B':>7} {'dCL_v':>8} {'dCD_v':>8} {'%dLD':>8}"
    )
    print(header2)
    for alpha_deg in COMPARISON_ALPHAS_DEG:
        cl_A, cd_A = _model_a(alpha_deg, AR, E_EFFICIENCY, cd0)
        cl_B, cd_B = _model_b(alpha_deg, AR, E_EFFICIENCY, sweep_deg, cd0)
        ld_A = lift_to_drag_ratio(cl_A, cd_A)
        ld_B = lift_to_drag_ratio(cl_B, cd_B)
        d_cl_v = cl_B - cl_A
        d_cd_v = cd_B - cd_A
        pct_dld = 100.0 * (ld_B - ld_A) / ld_A
        print(
            f"{alpha_deg:>7.1f} {cl_A:>8.4f} {cl_B:>8.4f} {cd_A:>8.4f} {cd_B:>8.4f} "
            f"{ld_A:>7.3f} {ld_B:>7.3f} {d_cl_v:>8.4f} {d_cd_v:>8.4f} {pct_dld:>7.2f}%"
        )

    # Best sampled L/D over the fine alpha grid, for both models.
    cl_A_fine, cd_A_fine = _model_a(FINE_ALPHA_DEG, AR, E_EFFICIENCY, cd0)
    ld_A_fine = lift_to_drag_ratio(cl_A_fine, cd_A_fine)
    i_A = int(np.argmax(ld_A_fine))

    cl_B_fine, cd_B_fine = _model_b(FINE_ALPHA_DEG, AR, E_EFFICIENCY, sweep_deg, cd0)
    ld_B_fine = lift_to_drag_ratio(cl_B_fine, cd_B_fine)
    i_B = int(np.argmax(ld_B_fine))

    print(f"\n-- Best sampled L/D within alpha in [0.01, 25] deg (NOT a claimed optimum) --")
    print(f"  Model A (attached-only):   best sampled L/D = {ld_A_fine[i_A]:.4f} at alpha = {FINE_ALPHA_DEG[i_A]:.2f} deg")
    print(f"  Model B (attached+vortex): best sampled L/D = {ld_B_fine[i_B]:.4f} at alpha = {FINE_ALPHA_DEG[i_B]:.2f} deg")

    # C_D0 sensitivity.
    print(f"\n-- C_D0 sensitivity: best sampled L/D (Model B) --")
    for cd0_case in CD0_SENSITIVITY:
        cl_fine, cd_fine = _model_b(FINE_ALPHA_DEG, AR, E_EFFICIENCY, sweep_deg, cd0_case)
        ld_fine = lift_to_drag_ratio(cl_fine, cd_fine)
        i = int(np.argmax(ld_fine))
        print(f"  C_D0={cd0_case:.2f}: best sampled L/D = {ld_fine[i]:.4f} at alpha = {FINE_ALPHA_DEG[i]:.2f} deg")

    # K_v +/-20% sensitivity.
    print(f"\n-- K_v sensitivity: best sampled L/D (Model B, C_D0={cd0}) --")
    for frac in KV_SENSITIVITY_FRACTIONS:
        kv_case = KV_REFERENCE * frac
        cl_fine, cd_fine = _model_b(FINE_ALPHA_DEG, AR, E_EFFICIENCY, sweep_deg, cd0, kv_ref=kv_case)
        ld_fine = lift_to_drag_ratio(cl_fine, cd_fine)
        i = int(np.argmax(ld_fine))
        print(f"  Kv={kv_case:.3f} ({frac:.1f}x): best sampled L/D = {ld_fine[i]:.4f} at alpha = {FINE_ALPHA_DEG[i]:.2f} deg")

    print("\n" + "=" * 82)
    print("Reduced-order Polhamus-inspired drag/L-D model.")
    print("Stall and vortex breakdown are NOT modeled.")
    print("'Best sampled L/D' is a grid-search result, not a claimed aerodynamic optimum.")
    print("=" * 82)


if __name__ == "__main__":
    main()
