#!/usr/bin/env python3
"""Generate figures/lift_drag_polar.png: C_L vs C_D for both models.

Deterministic: fixed alpha grid, fixed styling, no randomness.
"""

import math
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from delta_vortex_lift.attached_flow import attached_flow_CL_deg
from delta_vortex_lift.drag import CD0_DEFAULT, attached_only_drag_coefficient, drag_components
from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.vortex_lift import total_lift_coefficient_deg

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

E_EFFICIENCY = 0.9
ALPHA_MIN_DEG = 0.0
ALPHA_MAX_DEG = 25.0
ANNOTATE_ALPHAS_DEG = [5.0, 10.0, 15.0, 20.0, 25.0]


def make_figure(save_path: Path) -> None:
    wing = representative_geometry()
    AR = wing.aspect_ratio
    sweep_deg = wing.sweep_LE_deg
    cd0 = CD0_DEFAULT

    alpha_deg = np.linspace(ALPHA_MIN_DEG, ALPHA_MAX_DEG, 251)
    alpha_rad = np.radians(alpha_deg)

    cl_A = attached_flow_CL_deg(alpha_deg, AR, E_EFFICIENCY)
    cd_A = attached_only_drag_coefficient(alpha_rad, AR, E_EFFICIENCY, cd0=cd0)

    cl_B = total_lift_coefficient_deg(alpha_deg, AR, E_EFFICIENCY, sweep_deg)
    dc_B = drag_components(alpha_rad, AR, E_EFFICIENCY, np.radians(sweep_deg), cd0=cd0)
    cd_B = dc_B.cd_total

    fig, ax = plt.subplots(figsize=(7.5, 6.5), dpi=150)

    ax.plot(cd_A, cl_A, color="#1f77b4", linewidth=2.2, linestyle="--", label="Model A: attached-only")
    ax.plot(cd_B, cl_B, color="#d62728", linewidth=2.2, label="Model B: attached + vortex")

    for a_deg in ANNOTATE_ALPHAS_DEG:
        cl_a_pt = attached_flow_CL_deg(a_deg, AR, E_EFFICIENCY)
        cd_a_pt = attached_only_drag_coefficient(math.radians(a_deg), AR, E_EFFICIENCY, cd0=cd0)
        cl_b_pt = total_lift_coefficient_deg(a_deg, AR, E_EFFICIENCY, sweep_deg)
        dc_pt = drag_components(math.radians(a_deg), AR, E_EFFICIENCY, math.radians(sweep_deg), cd0=cd0)
        ax.plot(cd_a_pt, cl_a_pt, marker="o", color="#1f77b4", markersize=4, zorder=5)
        ax.plot(dc_pt.cd_total, cl_b_pt, marker="o", color="#d62728", markersize=4, zorder=5)
        ax.annotate(
            rf"{a_deg:.0f}$\degree$",
            (dc_pt.cd_total, cl_b_pt),
            textcoords="offset points",
            xytext=(6, 4),
            fontsize=7.5,
            color="#d62728",
        )

    ax.set_xlabel(r"$C_D$ [dimensionless]")
    ax.set_ylabel(r"$C_L$ [dimensionless]")
    ax.set_title(
        "Generic Delta Wing — Aerodynamic Polar (Milestone 3)\n"
        rf"$\Lambda_{{LE}} = {sweep_deg:.1f}\degree$, $AR = {AR:.2f}$, $C_{{D0}}={cd0}$" + "\n"
        "Reduced-order / conceptual model — not experimentally validated",
        fontsize=10.2,
    )
    ax.text(
        0.98,
        0.03,
        r"Points labeled by $\alpha$ [deg]. Stall / vortex breakdown not modeled.",
        transform=ax.transAxes,
        fontsize=8,
        ha="right",
        va="bottom",
        bbox=dict(boxstyle="round", facecolor="white", edgecolor="#888888", alpha=0.9),
    )

    ax.set_xlim(left=0.0)
    ax.set_ylim(bottom=0.0)
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax.legend(loc="upper left", fontsize=9, framealpha=0.92)

    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "lift_drag_polar.png"
    make_figure(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
