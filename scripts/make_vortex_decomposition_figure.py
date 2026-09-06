#!/usr/bin/env python3
"""Generate figures/vortex_lift_decomposition.png.

Plots C_L,attached, C_L,vortex, and C_L,total vs alpha for the representative
wing. Deterministic: fixed alpha grid, fixed styling, no randomness.
"""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from delta_vortex_lift.attached_flow import attached_flow_CL_deg
from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.vortex_lift import total_lift_coefficient_deg, vortex_lift_coefficient_deg

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

E_EFFICIENCY = 0.9
ALPHA_MIN_DEG = 0.0
ALPHA_MAX_DEG = 25.0


def make_figure(save_path: Path) -> None:
    wing = representative_geometry()
    AR = wing.aspect_ratio
    sweep_deg = wing.sweep_LE_deg

    alpha_deg = np.linspace(ALPHA_MIN_DEG, ALPHA_MAX_DEG, 251)
    cl_attached = attached_flow_CL_deg(alpha_deg, AR, E_EFFICIENCY)
    cl_vortex = vortex_lift_coefficient_deg(alpha_deg, sweep_deg)
    cl_total = total_lift_coefficient_deg(alpha_deg, AR, E_EFFICIENCY, sweep_deg)

    fig, ax = plt.subplots(figsize=(8.5, 6), dpi=150)

    ax.axhline(0.0, color="black", linewidth=0.8, zorder=1)
    ax.axvline(0.0, color="black", linewidth=0.8, zorder=1)

    ax.plot(
        alpha_deg,
        cl_attached,
        color="#1f77b4",
        linewidth=2.0,
        linestyle="--",
        label=r"attached-flow: $C_{L,\mathrm{attached}} = a\,\alpha$ (Milestone 1, unchanged)",
        zorder=3,
    )
    ax.plot(
        alpha_deg,
        cl_vortex,
        color="#d62728",
        linewidth=2.0,
        linestyle="-.",
        label=r"vortex lift: $C_{L,\mathrm{vortex}} = K_v(\Lambda_{LE})\cos\alpha\,\sin^2\!\alpha$ (Polhamus-style)",
        zorder=3,
    )
    ax.fill_between(alpha_deg, cl_attached, cl_total, color="#d62728", alpha=0.12, zorder=2)
    ax.plot(
        alpha_deg,
        cl_total,
        color="#1a1a1a",
        linewidth=2.6,
        label=r"total: $C_{L,\mathrm{total}} = C_{L,\mathrm{attached}} + C_{L,\mathrm{vortex}}$",
        zorder=4,
    )

    ax.set_xlabel(r"angle of attack, $\alpha$ [deg]")
    ax.set_ylabel(r"$C_L$")
    ax.set_title(
        "Generic Delta Wing — Lift Decomposition (Milestone 2)\n"
        rf"$\Lambda_{{LE}} = {sweep_deg:.1f}\degree$, $AR = {AR:.2f}$ — "
        "reduced-order / conceptual model, not experimentally validated",
        fontsize=10.8,
    )
    ax.text(
        0.02,
        0.97,
        "Polhamus-style vortex-lift term, not the full original theory.\n"
        "Vortex breakdown / stall NOT modeled — do not extrapolate\n"
        "beyond this plotted range.",
        transform=ax.transAxes,
        fontsize=8.2,
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
    out_path = FIGURES_DIR / "vortex_lift_decomposition.png"
    make_figure(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
