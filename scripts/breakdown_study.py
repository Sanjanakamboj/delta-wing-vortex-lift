#!/usr/bin/env python3
"""Milestone 4 engineering study: vortex-breakdown / lift-limit sensitivity.

Prints a deterministic engineering table plus geometry, unchanged M1-M3
constants, the breakdown-effectiveness equation, an onset-sensitivity
summary, the predeclared conceptual usable-AoA rule and resulting region,
and an independent numerical cross-check.

    THIS IS NOT A VALIDATED STALL/BREAKDOWN PREDICTION. Every onset angle
    used below is an assumed sensitivity parameter (see DESIGN.md source
    audit), not a measured or predicted breakdown angle for this project's
    generic wing.
"""

import math

import numpy as np

from delta_vortex_lift.attached_flow import finite_wing_lift_curve_slope
from delta_vortex_lift.breakdown import (
    ALPHA_B_DEFAULT_RAD,
    F_POST_DEFAULT,
    TRANSITION_WIDTH_DEFAULT_RAD,
    USABLE_MAX_ALPHA_RAD,
    USABLE_MIN_EFFECTIVENESS,
    USABLE_MIN_LD_FRACTION,
    BreakdownParameters,
    post_breakdown_aerodynamics,
    usable_alpha_limit,
    vortex_effectiveness,
)
from delta_vortex_lift.drag import CD0_DEFAULT, drag_components, lift_to_drag_ratio
from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.vortex_lift import KV_REFERENCE, total_lift_coefficient_deg, vortex_lift_coefficient_deg

E_EFFICIENCY = 0.9
TABLE_ALPHAS_DEG = [5.0, 10.0, 15.0, 20.0, 25.0, 30.0]
FINDINGS_ALPHAS_DEG = [15.0, 20.0, 25.0, 30.0]

ONSET_CASES_DEG = [17.0, 20.0, 23.0]
WIDTH_CASES_DEG = [3.0, 4.0, 5.0]

# Fine grid for best-sampled L/D / usable-region search, matching M3's
# original conceptual domain (0-25 deg) for the pre-breakdown reference.
M3_REFERENCE_ALPHA_DEG = np.linspace(0.01, 25.0, 500)
# Extended domain used ONLY for the breakdown sensitivity study itself.
M4_ALPHA_DEG = np.linspace(0.0, 30.0, 601)


def _m3_reference_ld(AR, e, sweep_deg, cd0):
    """Pre-breakdown (M3) best-sampled L/D within the original 0-25 deg domain."""
    cl = total_lift_coefficient_deg(M3_REFERENCE_ALPHA_DEG, AR, e, sweep_deg)
    dc = drag_components(np.radians(M3_REFERENCE_ALPHA_DEG), AR, e, math.radians(sweep_deg), cd0=cd0)
    ld = lift_to_drag_ratio(cl, dc.cd_total)
    i = int(np.argmax(ld))
    return float(ld[i]), float(M3_REFERENCE_ALPHA_DEG[i])


def main() -> None:
    wing = representative_geometry()
    AR = wing.aspect_ratio
    sweep_deg = wing.sweep_LE_deg
    sweep_rad = wing.sweep_LE_rad
    cd0 = CD0_DEFAULT
    default_params = BreakdownParameters()

    print("=" * 86)
    print("MILESTONE 4 -- VORTEX-BREAKDOWN / LIFT-LIMIT SENSITIVITY STUDY")
    print("This is NOT a validated stall/breakdown prediction. Onset angles are")
    print("assumed sensitivity parameters, not measured or predicted values.")
    print("=" * 86)

    print("\n-- Geometry and M1-M3 constants (all unchanged) --")
    print(f"  aspect ratio AR       = {AR:.4f}")
    print(f"  LE sweep Lambda_LE    = {sweep_deg:.4f} deg")
    print(f"  span efficiency e     = {E_EFFICIENCY}")
    a_rad = finite_wing_lift_curve_slope(AR, E_EFFICIENCY)
    print(f"  attached-flow slope a = {a_rad:.6f} 1/rad")
    print(f"  K_v reference          = {KV_REFERENCE:.4f}")
    print(f"  C_D0 (illustrative)    = {cd0}")

    print(f"\n-- Breakdown-effectiveness equation --")
    print("  f_b(alpha) = f_post + (1-f_post)*0.5*(1 - tanh((alpha - alpha_b)/w)),  w = Delta_alpha/2")
    print("  C_L,vortex,effective = C_L,vortex,pre * f_b(alpha)")
    print("  C_D,vortex,effective = C_L,vortex,effective * tan(alpha)")
    print(f"  Default alpha_b        = {math.degrees(ALPHA_B_DEFAULT_RAD):.1f} deg (assumed, illustrative)")
    print(f"  Default Delta_alpha    = {math.degrees(TRANSITION_WIDTH_DEFAULT_RAD):.1f} deg (assumed, illustrative)")
    print(f"  Default f_post         = {F_POST_DEFAULT} (assumed, illustrative)")
    print("  Source/scope: Polhamus (1966/1968) for the PRE-breakdown terms (unchanged);")
    print("  Wentz & Kohlman (1971) and NASA vortex-core-breakdown literature motivate")
    print("  the QUALITATIVE existence/sweep-dependence of breakdown, not these exact")
    print("  numbers for this project's specific generic wing. See DESIGN.md.")

    print(f"\n-- Representative table, default case (Lambda_LE={sweep_deg:.1f} deg) --")
    header = (
        f"{'a[deg]':>7} {'f_b':>7} {'CLv_pre':>9} {'CLv_eff':>9} {'CLt':>9} "
        f"{'CDt':>9} {'L/D':>8} {'f_v[%]':>7}"
    )
    print(header)
    print("-" * len(header))
    rows = {}
    for alpha_deg in TABLE_ALPHAS_DEG:
        alpha_rad = math.radians(alpha_deg)
        aero = post_breakdown_aerodynamics(alpha_rad, AR, E_EFFICIENCY, sweep_rad, default_params, cd0=cd0)
        f_v_pct = 100.0 * aero.cl_vortex_effective / aero.cl_total if aero.cl_total != 0 else 0.0
        rows[alpha_deg] = aero
        print(
            f"{alpha_deg:>7.1f} {aero.f_b:>7.4f} {aero.cl_vortex_pre:>9.5f} {aero.cl_vortex_effective:>9.5f} "
            f"{aero.cl_total:>9.5f} {aero.cd_total:>9.5f} {aero.lift_to_drag:>8.3f} {f_v_pct:>7.2f}"
        )

    # Independent numerical cross-check at alpha = 22 deg, hand-derived.
    check_alpha_deg = 22.0
    alpha_rad = math.radians(check_alpha_deg)
    a0 = 2.0 * math.pi
    a_hand = a0 / (1.0 + a0 / (math.pi * E_EFFICIENCY * AR))
    cl_attached_hand = a_hand * alpha_rad
    kv_hand = KV_REFERENCE * math.cos(math.radians(65.0)) / math.cos(sweep_rad)
    cl_vortex_pre_hand = kv_hand * math.cos(alpha_rad) * math.sin(alpha_rad) ** 2
    w_hand = TRANSITION_WIDTH_DEFAULT_RAD / 2.0
    fb_hand = F_POST_DEFAULT + (1 - F_POST_DEFAULT) * 0.5 * (1 - math.tanh((alpha_rad - ALPHA_B_DEFAULT_RAD) / w_hand))
    cl_vortex_eff_hand = cl_vortex_pre_hand * fb_hand
    cl_total_hand = cl_attached_hand + cl_vortex_eff_hand
    cdi_hand = cl_attached_hand**2 / (math.pi * E_EFFICIENCY * AR)
    cd_vortex_hand = cl_vortex_eff_hand * math.tan(alpha_rad)
    cd_total_hand = cd0 + cdi_hand + cd_vortex_hand
    aero_module = post_breakdown_aerodynamics(alpha_rad, AR, E_EFFICIENCY, sweep_rad, default_params, cd0=cd0)
    print(f"\n-- Independent hand cross-check at alpha = {check_alpha_deg} deg --")
    print(f"  hand-computed   C_L,total = {cl_total_hand:.10f}, C_D,total = {cd_total_hand:.10f}")
    print(f"  module-computed C_L,total = {aero_module.cl_total:.10f}, C_D,total = {aero_module.cd_total:.10f}")
    print(f"  residual (CL)             = {cl_total_hand - aero_module.cl_total:.3e}")
    print(f"  residual (CD)             = {cd_total_hand - aero_module.cd_total:.3e}")

    # Onset-angle sensitivity (fixed width/f_post).
    print(f"\n-- Breakdown-onset sensitivity (assumed alpha_b cases; Delta_alpha={math.degrees(TRANSITION_WIDTH_DEFAULT_RAD):.0f} deg, f_post={F_POST_DEFAULT} fixed) --")
    header2 = f"{'alpha_b[deg]':>13}" + "".join(f"  a={a:>4.0f}deg" for a in FINDINGS_ALPHAS_DEG)
    print(header2 + "  (columns: C_L,total)")
    ld_ref, ld_ref_alpha_deg = _m3_reference_ld(AR, E_EFFICIENCY, sweep_deg, cd0)
    for onset_deg in ONSET_CASES_DEG:
        params = BreakdownParameters(alpha_b_rad=math.radians(onset_deg))
        row = []
        for a in FINDINGS_ALPHAS_DEG:
            aero = post_breakdown_aerodynamics(math.radians(a), AR, E_EFFICIENCY, sweep_rad, params, cd0=cd0)
            row.append(aero.cl_total)
        print(f"{onset_deg:>13.1f}" + "".join(f"  {v:>9.5f}" for v in row))

    print(f"\n-- Same onset cases: L/D --")
    print(header2)
    for onset_deg in ONSET_CASES_DEG:
        params = BreakdownParameters(alpha_b_rad=math.radians(onset_deg))
        row = []
        for a in FINDINGS_ALPHAS_DEG:
            aero = post_breakdown_aerodynamics(math.radians(a), AR, E_EFFICIENCY, sweep_rad, params, cd0=cd0)
            row.append(aero.lift_to_drag)
        print(f"{onset_deg:>13.1f}" + "".join(f"  {v:>9.4f}" for v in row))

    # angle where effective vortex lift has fallen by 10% and 50% of total degradation.
    print(f"\n-- Degradation-angle summary (default params) --")
    fine_alphas_rad = np.radians(M4_ALPHA_DEG)
    cl_v_pre_fine = np.asarray(
        [vortex_lift_coefficient_deg(a, sweep_deg) for a in M4_ALPHA_DEG]
    )
    aero_fine = post_breakdown_aerodynamics(fine_alphas_rad, AR, E_EFFICIENCY, sweep_rad, default_params, cd0=cd0)
    cl_v_eff_fine = np.asarray(aero_fine.cl_vortex_effective)
    loss_fraction = np.divide(
        cl_v_pre_fine - cl_v_eff_fine, cl_v_pre_fine, out=np.zeros_like(cl_v_pre_fine), where=cl_v_pre_fine != 0
    )
    idx_10pct = np.argmax(loss_fraction >= 0.10) if np.any(loss_fraction >= 0.10) else None
    idx_50pct = np.argmax(loss_fraction >= 0.50) if np.any(loss_fraction >= 0.50) else None
    if idx_10pct is not None:
        print(f"  alpha where effective vortex lift has fallen 10% below pre-breakdown: {M4_ALPHA_DEG[idx_10pct]:.2f} deg")
    if idx_50pct is not None:
        print(f"  alpha where effective vortex lift has fallen 50% below pre-breakdown: {M4_ALPHA_DEG[idx_50pct]:.2f} deg")

    # Transition-width sensitivity (fixed onset/f_post).
    print(f"\n-- Transition-width sensitivity (alpha_b={math.degrees(ALPHA_B_DEFAULT_RAD):.0f} deg, f_post={F_POST_DEFAULT} fixed) --")
    print(header2)
    for width_deg in WIDTH_CASES_DEG:
        params = BreakdownParameters(transition_width_rad=math.radians(width_deg))
        row = []
        for a in FINDINGS_ALPHAS_DEG:
            aero = post_breakdown_aerodynamics(math.radians(a), AR, E_EFFICIENCY, sweep_rad, params, cd0=cd0)
            row.append(aero.cl_total)
        print(f"{width_deg:>13.1f}" + "".join(f"  {v:>9.5f}" for v in row))

    # Unbounded (M2/M3) vs breakdown-limited difference at the top of the M1-M3 domain.
    print(f"\n-- Unbounded (M2/M3) extrapolation vs. breakdown-limited (default case) at alpha=25 deg --")
    cl_unbounded = total_lift_coefficient_deg(25.0, AR, E_EFFICIENCY, sweep_deg)
    dc_unbounded = drag_components(math.radians(25.0), AR, E_EFFICIENCY, sweep_rad, cd0=cd0)
    ld_unbounded = lift_to_drag_ratio(cl_unbounded, dc_unbounded.cd_total)
    aero_25 = rows[25.0]
    print(f"  C_L,total: unbounded = {cl_unbounded:.5f}, breakdown-limited = {aero_25.cl_total:.5f}, "
          f"difference = {aero_25.cl_total - cl_unbounded:.5f} ({100*(aero_25.cl_total-cl_unbounded)/cl_unbounded:.2f}%)")
    print(f"  L/D:       unbounded = {ld_unbounded:.4f}, breakdown-limited = {aero_25.lift_to_drag:.4f}, "
          f"difference = {aero_25.lift_to_drag - ld_unbounded:.4f} ({100*(aero_25.lift_to_drag-ld_unbounded)/ld_unbounded:.2f}%)")

    # Predeclared conceptual usable-AoA rule.
    print(f"\n-- Predeclared conceptual usable-AoA rule (declared BEFORE computing this result) --")
    print(f"  (a) vortex effectiveness f_b(alpha) >= {USABLE_MIN_EFFECTIVENESS}")
    print(f"  (b) past its own L/D peak, breakdown-limited L/D(alpha) >= {USABLE_MIN_LD_FRACTION} x pre-breakdown (M3) reference L/D")
    print(f"  (c) alpha <= {math.degrees(USABLE_MAX_ALPHA_RAD):.0f} deg (original M1-M3 domain)")
    print(f"  M3 reference L/D = {ld_ref:.4f} at alpha = {ld_ref_alpha_deg:.2f} deg (pre-breakdown best sampled, [0,25] deg)")

    print(f"\n-- Resulting conceptual usable-AoA region (\"pre-breakdown operating region\") --")
    usable_edges = {}
    for onset_deg in ONSET_CASES_DEG:
        params = BreakdownParameters(alpha_b_rad=math.radians(onset_deg))
        limit_rad = usable_alpha_limit(AR, E_EFFICIENCY, sweep_rad, ld_ref, params=params, cd0=cd0)
        usable_edges[onset_deg] = math.degrees(limit_rad)
        print(f"  alpha_b={onset_deg:.0f} deg (assumed breakdown onset): usable region = [0, {math.degrees(limit_rad):.2f}] deg")

    if len(set(round(v, 2) for v in usable_edges.values())) == 1:
        print(
            "  NOTE: the usable-region upper edge is IDENTICAL across all three onset\n"
            "  cases. Inspection shows criterion (b) (ordinary L/D decay past its own\n"
            "  peak -- present already in M3, driven by induced drag) binds before\n"
            "  criterion (a) (vortex effectiveness) for every tested alpha_b. The\n"
            "  vortex-breakdown assumption is therefore NOT the limiting factor for this\n"
            "  compound rule at these parameter values -- see the f_b=0.9 threshold\n"
            "  angles below, which DO vary with alpha_b, for the metric that isolates\n"
            "  the breakdown assumption's own sensitivity."
        )

    print(f"\n-- Onset sensitivity of the vortex-effectiveness threshold alone (f_b = 0.9) --")
    for onset_deg in ONSET_CASES_DEG:
        params = BreakdownParameters(alpha_b_rad=math.radians(onset_deg))
        alphas_fine = np.linspace(0.0, 30.0, 3001)
        fb_fine = np.asarray(vortex_effectiveness(np.radians(alphas_fine), params))
        idx = np.argmax(fb_fine < 0.9) if np.any(fb_fine < 0.9) else None
        if idx is not None:
            print(f"  alpha_b={onset_deg:.0f} deg: f_b first drops below 0.9 at alpha = {alphas_fine[idx]:.2f} deg")

    print("\n" + "=" * 86)
    print("This is a SENSITIVITY model, not a validated stall/breakdown prediction.")
    print("Onset angles are assumed parameters. 'Usable region' is a conceptual,")
    print("predeclared-rule construct -- NOT a safe flight envelope or stall boundary.")
    print("=" * 86)


if __name__ == "__main__":
    main()
