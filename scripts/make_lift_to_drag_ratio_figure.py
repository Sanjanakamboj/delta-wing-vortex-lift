#!/usr/bin/env python3
"""Generate figures/lift_to_drag_ratio.png: L/D vs alpha for both models.

Deterministic: fixed alpha grid, fixed styling, no randomness.
"""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from delta_vortex_lift.attached_flow import attached_flow_CL_deg
from delta_vortex_lift.drag import CD0_DEFAULT, attached_only_drag_coefficient, drag_components, lift_to_drag_ratio
from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.vortex_lift import total_lift_coefficient_deg

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

E_EFFICIENCY = 0.9
ALPHA_MIN_DEG = 0.01  # avoid the exact 0/0 -> 0 point for a cleaner curve start
ALPHA_MAX_DEG = 25.0


def make_figure(save_path: Path) -> None:
    wing = representative_geometry()
    AR = wing.aspect_ratio
    sweep_deg = wing.sweep_LE_deg
    cd0 = CD0_DEFAULT

    alpha_deg = np.linspace(ALPHA_MIN_DEG, ALPHA_MAX_DEG, 251)
    alpha_rad = np.radians(alpha_deg)

    cl_A = attached_flow_CL_deg(alpha_deg, AR, E_EFFICIENCY)
    cd_A = attached_only_drag_coefficient(alpha_rad, AR, E_EFFICIENCY, cd0=cd0)
    ld_A = lift_to_drag_ratio(cl_A, cd_A)

    cl_B = total_lift_coefficient_deg(alpha_deg, AR, E_EFFICIENCY, sweep_deg)
    dc_B = drag_components(alpha_rad, AR, E_EFFICIENCY, np.radians(sweep_deg), cd0=cd0)
    ld_B = lift_to_drag_ratio(cl_B, dc_B.cd_total)

    i_A = int(np.argmax(ld_A))
    i_B = int(np.argmax(ld_B))

    fig, ax = plt.subplots(figsize=(8.5, 5.8), dpi=150)

    ax.axhline(0.0, color="black", linewidth=0.8, zorder=1)
    ax.axvline(0.0, color="black", linewidth=0.8, zorder=1)

    ax.plot(alpha_deg, ld_A, color="#1f77b4", linewidth=2.2, linestyle="--", label="Model A: attached-only")
    ax.plot(alpha_deg, ld_B, color="#d62728", linewidth=2.2, label="Model B: attached + vortex")

    ax.plot(alpha_deg[i_A], ld_A[i_A], marker="o", color="#1f77b4", markersize=7, zorder=5)
    ax.annotate(
        f"best sampled: {ld_A[i_A]:.2f} @ {alpha_deg[i_A]:.1f}°",
        (alpha_deg[i_A], ld_A[i_A]),
        textcoords="offset points",
        xytext=(6, -14),
        fontsize=8,
        color="#1f77b4",
    )
    ax.plot(alpha_deg[i_B], ld_B[i_B], marker="o", color="#d62728", markersize=7, zorder=5)
    ax.annotate(
        f"best sampled: {ld_B[i_B]:.2f} @ {alpha_deg[i_B]:.1f}°",
        (alpha_deg[i_B], ld_B[i_B]),
        textcoords="offset points",
        xytext=(6, 8),
        fontsize=8,
        color="#d62728",
    )

    ax.set_xlabel(r"angle of attack, $\alpha$ [deg]")
    ax.set_ylabel(r"$L/D = C_L/C_D$")
    ax.set_title(
        "Generic Delta Wing — Lift-to-Drag Ratio (Milestone 3)\n"
        rf"$\Lambda_{{LE}} = {sweep_deg:.1f}\degree$, $AR = {AR:.2f}$, $C_{{D0}}={cd0}$ — "
        "reduced-order / conceptual model",
        fontsize=10.3,
    )
    ax.text(
        0.02,
        0.03,
        "Markers show the best SAMPLED L/D within this plotted range only\n"
        "— not a claimed aerodynamic optimum. Stall / vortex breakdown not modeled.",
        transform=ax.transAxes,
        fontsize=8,
        ha="left",
        va="bottom",
        bbox=dict(boxstyle="round", facecolor="white", edgecolor="#888888", alpha=0.9),
    )

    ax.set_xlim(0.0, ALPHA_MAX_DEG)
    ax.set_ylim(bottom=0.0)
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax.legend(loc="center right", fontsize=9, framealpha=0.92)

    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "lift_to_drag_ratio.png"
    make_figure(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
