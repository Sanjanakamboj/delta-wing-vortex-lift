#!/usr/bin/env python3
"""Generate figures/pitching_moment_decomposition.png.

Plots C_m,attached, C_m,vortex, and C_m,total vs alpha at the nominal
(co-located) force-location model. Deterministic: fixed alpha grid, fixed
styling, no randomness.
"""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.pitching_moment import DEFAULT_MOMENT_PARAMS, pitching_moment_aerodynamics

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

E_EFFICIENCY = 0.9
ALPHA_MIN_DEG = 0.0
ALPHA_MAX_DEG = 30.0


def make_figure(save_path: Path) -> None:
    wing = representative_geometry()
    AR = wing.aspect_ratio
    sweep_rad = wing.sweep_LE_rad
    params = DEFAULT_MOMENT_PARAMS

    alpha_deg = np.linspace(ALPHA_MIN_DEG, ALPHA_MAX_DEG, 301)
    alpha_rad = np.radians(alpha_deg)
    aero = pitching_moment_aerodynamics(alpha_rad, AR, E_EFFICIENCY, sweep_rad, moment_params=params)

    fig, ax = plt.subplots(figsize=(8.5, 6), dpi=150)

    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.axvline(0.0, color="black", linewidth=0.8)

    ax.plot(alpha_deg, aero.cm_attached, color="#1f77b4", linewidth=2.0, linestyle="--", label=r"$C_{m,\mathrm{attached}}$")
    ax.plot(alpha_deg, aero.cm_vortex, color="#d62728", linewidth=2.0, linestyle="-.", label=r"$C_{m,\mathrm{vortex}}$ (breakdown-limited)")
    ax.plot(alpha_deg, aero.cm_total, color="#1a1a1a", linewidth=2.4, label=r"$C_{m,\mathrm{total}}$")

    ax.set_xlabel(r"angle of attack, $\alpha$ [deg]")
    ax.set_ylabel(r"$C_m$ (about $x_{ref}/c_r=" + f"{params.x_ref_hat:.2f}" + r"$)")
    ax.set_title(
        "Generic Delta Wing — Pitching-Moment Decomposition (Milestone 5)\n"
        rf"$x_{{ref}}/c_r={params.x_ref_hat}$, $x_{{attached}}/c_r=x_{{vortex}}/c_r={params.x_attached_hat:.3f}$ "
        "(nominal, co-located) — isolated wing only",
        fontsize=10,
    )
    ax.text(
        0.98,
        0.97,
        "Isolated-wing pitching tendency only — NOT a complete-aircraft\n"
        "stability analysis (no tail, trim, or CG model). Zero crossings\n"
        "are not trim points.",
        transform=ax.transAxes,
        fontsize=8,
        va="top",
        ha="right",
        bbox=dict(boxstyle="round", facecolor="white", edgecolor="#888888", alpha=0.9),
    )

    ax.set_xlim(ALPHA_MIN_DEG, ALPHA_MAX_DEG)
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax.legend(loc="lower left", fontsize=9, framealpha=0.92)

    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "pitching_moment_decomposition.png"
    make_figure(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
