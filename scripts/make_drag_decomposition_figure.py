#!/usr/bin/env python3
"""Generate figures/drag_decomposition.png.

Plots C_D0, C_Di,attached, C_D,vortex, and C_D,total vs alpha. Deterministic:
fixed alpha grid, fixed styling, no randomness.
"""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from delta_vortex_lift.drag import CD0_DEFAULT, drag_components
from delta_vortex_lift.geometry import representative_geometry

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

E_EFFICIENCY = 0.9
ALPHA_MIN_DEG = 0.0
ALPHA_MAX_DEG = 25.0


def make_figure(save_path: Path) -> None:
    wing = representative_geometry()
    AR = wing.aspect_ratio
    sweep_deg = wing.sweep_LE_deg
    cd0 = CD0_DEFAULT

    alpha_deg = np.linspace(ALPHA_MIN_DEG, ALPHA_MAX_DEG, 251)
    alpha_rad = np.radians(alpha_deg)
    dc = drag_components(alpha_rad, AR, E_EFFICIENCY, np.radians(sweep_deg), cd0=cd0)
    cd0_line = np.full_like(alpha_deg, cd0)

    fig, ax = plt.subplots(figsize=(8.5, 6), dpi=150)

    ax.axhline(0.0, color="black", linewidth=0.8, zorder=1)
    ax.axvline(0.0, color="black", linewidth=0.8, zorder=1)

    ax.plot(alpha_deg, cd0_line, color="#7f7f7f", linewidth=1.8, linestyle=":", label=r"$C_{D0}$ (illustrative, uncalibrated)")
    ax.plot(
        alpha_deg,
        dc.cdi_attached,
        color="#1f77b4",
        linewidth=2.0,
        linestyle="--",
        label=r"$C_{Di,\mathrm{attached}} = C_{L,\mathrm{attached}}^2/(\pi e\,AR)$",
    )
    ax.plot(
        alpha_deg,
        dc.cd_vortex,
        color="#d62728",
        linewidth=2.0,
        linestyle="-.",
        label=r"$C_{D,\mathrm{vortex}} = C_{L,\mathrm{vortex}}\tan\alpha$ (Polhamus-style)",
    )
    ax.plot(
        alpha_deg,
        dc.cd_total,
        color="#1a1a1a",
        linewidth=2.6,
        label=r"$C_{D,\mathrm{total}} = C_{D0} + C_{Di,\mathrm{attached}} + C_{D,\mathrm{vortex}}$",
    )

    ax.set_xlabel(r"angle of attack, $\alpha$ [deg]")
    ax.set_ylabel(r"$C_D$ [dimensionless]")
    ax.set_title(
        "Generic Delta Wing — Drag-Due-to-Lift Decomposition (Milestone 3)\n"
        rf"$\Lambda_{{LE}} = {sweep_deg:.1f}\degree$, $AR = {AR:.2f}$, $C_{{D0}}={cd0}$ — "
        "reduced-order / conceptual model",
        fontsize=10.3,
    )
    ax.text(
        0.98,
        0.03,
        "Polhamus-style vortex-drag term, not the full original combined theory.\n"
        "Vortex breakdown / stall NOT modeled — do not extrapolate beyond this plotted range.",
        transform=ax.transAxes,
        fontsize=8.2,
        va="bottom",
        ha="right",
        bbox=dict(boxstyle="round", facecolor="white", edgecolor="#888888", alpha=0.9),
    )

    ax.set_xlim(ALPHA_MIN_DEG, ALPHA_MAX_DEG)
    ax.set_ylim(bottom=0.0)
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax.legend(loc="upper left", fontsize=8.6, framealpha=0.92)

    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "drag_decomposition.png"
    make_figure(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
