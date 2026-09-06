#!/usr/bin/env python3
"""Generate figures/lift_with_breakdown.png.

Plots attached-only lift, the original M2 (unbounded) attached+vortex
extrapolation, and the M4 breakdown-limited total lift for each onset case.
Deterministic: fixed alpha grid, fixed styling, no randomness.
"""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from delta_vortex_lift.attached_flow import attached_flow_CL_deg
from delta_vortex_lift.breakdown import BreakdownParameters, post_breakdown_aerodynamics
from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.vortex_lift import total_lift_coefficient_deg

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

E_EFFICIENCY = 0.9
ALPHA_MIN_DEG = 0.0
ALPHA_MAX_DEG = 30.0
M1_M3_DOMAIN_MAX_DEG = 25.0
ONSET_CASES_DEG = [17.0, 20.0, 23.0]


def make_figure(save_path: Path) -> None:
    wing = representative_geometry()
    AR = wing.aspect_ratio
    sweep_deg = wing.sweep_LE_deg
    sweep_rad = wing.sweep_LE_rad

    alpha_deg = np.linspace(ALPHA_MIN_DEG, ALPHA_MAX_DEG, 301)
    alpha_rad = np.radians(alpha_deg)

    cl_attached = attached_flow_CL_deg(alpha_deg, AR, E_EFFICIENCY)
    cl_m2_unbounded = total_lift_coefficient_deg(alpha_deg, AR, E_EFFICIENCY, sweep_deg)

    fig, ax = plt.subplots(figsize=(9, 6.2), dpi=150)

    ax.axvspan(M1_M3_DOMAIN_MAX_DEG, ALPHA_MAX_DEG, color="#888888", alpha=0.07, zorder=0)
    ax.text(
        M1_M3_DOMAIN_MAX_DEG + 0.3,
        0.90,
        "extended domain\n(M4 sensitivity only)",
        transform=ax.get_xaxis_transform(),
        fontsize=7.5,
        color="#666666",
        va="top",
    )

    ax.plot(alpha_deg, cl_attached, color="#1f77b4", linewidth=2.0, linestyle=":", label="attached-only (M1)")
    ax.plot(
        alpha_deg,
        cl_m2_unbounded,
        color="#7f7f7f",
        linewidth=2.0,
        linestyle="--",
        label="original M2/M3 unbounded extrapolation",
    )

    colors = ["#2ca02c", "#1a1a1a", "#d62728"]
    for onset_deg, color in zip(ONSET_CASES_DEG, colors):
        params = BreakdownParameters(alpha_b_rad=np.radians(onset_deg))
        aero = post_breakdown_aerodynamics(alpha_rad, AR, E_EFFICIENCY, sweep_rad, params)
        ax.plot(alpha_deg, aero.cl_total, color=color, linewidth=2.2, label=rf"M4 breakdown-limited, $\alpha_b={onset_deg:.0f}\degree$")

    ax.set_xlabel(r"angle of attack, $\alpha$ [deg]")
    ax.set_ylabel(r"$C_L$")
    ax.set_title(
        "Generic Delta Wing — Lift with Breakdown Sensitivity (Milestone 4)\n"
        rf"$\Lambda_{{LE}}={sweep_deg:.1f}\degree$, $AR={AR:.2f}$ — conceptual sensitivity model",
        fontsize=10.3,
    )
    ax.text(
        0.02,
        0.97,
        "Gray dashed curve is the ORIGINAL M2/M3 extrapolation (no breakdown limit).\n"
        "Colored curves apply the M4 vortex-effectiveness sensitivity model.\n"
        "Not a validated stall/breakdown prediction.",
        transform=ax.transAxes,
        fontsize=8,
        va="top",
        ha="left",
        bbox=dict(boxstyle="round", facecolor="white", edgecolor="#888888", alpha=0.9),
    )

    ax.set_xlim(ALPHA_MIN_DEG, ALPHA_MAX_DEG)
    ax.set_ylim(bottom=0.0)
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax.legend(loc="lower right", fontsize=8.6, framealpha=0.92)

    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "lift_with_breakdown.png"
    make_figure(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
