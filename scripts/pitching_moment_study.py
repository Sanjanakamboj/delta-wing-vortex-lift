#!/usr/bin/env python3
"""Milestone 5 engineering study: pitching moment and center of pressure.

Prints geometry/moment-reference values, the sign convention, a
representative table, a breakdown comparison (unbounded M2 vs. M4
breakdown-limited), a force-location sensitivity study, a local
dC_m/d(alpha) "isolated-wing static pitching tendency" estimate, and an
independent numerical cross-check.

    THIS IS NOT A COMPLETE-AIRCRAFT STABILITY ANALYSIS. No tail, elevator,
    trim solution, CG model, or dynamic-stability derivative is included.
"""

import math

from delta_vortex_lift.attached_flow import attached_flow_CL
from delta_vortex_lift.breakdown import DEFAULT_BREAKDOWN_PARAMS
from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.pitching_moment import (
    C_REF_HAT_DEFAULT,
    X_ATTACHED_HAT_DEFAULT,
    X_REF_HAT_DEFAULT,
    X_VORTEX_HAT_DEFAULT,
    PitchingMomentParameters,
    pitching_moment_aerodynamics,
    total_moment_coefficient,
)
from delta_vortex_lift.vortex_lift import KV_REFERENCE, vortex_lift_coefficient

E_EFFICIENCY = 0.9
TABLE_ALPHAS_DEG = [5.0, 10.0, 15.0, 20.0, 25.0, 30.0]
FINDINGS_ALPHAS_DEG = [10.0, 15.0, 20.0, 25.0]
X_VORTEX_OFFSETS = [-0.10, 0.0, 0.10]  # relative to X_VORTEX_HAT_DEFAULT
X_REF_CASES = [0.40, 0.50, 0.60]


def main() -> None:
    wing = representative_geometry()
    AR = wing.aspect_ratio
    sweep_deg = wing.sweep_LE_deg
    sweep_rad = wing.sweep_LE_rad
    default_params = PitchingMomentParameters()

    print("=" * 88)
    print("MILESTONE 5 -- PITCHING MOMENT AND CENTER-OF-PRESSURE STUDY")
    print("Isolated-wing conceptual study only. NOT a complete-aircraft")
    print("stability analysis: no tail, elevator, trim solution, or CG model.")
    print("=" * 88)

    print("\n## Geometry / moment reference")
    print(f"  root chord c_r         = {wing.root_chord:.4f} m")
    print(f"  MAC                    = {wing.mean_aerodynamic_chord:.4f} m  (= (2/3) c_r)")
    print(f"  MAC leading-edge x     = {wing.mac_leading_edge_x:.4f} m  (= c_r/3, informational only)")
    print(f"  x_ref/c_r              = {default_params.x_ref_hat}  (matches NASA TN D-6994 Cm reference)")
    print(f"  x_attached/c_r         = {default_params.x_attached_hat:.4f}  (Jones 1946 slender-wing centroid, 2/3)")
    print(f"  x_vortex/c_r (nominal) = {default_params.x_vortex_hat:.4f}  (co-located nominal; AR<=2 per Snyder & Lamar)")
    print(f"  c_ref/c_r              = {default_params.c_ref_hat:.4f}  (= MAC/c_r)")
    print(f"  C_m0                   = {default_params.cm0}  (symmetric wing, no source justifies nonzero)")

    print("\n## Sign convention")
    print("  x positive aft from the apex; L positive up. A force AFT of x_ref produces")
    print("  a NOSE-DOWN (negative) C_m; a force FORWARD of x_ref produces nose-up (positive).")
    print("  C_m = -C_L * (x_force - x_ref) / c_ref  (derived in DESIGN.md/pitching_moment.py)")

    print(f"\n## Representative table (Lambda_LE={sweep_deg:.1f} deg, nominal force locations)")
    header = (
        f"{'a[deg]':>7} {'f_b':>7} {'CLa':>8} {'CLv_eff':>8} {'CLt':>8} {'f_v[%]':>7} "
        f"{'xcp/cr':>8} {'Cm_a':>9} {'Cm_v':>9} {'Cm_t':>9}"
    )
    print(header)
    print("-" * len(header))
    rows = {}
    for alpha_deg in TABLE_ALPHAS_DEG:
        alpha = math.radians(alpha_deg)
        aero = pitching_moment_aerodynamics(alpha, AR, E_EFFICIENCY, sweep_rad)
        f_v_pct = 100.0 * aero.cl_vortex_effective / aero.cl_total if aero.cl_total != 0 else 0.0
        rows[alpha_deg] = aero
        print(
            f"{alpha_deg:>7.1f} {aero.f_b:>7.4f} {aero.cl_attached:>8.4f} {aero.cl_vortex_effective:>8.4f} "
            f"{aero.cl_total:>8.4f} {f_v_pct:>7.2f} {aero.x_cp_hat:>8.4f} "
            f"{aero.cm_attached:>9.5f} {aero.cm_vortex:>9.5f} {aero.cm_total:>9.5f}"
        )

    # Independent numerical cross-check at alpha = 19 deg.
    check_alpha_deg = 19.0
    alpha_rad = math.radians(check_alpha_deg)
    a0 = 2.0 * math.pi
    a_hand = a0 / (1.0 + a0 / (math.pi * E_EFFICIENCY * AR))
    cl_a_hand = a_hand * alpha_rad
    kv_hand = KV_REFERENCE * math.cos(math.radians(65.0)) / math.cos(sweep_rad)
    cl_v_pre_hand = kv_hand * math.cos(alpha_rad) * math.sin(alpha_rad) ** 2
    bp = DEFAULT_BREAKDOWN_PARAMS
    w_hand = bp.transition_width_rad / 2.0
    fb_hand = bp.f_post + (1 - bp.f_post) * 0.5 * (1 - math.tanh((alpha_rad - bp.alpha_b_rad) / w_hand))
    cl_v_eff_hand = cl_v_pre_hand * fb_hand
    cm_a_hand = -cl_a_hand * (X_ATTACHED_HAT_DEFAULT - X_REF_HAT_DEFAULT) / C_REF_HAT_DEFAULT
    cm_v_hand = -cl_v_eff_hand * (X_VORTEX_HAT_DEFAULT - X_REF_HAT_DEFAULT) / C_REF_HAT_DEFAULT
    cm_total_hand = cm_a_hand + cm_v_hand
    aero_module = pitching_moment_aerodynamics(alpha_rad, AR, E_EFFICIENCY, sweep_rad)
    print(f"\n## Independent check at alpha = {check_alpha_deg} deg (force x arm, by hand)")
    print(f"  hand-computed   C_m,total = {cm_total_hand:.10f}")
    print(f"  module-computed C_m,total = {aero_module.cm_total:.10f}")
    print(f"  residual                  = {cm_total_hand - aero_module.cm_total:.3e}")

    # Breakdown comparison: unbounded M2 vortex lift vs M4 breakdown-limited.
    print(f"\n## Breakdown comparison: unbounded (M2) vs. breakdown-limited (M4) moment, at high alpha")
    header2 = f"{'a[deg]':>7} {'Cm_t (unbounded)':>18} {'Cm_t (limited)':>16} {'d(Cm_t)':>10}"
    print(header2)
    for alpha_deg in (20.0, 25.0, 30.0):
        alpha = math.radians(alpha_deg)
        cl_a = attached_flow_CL(alpha, AR, E_EFFICIENCY)
        cl_v_unbounded = vortex_lift_coefficient(alpha, sweep_rad)
        cm_unbounded = total_moment_coefficient(cl_a, cl_v_unbounded)
        cm_limited = rows[alpha_deg].cm_total
        print(f"{alpha_deg:>7.1f} {cm_unbounded:>18.5f} {cm_limited:>16.5f} {cm_limited - cm_unbounded:>10.5f}")

    # Sensitivity to vortex force location.
    print(f"\n## Sensitivity to vortex force-location assumption (x_vortex/c_r = {X_VORTEX_HAT_DEFAULT:.4f} +/- 0.10)")
    header3 = f"{'a[deg]':>7}" + "".join(f"  x_v={X_VORTEX_HAT_DEFAULT+d:>6.4f}" for d in X_VORTEX_OFFSETS)
    print(header3 + "  (columns: C_m,total)")
    for alpha_deg in FINDINGS_ALPHAS_DEG:
        alpha = math.radians(alpha_deg)
        row = []
        for d in X_VORTEX_OFFSETS:
            params = PitchingMomentParameters(x_vortex_hat=X_VORTEX_HAT_DEFAULT + d)
            aero = pitching_moment_aerodynamics(alpha, AR, E_EFFICIENCY, sweep_rad, moment_params=params)
            row.append(aero.cm_total)
        print(f"{alpha_deg:>7.1f}" + "".join(f"  {v:>12.5f}" for v in row))

    print(f"\n## Same offsets: x_cp/c_r")
    print(header3)
    for alpha_deg in FINDINGS_ALPHAS_DEG:
        alpha = math.radians(alpha_deg)
        row = []
        for d in X_VORTEX_OFFSETS:
            params = PitchingMomentParameters(x_vortex_hat=X_VORTEX_HAT_DEFAULT + d)
            aero = pitching_moment_aerodynamics(alpha, AR, E_EFFICIENCY, sweep_rad, moment_params=params)
            row.append(aero.x_cp_hat)
        print(f"{alpha_deg:>7.1f}" + "".join(f"  {v:>12.5f}" for v in row))

    print(f"\n## NOTE on the co-located nominal case")
    print("  Because the nominal model sets x_vortex/c_r EQUAL to x_attached/c_r (both source-")
    print("  motivated, see DESIGN.md), x_cp/c_r is IDENTICALLY 2/3 for every alpha in the nominal")
    print("  case -- the co-located assumption trivially produces no x_cp movement. Any x_cp")
    print("  movement shown above therefore isolates the effect of the assumed x_vortex OFFSET,")
    print("  which is the genuinely uncertain part of this reduced-order model.")

    # x_ref sensitivity.
    print(f"\n## Sensitivity to moment reference point x_ref/c_r")
    header4 = f"{'a[deg]':>7}" + "".join(f"  x_ref={x:>4.2f}" for x in X_REF_CASES)
    print(header4 + "  (columns: C_m,total, nominal force locations)")
    for alpha_deg in FINDINGS_ALPHAS_DEG:
        alpha = math.radians(alpha_deg)
        row = []
        for x_ref in X_REF_CASES:
            params = PitchingMomentParameters(x_ref_hat=x_ref)
            aero = pitching_moment_aerodynamics(alpha, AR, E_EFFICIENCY, sweep_rad, moment_params=params)
            row.append(aero.cm_total)
        print(f"{alpha_deg:>7.1f}" + "".join(f"  {v:>10.5f}" for v in row))

    # Local static pitching tendency dCm/dalpha over one stated interval.
    print(f"\n## Isolated-wing static pitching tendency (NOT 'aircraft stability')")
    a1_deg, a2_deg = 10.0, 15.0
    cm1 = pitching_moment_aerodynamics(math.radians(a1_deg), AR, E_EFFICIENCY, sweep_rad).cm_total
    cm2 = pitching_moment_aerodynamics(math.radians(a2_deg), AR, E_EFFICIENCY, sweep_rad).cm_total
    dcm_dalpha_per_rad = (cm2 - cm1) / math.radians(a2_deg - a1_deg)
    print(f"  local dC_m/d(alpha) over alpha=[{a1_deg},{a2_deg}] deg (nominal locations, about x_ref={X_REF_HAT_DEFAULT}c_r):")
    print(f"    = {dcm_dalpha_per_rad:.4f} 1/rad  ({math.radians(1.0)*dcm_dalpha_per_rad:.5f} 1/deg)")
    print("  This describes the ISOLATED WING's pitching tendency about the chosen reference")
    print("  point over this interval only -- it is NOT a claim about complete-aircraft")
    print("  longitudinal stability, which would require a fuselage, tail, and CG model.")

    print("\n" + "=" * 88)
    print("Conceptual force-location model. NOT a complete-aircraft stability analysis.")
    print("=" * 88)


if __name__ == "__main__":
    main()
