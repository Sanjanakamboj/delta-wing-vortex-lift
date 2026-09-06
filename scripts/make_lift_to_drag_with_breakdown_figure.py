#!/usr/bin/env python3
"""Generate figures/lift_to_drag_with_breakdown.png.

Plots L/D vs alpha for the original M3 model and the M4 onset-sensitivity
cases. Deterministic: fixed alpha grid, fixed styling, no randomness.
"""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from delta_vortex_lift.breakdown import BreakdownParameters, post_breakdown_aerodynamics
from delta_vortex_lift.drag import CD0_DEFAULT, drag_components, lift_to_drag_ratio
from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.vortex_lift import total_lift_coefficient_deg

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

E_EFFICIENCY = 0.9
ALPHA_MIN_DEG = 0.01
ALPHA_MAX_DEG = 30.0
M1_M3_DOMAIN_MAX_DEG = 25.0
ONSET_CASES_DEG = [17.0, 20.0, 23.0]


def make_figure(save_path: Path) -> None:
    wing = representative_geometry()
    AR = wing.aspect_ratio
    sweep_deg = wing.sweep_LE_deg
    sweep_rad = wing.sweep_LE_rad
    cd0 = CD0_DEFAULT

    alpha_deg = np.linspace(ALPHA_MIN_DEG, ALPHA_MAX_DEG, 301)
    alpha_rad = np.radians(alpha_deg)

    cl_m3 = total_lift_coefficient_deg(alpha_deg, AR, E_EFFICIENCY, sweep_deg)
    dc_m3 = drag_components(alpha_rad, AR, E_EFFICIENCY, sweep_rad, cd0=cd0)
    ld_m3 = lift_to_drag_ratio(cl_m3, dc_m3.cd_total)

    fig, ax = plt.subplots(figsize=(9, 6.2), dpi=150)

    ax.axvspan(M1_M3_DOMAIN_MAX_DEG, ALPHA_MAX_DEG, color="#888888", alpha=0.07, zorder=0)

    ax.plot(alpha_deg, ld_m3, color="#7f7f7f", linewidth=2.0, linestyle="--", label="original M3 model (no breakdown limit)")

    colors = ["#2ca02c", "#1a1a1a", "#d62728"]
    best_pts = []
    for onset_deg, color in zip(ONSET_CASES_DEG, colors):
        params = BreakdownParameters(alpha_b_rad=np.radians(onset_deg))
        aero = post_breakdown_aerodynamics(alpha_rad, AR, E_EFFICIENCY, sweep_rad, params, cd0=cd0)
        ld = np.asarray(aero.lift_to_drag, dtype=float)
        ax.plot(alpha_deg, ld, color=color, linewidth=2.2, label=rf"M4, assumed $\alpha_b={onset_deg:.0f}\degree$")
        i = int(np.argmax(ld))
        best_pts.append((alpha_deg[i], ld[i], color))

    for a_pt, ld_pt, color in best_pts:
        ax.plot(a_pt, ld_pt, marker="o", color=color, markersize=5, zorder=5)

    ax.text(
        0.98,
        0.55,
        "Markers show best SAMPLED L/D within each curve\n"
        "— not a claimed optimum. Not a validated\n"
        "stall/breakdown prediction.",
        transform=ax.transAxes,
        fontsize=8,
        va="top",
        ha="right",
        bbox=dict(boxstyle="round", facecolor="white", edgecolor="#888888", alpha=0.9),
    )

    ax.set_xlabel(r"angle of attack, $\alpha$ [deg]")
    ax.set_ylabel(r"$L/D = C_L/C_D$")
    ax.set_title(
        "Generic Delta Wing — L/D with Breakdown Sensitivity (Milestone 4)\n"
        rf"$\Lambda_{{LE}}={sweep_deg:.1f}\degree$, $AR={AR:.2f}$, $C_{{D0}}={cd0}$ — conceptual model",
        fontsize=10.3,
    )

    ax.set_xlim(ALPHA_MIN_DEG, ALPHA_MAX_DEG)
    ax.set_ylim(bottom=0.0)
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax.legend(loc="upper right", fontsize=8.6, framealpha=0.92)

    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "lift_to_drag_with_breakdown.png"
    make_figure(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
