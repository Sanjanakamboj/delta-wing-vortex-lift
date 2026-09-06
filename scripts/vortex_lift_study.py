#!/usr/bin/env python3
"""Milestone 2 engineering study: attached-flow vs. vortex-lift decomposition.

Prints a concise, deterministic engineering table plus geometry, model
coefficient, an independent cross-check, and a sweep/coefficient sensitivity
study.

    STALL AND VORTEX BREAKDOWN ARE NOT MODELED. Do not extrapolate the
    curves below alpha = 0 deg or above alpha = 25 deg.
"""

import math

import numpy as np

from delta_vortex_lift.attached_flow import attached_flow_CL_deg, finite_wing_lift_curve_slope
from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.vortex_lift import (
    KV_REFERENCE,
    kv_of_sweep,
    total_lift_coefficient_deg,
    vortex_fraction,
    vortex_lift_coefficient_deg,
)

E_EFFICIENCY = 0.9
STUDY_ALPHAS_DEG = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0]
SENSITIVITY_ALPHAS_DEG = [5.0, 10.0, 15.0, 20.0]
SWEEP_ANGLES_DEG = [55.0, 65.0, 75.0]


def main() -> None:
    wing = representative_geometry()
    AR = wing.aspect_ratio
    sweep_deg = wing.sweep_LE_deg

    print("=" * 78)
    print("MILESTONE 2 -- POLHAMUS-STYLE VORTEX-LIFT STUDY")
    print("Reduced-order / conceptual model. Stall and vortex breakdown are")
    print("NOT modeled. Do not extrapolate beyond alpha = 0-25 deg.")
    print("=" * 78)

    print("\n-- Geometry (unchanged from Milestone 1) --")
    print(f"  root chord c_r        = {wing.root_chord:.4f} m")
    print(f"  span b                = {wing.span:.4f} m")
    print(f"  planform area S       = {wing.area:.4f} m^2")
    print(f"  aspect ratio AR       = {AR:.4f}")
    print(f"  LE sweep Lambda_LE    = {sweep_deg:.4f} deg")

    a_rad = finite_wing_lift_curve_slope(AR, E_EFFICIENCY)
    kv_nominal = kv_of_sweep(math.radians(sweep_deg))
    print(f"\n-- Model coefficients --")
    print(f"  attached-flow slope a = {a_rad:.6f} 1/rad  (e = {E_EFFICIENCY}, unchanged from M1)")
    print(f"  K_v reference          = {KV_REFERENCE:.4f}  (illustrative, Polhamus fig. 9 range ~3.14-3.45)")
    print(f"  K_v at Lambda_LE={sweep_deg:.1f} deg = {kv_nominal:.4f}")
    print("  vortex form: C_L,vortex = K_v * cos(alpha) * sin^2(alpha)  [Polhamus (1966), eq. (12)]")

    print(f"\n-- Lift decomposition table (Lambda_LE = {sweep_deg:.1f} deg) --")
    header = f"{'alpha[deg]':>10}  {'CL_attached':>12}  {'CL_vortex':>10}  {'CL_total':>10}  {'f_v[%]':>8}"
    print(header)
    print("-" * len(header))
    table_rows = {}
    for alpha_deg in STUDY_ALPHAS_DEG:
        cl_a = attached_flow_CL_deg(alpha_deg, AR, E_EFFICIENCY)
        cl_v = vortex_lift_coefficient_deg(alpha_deg, sweep_deg)
        cl_t = total_lift_coefficient_deg(alpha_deg, AR, E_EFFICIENCY, sweep_deg)
        f_v = vortex_fraction(math.radians(alpha_deg), AR, E_EFFICIENCY, math.radians(sweep_deg)) * 100.0
        table_rows[alpha_deg] = (cl_a, cl_v, cl_t, f_v)
        print(f"{alpha_deg:>10.1f}  {cl_a:>12.6f}  {cl_v:>10.6f}  {cl_t:>10.6f}  {f_v:>8.2f}")

    # Independent numerical cross-check at alpha = 15 deg, written out by
    # hand from the documented formulas (not calling the module functions
    # for this specific value).
    check_alpha_deg = 15.0
    alpha_rad = math.radians(check_alpha_deg)
    a0 = 2.0 * math.pi
    a_hand = a0 / (1.0 + a0 / (math.pi * E_EFFICIENCY * AR))
    cl_attached_hand = a_hand * alpha_rad
    kv_hand = KV_REFERENCE * math.cos(math.radians(65.0)) / math.cos(math.radians(sweep_deg))
    cl_vortex_hand = kv_hand * math.cos(alpha_rad) * math.sin(alpha_rad) ** 2
    cl_total_hand = cl_attached_hand + cl_vortex_hand
    cl_total_module = table_rows[check_alpha_deg][2]
    print(f"\n-- Independent hand cross-check at alpha = {check_alpha_deg} deg --")
    print(f"  hand-computed   C_L,total = {cl_total_hand:.10f}")
    print(f"  module-computed C_L,total = {cl_total_module:.10f}")
    print(f"  residual                  = {cl_total_hand - cl_total_module:.3e}")

    # Comparison against the attached-only model at representative angles.
    print(f"\n-- Vortex-lift increment vs. attached-only model --")
    print(f"{'alpha[deg]':>10}  {'dCL':>10}  {'%increase':>10}")
    for alpha_deg in (10.0, 15.0, 20.0):
        cl_a, cl_v, cl_t, _ = table_rows[alpha_deg]
        d_cl = cl_t - cl_a
        pct = 100.0 * d_cl / cl_a
        print(f"{alpha_deg:>10.1f}  {d_cl:>10.6f}  {pct:>9.2f}%")

    # Sweep sensitivity study.
    print(f"\n-- Sweep sensitivity: C_L,vortex(alpha) for Lambda_LE in {SWEEP_ANGLES_DEG} deg --")
    header2 = f"{'alpha[deg]':>10}" + "".join(f"  Lam={s:>4.0f}deg" for s in SWEEP_ANGLES_DEG)
    print(header2)
    for alpha_deg in SENSITIVITY_ALPHAS_DEG:
        row = [vortex_lift_coefficient_deg(alpha_deg, s) for s in SWEEP_ANGLES_DEG]
        print(f"{alpha_deg:>10.1f}" + "".join(f"  {v:>10.6f}" for v in row))

    # +/-20% K_v sensitivity.
    print(f"\n-- Coefficient sensitivity: C_L,vortex(alpha) for K_v = {KV_REFERENCE}*[0.8, 1.0, 1.2] --")
    kv_variants = [0.8 * KV_REFERENCE, KV_REFERENCE, 1.2 * KV_REFERENCE]
    header3 = f"{'alpha[deg]':>10}" + "".join(f"  Kv={k:>5.2f}" for k in kv_variants)
    print(header3)
    for alpha_deg in SENSITIVITY_ALPHAS_DEG:
        row = [
            vortex_lift_coefficient_deg(alpha_deg, sweep_deg, kv_ref=k) for k in kv_variants
        ]
        print(f"{alpha_deg:>10.1f}" + "".join(f"  {v:>9.6f}" for v in row))

    print("\n" + "=" * 78)
    print("Reduced-order Polhamus-inspired vortex-lift model.")
    print("Stall and vortex breakdown are NOT modeled.")
    print("=" * 78)


if __name__ == "__main__":
    main()
