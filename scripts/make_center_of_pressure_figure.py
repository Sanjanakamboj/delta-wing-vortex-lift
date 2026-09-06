#!/usr/bin/env python3
"""Generate figures/center_of_pressure_vs_alpha.png.

Plots x_cp/c_r vs alpha for the unbounded (M2) and breakdown-limited (M4)
models, at a forward-offset x_vortex sensitivity case (since the nominal,
co-located x_vortex=x_attached model trivially gives a constant x_cp -- see
pitching_moment_study.py's note). Shows x_attached and x_vortex as
horizontal references. No x_cp is plotted at alpha=0 (undefined).
Deterministic: fixed alpha grid, fixed styling, no randomness.
"""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from delta_vortex_lift.attached_flow import attached_flow_CL
from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.pitching_moment import PitchingMomentParameters, center_of_pressure_hat
from delta_vortex_lift.vortex_lift import vortex_lift_coefficient
from delta_vortex_lift.breakdown import effective_vortex_lift_coefficient

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

E_EFFICIENCY = 0.9
ALPHA_MIN_DEG = 0.5  # avoid exact 0 (undefined x_cp)
ALPHA_MAX_DEG = 30.0
X_VORTEX_OFFSET = -0.10  # forward-offset sensitivity case used to illustrate movement


def make_figure(save_path: Path) -> None:
    wing = representative_geometry()
    AR = wing.aspect_ratio
    sweep_rad = wing.sweep_LE_rad

    params = PitchingMomentParameters(x_vortex_hat=PitchingMomentParameters().x_attached_hat + X_VORTEX_OFFSET)

    alpha_deg = np.linspace(ALPHA_MIN_DEG, ALPHA_MAX_DEG, 301)
    alpha_rad = np.radians(alpha_deg)

    cl_attached = attached_flow_CL(alpha_rad, AR, E_EFFICIENCY)
    cl_vortex_unbounded = vortex_lift_coefficient(alpha_rad, sweep_rad)
    cl_vortex_limited = effective_vortex_lift_coefficient(alpha_rad, sweep_rad)

    x_cp_unbounded = center_of_pressure_hat(cl_attached, cl_vortex_unbounded, params)
    x_cp_limited = center_of_pressure_hat(cl_attached, cl_vortex_limited, params)

    fig, ax = plt.subplots(figsize=(8.5, 6), dpi=150)

    ax.axhline(params.x_attached_hat, color="#1f77b4", linewidth=1.4, linestyle=":", label=r"$x_{\mathrm{attached}}/c_r$")

    ax.plot(alpha_deg, x_cp_unbounded, color="#7f7f7f", linewidth=2.0, linestyle="--", label="unbounded (M2) vortex lift")
    ax.plot(alpha_deg, x_cp_limited, color="#1a1a1a", linewidth=2.2, label="breakdown-limited (M4), default onset")

    y_lo = min(np.min(x_cp_unbounded), np.min(x_cp_limited)) - 0.005
    y_hi = params.x_attached_hat + 0.005
    ax.set_ylim(y_lo, y_hi)
    ax.text(
        0.98,
        0.97,
        rf"$x_{{vortex}}/c_r = {params.x_vortex_hat:.4f}$ (below plotted range;"
        f"\nsensitivity case, {X_VORTEX_OFFSET:+.2f} from $x_{{attached}}$)",
        transform=ax.transAxes,
        fontsize=8,
        va="top",
        ha="right",
        color="#d62728",
        bbox=dict(boxstyle="round", facecolor="white", edgecolor="#d62728", alpha=0.9),
    )

    ax.set_xlabel(r"angle of attack, $\alpha$ [deg]")
    ax.set_ylabel(r"$x_{cp}/c_r$")
    ax.set_title(
        "Generic Delta Wing — Center-of-Pressure Movement (Milestone 5)\n"
        rf"Conceptual force-location model — $x_{{vortex}}/c_r = x_{{attached}}/c_r {X_VORTEX_OFFSET:+.2f}$ sensitivity case",
        fontsize=10,
    )
    ax.text(
        0.02,
        0.03,
        r"No point plotted at $\alpha=0^\circ$ (total lift and $x_{cp}$ undefined there)."
        "\n"
        r"Nominal (co-located) model gives a constant $x_{cp}$ — see DESIGN.md.",
        transform=ax.transAxes,
        fontsize=8,
        va="bottom",
        ha="left",
        bbox=dict(boxstyle="round", facecolor="white", edgecolor="#888888", alpha=0.9),
    )

    ax.set_xlim(ALPHA_MIN_DEG, ALPHA_MAX_DEG)
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax.legend(loc="center right", fontsize=8.6, framealpha=0.92)

    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "center_of_pressure_vs_alpha.png"
    make_figure(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
