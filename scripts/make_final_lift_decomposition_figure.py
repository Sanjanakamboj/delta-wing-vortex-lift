#!/usr/bin/env python3
"""Generate figures/final_lift_decomposition.png -- Milestone 6 polished final figure.

Plots attached-flow, vortex, pre-breakdown total, and breakdown-limited
total lift vs alpha for the representative wing. Deterministic: fixed
alpha grid, fixed styling, no randomness.
"""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from delta_vortex_lift.attached_flow import attached_flow_CL_deg
from delta_vortex_lift.breakdown import effective_vortex_lift_coefficient
from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.vortex_lift import total_lift_coefficient_deg, vortex_lift_coefficient_deg

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

E_EFFICIENCY = 0.9
ALPHA_MIN_DEG = 0.0
ALPHA_MAX_DEG = 30.0


def make_figure(save_path: Path) -> None:
    wing = representative_geometry()
    AR = wing.aspect_ratio
    sweep_deg = wing.sweep_LE_deg

    alpha_deg = np.linspace(ALPHA_MIN_DEG, ALPHA_MAX_DEG, 301)
    cl_attached = attached_flow_CL_deg(alpha_deg, AR, E_EFFICIENCY)
    cl_vortex = vortex_lift_coefficient_deg(alpha_deg, sweep_deg)
    cl_total_prebreakdown = total_lift_coefficient_deg(alpha_deg, AR, E_EFFICIENCY, sweep_deg)
    cl_vortex_eff = np.asarray(
        [effective_vortex_lift_coefficient(np.radians(a), wing.sweep_LE_rad) for a in alpha_deg]
    )
    cl_total_limited = cl_attached + cl_vortex_eff

    fig, ax = plt.subplots(figsize=(9, 6.3), dpi=150)

    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.axvline(0.0, color="black", linewidth=0.8)

    ax.plot(alpha_deg, cl_attached, color="#1f77b4", linewidth=2.0, linestyle=":", label=r"attached-flow: $C_{L,\mathrm{attached}}=a\,\alpha$")
    ax.plot(alpha_deg, cl_vortex, color="#ff7f0e", linewidth=1.8, linestyle="--", label=r"vortex (pre-breakdown): $C_{L,\mathrm{vortex}}$")
    ax.plot(alpha_deg, cl_total_prebreakdown, color="#7f7f7f", linewidth=2.0, linestyle="-.", label="pre-breakdown total (M2/M3 extrapolation)")
    ax.plot(alpha_deg, cl_total_limited, color="#1a1a1a", linewidth=2.6, label="breakdown-limited total (M4)")

    onset_deg = 20.0
    ax.axvline(onset_deg, color="#d62728", linewidth=1.0, linestyle=":", alpha=0.7)
    ax.annotate(
        r"assumed breakdown onset $\alpha_b=20\degree$" + "\n(M4 limiter begins changing\nthe extrapolation here)",
        xy=(onset_deg, 1.25),
        xytext=(15.5, 1.85),
        fontsize=8,
        color="#d62728",
        ha="center",
        arrowprops=dict(arrowstyle="->", color="#d62728", linewidth=0.9),
    )
    ax.annotate(
        r"vortex lift becomes a growing fraction of $C_L$"
        "\nas $\\alpha$ increases beyond ~5°",
        xy=(12.0, 0.75),
        xytext=(3.5, 1.55),
        fontsize=8,
        color="#ff7f0e",
        arrowprops=dict(arrowstyle="->", color="#ff7f0e", linewidth=0.9),
    )

    ax.set_xlabel(r"angle of attack, $\alpha$ [deg]")
    ax.set_ylabel(r"$C_L$")
    ax.set_title(
        "Generic 65° Delta Wing — Lift Decomposition\n"
        "Reduced-order generic 65° delta-wing model — conceptual only",
        fontsize=11,
    )
    ax.text(
        0.02,
        0.97,
        rf"$\Lambda_{{LE}}={sweep_deg:.0f}\degree$, $AR={AR:.2f}$ — not experimentally validated",
        transform=ax.transAxes,
        fontsize=8.3,
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
    out_path = FIGURES_DIR / "final_lift_decomposition.png"
    make_figure(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
