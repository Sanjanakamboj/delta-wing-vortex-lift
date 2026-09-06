#!/usr/bin/env python3
"""Generate figures/final_aerodynamic_trade.png -- Milestone 6 3-panel summary.

Panel 1: C_L vs alpha (attached-only, attached+vortex breakdown-limited).
Panel 2: C_D vs alpha (same two models).
Panel 3: L/D vs alpha (same two models), best-sampled points marked.

Deterministic: fixed alpha grid, fixed styling, no randomness.
"""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from delta_vortex_lift.attached_flow import attached_flow_CL_deg
from delta_vortex_lift.breakdown import post_breakdown_aerodynamics
from delta_vortex_lift.drag import CD0_DEFAULT, attached_only_drag_coefficient, lift_to_drag_ratio
from delta_vortex_lift.geometry import representative_geometry

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

E_EFFICIENCY = 0.9
ALPHA_MIN_DEG = 0.01
ALPHA_MAX_DEG = 25.0


def make_figure(save_path: Path) -> None:
    wing = representative_geometry()
    AR = wing.aspect_ratio
    sweep_rad = wing.sweep_LE_rad
    cd0 = CD0_DEFAULT

    alpha_deg = np.linspace(ALPHA_MIN_DEG, ALPHA_MAX_DEG, 251)
    alpha_rad = np.radians(alpha_deg)

    cl_A = attached_flow_CL_deg(alpha_deg, AR, E_EFFICIENCY)
    cd_A = attached_only_drag_coefficient(alpha_rad, AR, E_EFFICIENCY, cd0=cd0)
    ld_A = lift_to_drag_ratio(cl_A, cd_A)

    aero_B = post_breakdown_aerodynamics(alpha_rad, AR, E_EFFICIENCY, sweep_rad, cd0=cd0)
    cl_B = np.asarray(aero_B.cl_total, dtype=float)
    cd_B = np.asarray(aero_B.cd_total, dtype=float)
    ld_B = np.asarray(aero_B.lift_to_drag, dtype=float)

    i_A = int(np.argmax(ld_A))
    i_B = int(np.argmax(ld_B))

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), dpi=150)
    ax1, ax2, ax3 = axes

    for ax, yA, yB, ylabel, title in [
        (ax1, cl_A, cl_B, r"$C_L$", r"(a) Lift"),
        (ax2, cd_A, cd_B, r"$C_D$", r"(b) Drag"),
        (ax3, ld_A, ld_B, r"$L/D$", r"(c) Efficiency"),
    ]:
        ax.plot(alpha_deg, yA, color="#1f77b4", linewidth=2.0, linestyle="--", label="attached-only")
        ax.plot(alpha_deg, yB, color="#d62728", linewidth=2.2, label="attached+vortex (breakdown-limited)")
        ax.set_xlabel(r"$\alpha$ [deg]")
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontsize=10.5)
        ax.set_xlim(ALPHA_MIN_DEG, ALPHA_MAX_DEG)
        ax.set_ylim(bottom=0.0)
        ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)

    ax3.plot(alpha_deg[i_A], ld_A[i_A], marker="o", color="#1f77b4", markersize=6, zorder=5)
    ax3.plot(alpha_deg[i_B], ld_B[i_B], marker="o", color="#d62728", markersize=6, zorder=5)
    ax3.annotate(
        f"best sampled\n{ld_A[i_A]:.2f} @ {alpha_deg[i_A]:.1f}°",
        (alpha_deg[i_A], ld_A[i_A]),
        textcoords="offset points",
        xytext=(10, -35),
        fontsize=7.5,
        color="#1f77b4",
    )
    ax3.annotate(
        f"best sampled\n{ld_B[i_B]:.2f} @ {alpha_deg[i_B]:.1f}°",
        (alpha_deg[i_B], ld_B[i_B]),
        textcoords="offset points",
        xytext=(10, -55),
        fontsize=7.5,
        color="#d62728",
    )
    ax3.set_ylim(top=max(np.max(ld_A), np.max(ld_B)) * 1.15)
    ax1.legend(loc="upper left", fontsize=8.5)

    fig.suptitle(
        "Generic 65° Delta Wing — Aerodynamic Trade Summary (Milestone 6)\n"
        "Reduced-order conceptual model — not experimentally validated. \"Best sampled\" is not a claimed optimum.",
        fontsize=11.5,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(save_path)
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "final_aerodynamic_trade.png"
    make_figure(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
