#!/usr/bin/env python3
"""Generate figures/pitching_moment_sensitivity.png.

Two panels:
  (a) C_m,total vs alpha for x_vortex/c_r = nominal +/- 0.10.
  (b) x_cp/c_r vs alpha for the same three cases.

Deterministic: fixed alpha grid, fixed styling, no randomness.
"""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.pitching_moment import PitchingMomentParameters, pitching_moment_aerodynamics

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

E_EFFICIENCY = 0.9
ALPHA_MIN_DEG = 0.5
ALPHA_MAX_DEG = 30.0
OFFSETS = [-0.10, 0.0, 0.10]


def make_figure(save_path: Path) -> None:
    wing = representative_geometry()
    AR = wing.aspect_ratio
    sweep_rad = wing.sweep_LE_rad
    x_attached_hat = PitchingMomentParameters().x_attached_hat

    alpha_deg = np.linspace(ALPHA_MIN_DEG, ALPHA_MAX_DEG, 301)
    alpha_rad = np.radians(alpha_deg)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.6), dpi=150)

    colors = ["#2ca02c", "#1a1a1a", "#d62728"]
    for offset, color in zip(OFFSETS, colors):
        params = PitchingMomentParameters(x_vortex_hat=x_attached_hat + offset)
        aero = pitching_moment_aerodynamics(alpha_rad, AR, E_EFFICIENCY, sweep_rad, moment_params=params)
        label = rf"$x_{{vortex}}/c_r = x_{{attached}}/c_r {offset:+.2f}$"
        ax1.plot(alpha_deg, np.asarray(aero.cm_total, dtype=float), color=color, linewidth=2.0, label=label)
        ax2.plot(alpha_deg, np.asarray(aero.x_cp_hat, dtype=float), color=color, linewidth=2.0, label=label)

    ax1.axhline(0.0, color="black", linewidth=0.7)
    ax1.set_xlabel(r"angle of attack, $\alpha$ [deg]")
    ax1.set_ylabel(r"$C_{m,\mathrm{total}}$")
    ax1.set_title(r"(a) $C_{m,\mathrm{total}}$ sensitivity to $x_{vortex}$", fontsize=10.5)
    ax1.set_xlim(ALPHA_MIN_DEG, ALPHA_MAX_DEG)
    ax1.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax1.legend(loc="lower left", fontsize=8)

    ax2.axhline(x_attached_hat, color="#888888", linewidth=1.0, linestyle=":")
    ax2.set_xlabel(r"angle of attack, $\alpha$ [deg]")
    ax2.set_ylabel(r"$x_{cp}/c_r$")
    ax2.set_title(r"(b) $x_{cp}/c_r$ sensitivity to $x_{vortex}$", fontsize=10.5)
    ax2.set_xlim(ALPHA_MIN_DEG, ALPHA_MAX_DEG)
    ax2.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax2.legend(loc="upper right", fontsize=8)

    fig.suptitle(
        "Generic Delta Wing — Force-Location Sensitivity (Milestone 5)\n"
        "Force-location sensitivity — not aerodynamic calibration",
        fontsize=11.5,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(save_path)
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "pitching_moment_sensitivity.png"
    make_figure(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
