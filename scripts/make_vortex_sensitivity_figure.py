#!/usr/bin/env python3
"""Generate figures/vortex_lift_sensitivity.png.

Two panels:
  (a) C_L,vortex vs alpha for Lambda_LE = 55, 65, 75 deg (nominal K_v).
  (b) Vortex-lift fraction f_v = C_L,vortex/C_L,total vs alpha, for the
      representative sweep, comparing nominal K_v against +/-20% K_v.

Deterministic: fixed alpha grid, fixed styling, no randomness.
"""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.vortex_lift import KV_REFERENCE, vortex_fraction, vortex_lift_coefficient_deg

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

E_EFFICIENCY = 0.9
ALPHA_MIN_DEG = 0.0
ALPHA_MAX_DEG = 25.0
SWEEP_ANGLES_DEG = [55.0, 65.0, 75.0]
KV_FRACTIONS = [0.8, 1.0, 1.2]


def make_figure(save_path: Path) -> None:
    wing = representative_geometry()
    AR = wing.aspect_ratio
    nominal_sweep_deg = wing.sweep_LE_deg

    alpha_deg = np.linspace(ALPHA_MIN_DEG, ALPHA_MAX_DEG, 251)
    alpha_rad = np.radians(alpha_deg)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.5), dpi=150)

    # --- Panel (a): sweep sensitivity of vortex lift ---
    colors_sweep = ["#2ca02c", "#1f77b4", "#d62728"]
    for sweep_deg, color in zip(SWEEP_ANGLES_DEG, colors_sweep):
        cl_v = vortex_lift_coefficient_deg(alpha_deg, sweep_deg)
        style = "-" if sweep_deg == nominal_sweep_deg else "--"
        label = rf"$\Lambda_{{LE}} = {sweep_deg:.0f}\degree$"
        if sweep_deg == nominal_sweep_deg:
            label += " (representative wing)"
        ax1.plot(alpha_deg, cl_v, color=color, linewidth=2.0, linestyle=style, label=label)

    ax1.axhline(0.0, color="black", linewidth=0.7)
    ax1.axvline(0.0, color="black", linewidth=0.7)
    ax1.set_xlabel(r"angle of attack, $\alpha$ [deg]")
    ax1.set_ylabel(r"$C_{L,\mathrm{vortex}}$")
    ax1.set_title(r"(a) Sweep sensitivity of $C_{L,\mathrm{vortex}}$" + "\n" + r"($K_v \propto 1/\cos\Lambda_{LE}$, Polhamus eq. 13)", fontsize=10)
    ax1.set_xlim(ALPHA_MIN_DEG, ALPHA_MAX_DEG)
    ax1.set_ylim(bottom=0.0)
    ax1.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax1.legend(loc="upper left", fontsize=8.6)

    # --- Panel (b): vortex fraction vs alpha, K_v +/- 20% ---
    colors_kv = ["#9467bd", "#1a1a1a", "#ff7f0e"]
    for frac, color in zip(KV_FRACTIONS, colors_kv):
        kv = KV_REFERENCE * frac
        f_v = vortex_fraction(alpha_rad, AR, E_EFFICIENCY, np.radians(nominal_sweep_deg), kv_ref=kv) * 100.0
        style = "-" if frac == 1.0 else "--"
        label = rf"$K_v = {frac:.1f}\times K_{{v,\mathrm{{ref}}}}$" + (" (nominal)" if frac == 1.0 else "")
        ax2.plot(alpha_deg, f_v, color=color, linewidth=2.0, linestyle=style, label=label)

    ax2.axhline(0.0, color="black", linewidth=0.7)
    ax2.axvline(0.0, color="black", linewidth=0.7)
    ax2.set_xlabel(r"angle of attack, $\alpha$ [deg]")
    ax2.set_ylabel(r"vortex-lift fraction, $f_v = C_{L,\mathrm{vortex}}/C_{L,\mathrm{total}}$ [%]")
    ax2.set_title(
        rf"(b) Vortex-lift fraction vs. $\alpha$ at $\Lambda_{{LE}}={nominal_sweep_deg:.0f}\degree$"
        "\n"
        r"$\pm20\%$ sensitivity to illustrative coefficient $K_v$",
        fontsize=10,
    )
    ax2.set_xlim(ALPHA_MIN_DEG, ALPHA_MAX_DEG)
    ax2.set_ylim(bottom=0.0)
    ax2.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax2.legend(loc="upper left", fontsize=8.6)

    fig.suptitle(
        "Generic Delta Wing — Vortex-Lift Sensitivity (Milestone 2)\n"
        "Reduced-order / conceptual model — stall and vortex breakdown not modeled",
        fontsize=11.5,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(save_path)
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "vortex_lift_sensitivity.png"
    make_figure(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
