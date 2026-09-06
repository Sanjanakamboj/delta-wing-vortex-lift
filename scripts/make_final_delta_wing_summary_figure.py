#!/usr/bin/env python3
"""Generate figures/final_delta_wing_summary.png -- the single strongest
portfolio summary figure (Milestone 6), 4 panels:
  1. Delta-wing planform geometry.
  2. Lift decomposition.
  3. L/D behavior.
  4. Center-of-pressure / pitching-moment behavior.

Includes a compact annotation box with headline numbers. Deterministic:
fixed alpha grid, fixed styling, no randomness.
"""

import math
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from delta_vortex_lift.attached_flow import attached_flow_CL_deg, finite_wing_lift_curve_slope
from delta_vortex_lift.breakdown import post_breakdown_aerodynamics, usable_alpha_limit
from delta_vortex_lift.drag import CD0_DEFAULT, drag_components, lift_to_drag_ratio
from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.pitching_moment import DEFAULT_MOMENT_PARAMS, pitching_moment_aerodynamics
from delta_vortex_lift.vortex_lift import total_lift_coefficient_deg

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

E_EFFICIENCY = 0.9
ALPHA_MIN_DEG = 0.01
ALPHA_MAX_DEG = 25.0


def make_figure(save_path: Path) -> None:
    wing = representative_geometry()
    AR = wing.aspect_ratio
    sweep_deg = wing.sweep_LE_deg
    sweep_rad = wing.sweep_LE_rad
    cd0 = CD0_DEFAULT

    alpha_deg = np.linspace(ALPHA_MIN_DEG, ALPHA_MAX_DEG, 251)
    alpha_rad = np.radians(alpha_deg)

    fig = plt.figure(figsize=(13, 10.5), dpi=150)
    gs = fig.add_gridspec(2, 2, hspace=0.32, wspace=0.28, top=0.80)
    ax_geo = fig.add_subplot(gs[0, 0])
    ax_lift = fig.add_subplot(gs[0, 1])
    ax_ld = fig.add_subplot(gs[1, 0])
    ax_cp = fig.add_subplot(gs[1, 1])

    # --- Panel 1: geometry ---
    c_r, half_b = wing.root_chord, wing.semi_span
    ax_geo.fill([0, c_r, c_r, 0], [0, half_b, -half_b, 0], color="#8fb8de", edgecolor="#1f3b57", linewidth=1.6)
    ax_geo.plot([0, c_r], [0, 0], linestyle="--", color="#555", linewidth=0.8)
    ax_geo.set_aspect("equal", adjustable="box")
    ax_geo.set_xlabel("x [m]")
    ax_geo.set_ylabel("y [m]")
    ax_geo.set_title(f"(1) Planform: $\\Lambda_{{LE}}={sweep_deg:.0f}\\degree$, $AR={AR:.2f}$", fontsize=10)
    ax_geo.grid(True, linestyle=":", linewidth=0.4, alpha=0.5)

    # --- Panel 2: lift decomposition ---
    cl_attached = attached_flow_CL_deg(alpha_deg, AR, E_EFFICIENCY)
    cl_total = total_lift_coefficient_deg(alpha_deg, AR, E_EFFICIENCY, sweep_deg)
    aero_bd = post_breakdown_aerodynamics(alpha_rad, AR, E_EFFICIENCY, sweep_rad, cd0=cd0)
    cl_limited = np.asarray(aero_bd.cl_total, dtype=float)
    ax_lift.plot(alpha_deg, cl_attached, color="#1f77b4", linewidth=1.8, linestyle=":", label="attached-only")
    ax_lift.plot(alpha_deg, cl_total, color="#7f7f7f", linewidth=1.8, linestyle="--", label="pre-breakdown total")
    ax_lift.plot(alpha_deg, cl_limited, color="#1a1a1a", linewidth=2.2, label="breakdown-limited")
    ax_lift.set_xlabel(r"$\alpha$ [deg]")
    ax_lift.set_ylabel(r"$C_L$")
    ax_lift.set_title("(2) Lift decomposition", fontsize=10)
    ax_lift.set_ylim(bottom=0.0)
    ax_lift.grid(True, linestyle=":", linewidth=0.4, alpha=0.5)
    ax_lift.legend(loc="upper left", fontsize=7.5)

    # --- Panel 3: L/D ---
    ld_limited = np.asarray(aero_bd.lift_to_drag, dtype=float)
    i_best = int(np.argmax(ld_limited))
    ax_ld.plot(alpha_deg, ld_limited, color="#1a1a1a", linewidth=2.2, label="breakdown-limited")
    ax_ld.plot(alpha_deg[i_best], ld_limited[i_best], marker="o", color="#d62728", markersize=6, zorder=5)
    ax_ld.annotate(
        f"best sampled\n{ld_limited[i_best]:.2f} @ {alpha_deg[i_best]:.1f}°",
        (alpha_deg[i_best], ld_limited[i_best]),
        textcoords="offset points",
        xytext=(8, 5),
        fontsize=7.5,
        color="#d62728",
    )
    ax_ld.set_xlabel(r"$\alpha$ [deg]")
    ax_ld.set_ylabel(r"$L/D$")
    ax_ld.set_title("(3) Efficiency (best sampled, not an optimum)", fontsize=10)
    ax_ld.set_ylim(0.0, ld_limited[i_best] * 1.18)
    ax_ld.grid(True, linestyle=":", linewidth=0.4, alpha=0.5)

    # --- Panel 4: center of pressure / Cm ---
    aero_pm = pitching_moment_aerodynamics(alpha_rad, AR, E_EFFICIENCY, sweep_rad)
    cm_total = np.asarray(aero_pm.cm_total, dtype=float)
    ax_cp2 = ax_cp.twinx()
    ax_cp.plot(alpha_deg, np.full_like(alpha_deg, DEFAULT_MOMENT_PARAMS.x_attached_hat), color="#2ca02c", linewidth=2.0, label=r"$x_{cp}/c_r$ (nominal)")
    ax_cp2.plot(alpha_deg, cm_total, color="#9467bd", linewidth=2.0, linestyle="--", label=r"$C_{m,\mathrm{total}}$")
    ax_cp.set_xlabel(r"$\alpha$ [deg]")
    ax_cp.set_ylabel(r"$x_{cp}/c_r$", color="#2ca02c")
    ax_cp2.set_ylabel(r"$C_{m,\mathrm{total}}$", color="#9467bd")
    ax_cp.set_title("(4) Center of pressure / pitching moment", fontsize=10)
    ax_cp.grid(True, linestyle=":", linewidth=0.4, alpha=0.5)
    ax_cp.tick_params(axis="y", labelcolor="#2ca02c")
    ax_cp2.tick_params(axis="y", labelcolor="#9467bd")

    # --- Annotation box ---
    a_slope = finite_wing_lift_curve_slope(AR, E_EFFICIENCY)
    cl_20 = total_lift_coefficient_deg(20.0, AR, E_EFFICIENCY, sweep_deg)
    ld_ref_grid = np.linspace(0.01, 25.0, 2000)
    cl_ref = total_lift_coefficient_deg(ld_ref_grid, AR, E_EFFICIENCY, sweep_deg)
    dc_ref = drag_components(np.radians(ld_ref_grid), AR, E_EFFICIENCY, sweep_rad, cd0=cd0)
    ld_ref = lift_to_drag_ratio(cl_ref, dc_ref.cd_total)
    best_ld = float(np.max(ld_ref))
    usable_edge_deg = math.degrees(usable_alpha_limit(AR, E_EFFICIENCY, sweep_rad, best_ld, cd0=cd0))

    summary_text = (
        rf"$\Lambda_{{LE}}={sweep_deg:.0f}\degree$   $AR={AR:.2f}$   $a={a_slope:.3f}\,\mathrm{{rad}}^{{-1}}$" + "\n"
        rf"$C_{{L,\mathrm{{total}}}}(20\degree)={cl_20:.3f}$   best sampled $L/D={best_ld:.2f}$" + "\n"
        rf"conceptual study region: $[0\degree,\,{usable_edge_deg:.1f}\degree]$" + "\n"
        "Generic reduced-order model — NOT experimentally validated"
    )
    fig.text(
        0.5,
        0.895,
        summary_text,
        ha="center",
        va="top",
        fontsize=9.3,
        bbox=dict(boxstyle="round", facecolor="#fffbe6", edgecolor="#888888", alpha=0.95),
    )

    fig.suptitle(
        "Generic 65° Delta Wing — Reduced-Order Aerodynamic Study Summary",
        fontsize=13,
        y=1.02,
    )
    fig.savefig(save_path, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "final_delta_wing_summary.png"
    make_figure(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
