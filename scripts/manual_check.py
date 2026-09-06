#!/usr/bin/env python3
"""Manual hand-check of the representative delta wing and attached-flow baseline.

Prints geometry, the attached-flow lift-curve slope, and C_L,attached at a
handful of representative angles of attack, then independently reconstructs
one of those C_L values directly from the documented formula and prints the
residual as a sanity check.

    ATTACHED-FLOW BASELINE ONLY -- VORTEX LIFT NOT YET MODELED.
"""

import math

from delta_vortex_lift.attached_flow import attached_flow_CL_deg, finite_wing_lift_curve_slope
from delta_vortex_lift.geometry import representative_geometry

# Generic, illustrative span-efficiency factor for this reduced-order baseline.
# Not calibrated against any real aircraft; chosen within the documented
# 0.8-1.0 conceptual range (see DESIGN.md).
E_EFFICIENCY = 0.9


def main() -> None:
    wing = representative_geometry()

    print("=" * 70)
    print("GENERIC DELTA WING -- MILESTONE 1 MANUAL CHECK")
    print("Attached-flow baseline only -- vortex lift not yet modeled.")
    print("=" * 70)

    print("\n-- Geometry (generic, illustrative; not a real aircraft) --")
    print(f"  root chord c_r        = {wing.root_chord:.4f} m")
    print(f"  span b                = {wing.span:.4f} m")
    print(f"  semi-span b/2         = {wing.semi_span:.4f} m")
    print(f"  planform area S       = {wing.area:.4f} m^2")
    print(f"  aspect ratio AR       = {wing.aspect_ratio:.4f}")
    print(f"  LE sweep Lambda_LE    = {wing.sweep_LE_deg:.4f} deg ({wing.sweep_LE_rad:.4f} rad)")

    a_rad = finite_wing_lift_curve_slope(wing.aspect_ratio, E_EFFICIENCY)
    # NOTE: a is in 1/rad. To express as 1/deg, multiply by (pi/180) since
    # dCL/d(deg) = dCL/d(rad) * d(rad)/d(deg) = a * (pi/180).
    a_per_deg = a_rad * (math.pi / 180.0)

    print(f"\n-- Attached-flow lift-curve slope (e = {E_EFFICIENCY}) --")
    print(f"  a (finite-wing slope) = {a_rad:.6f} 1/rad")
    print(f"  a (finite-wing slope) = {a_per_deg:.6f} 1/deg")

    alphas_deg = [0.0, 5.0, 10.0, 15.0]
    print(f"\n-- C_L,attached at representative alpha (deg) --")
    cl_values = {}
    for alpha_deg in alphas_deg:
        cl = attached_flow_CL_deg(alpha_deg, wing.aspect_ratio, E_EFFICIENCY)
        cl_values[alpha_deg] = cl
        print(f"  alpha = {alpha_deg:5.1f} deg  ->  C_L,attached = {cl:.6f}")

    # Independent reconstruction of one value directly from the documented
    # formula: C_L = [a0 / (1 + a0/(pi*e*AR))] * alpha_rad, written out here
    # without calling attached_flow_CL_deg, to cross-check the module.
    check_alpha_deg = 10.0
    a0 = 2.0 * math.pi
    AR = wing.aspect_ratio
    e = E_EFFICIENCY
    a_hand = a0 / (1.0 + a0 / (math.pi * e * AR))
    alpha_rad = math.radians(check_alpha_deg)
    cl_hand = a_hand * alpha_rad

    residual = cl_hand - cl_values[check_alpha_deg]
    print(f"\n-- Independent hand-formula reconstruction at alpha = {check_alpha_deg} deg --")
    print(f"  hand-computed C_L,attached = {cl_hand:.10f}")
    print(f"  module-computed C_L,attached = {cl_values[check_alpha_deg]:.10f}")
    print(f"  residual                    = {residual:.3e}")

    print("\n" + "=" * 70)
    print("Attached-flow baseline only -- vortex lift not yet modeled.")
    print("=" * 70)


if __name__ == "__main__":
    main()
