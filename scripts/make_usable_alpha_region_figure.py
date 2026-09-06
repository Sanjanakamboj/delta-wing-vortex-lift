#!/usr/bin/env python3
"""Generate figures/usable_alpha_region.png.

A compact engineering summary: normalized vortex effectiveness and
normalized L/D vs alpha, with the predeclared conceptual usable-AoA region
shaded. Deterministic: fixed alpha grid, fixed styling, no randomness.
"""

import math
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from delta_vortex_lift.breakdown import (
    USABLE_MAX_ALPHA_RAD,
    USABLE_MIN_EFFECTIVENESS,
    USABLE_MIN_LD_FRACTION,
    BreakdownParameters,
    post_breakdown_aerodynamics,
    usable_alpha_limit,
    vortex_effectiveness,
)
from delta_vortex_lift.drag import CD0_DEFAULT, drag_components, lift_to_drag_ratio
from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.vortex_lift import total_lift_coefficient_deg

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

E_EFFICIENCY = 0.9
ALPHA_MIN_DEG = 0.01
ALPHA_MAX_DEG = 30.0
M3_REFERENCE_ALPHA_DEG = np.linspace(0.01, 25.0, 500)


def _m3_reference_ld(AR, e, sweep_deg, cd0):
    cl = total_lift_coefficient_deg(M3_REFERENCE_ALPHA_DEG, AR, e, sweep_deg)
    dc = drag_components(np.radians(M3_REFERENCE_ALPHA_DEG), AR, e, math.radians(sweep_deg), cd0=cd0)
    ld = lift_to_drag_ratio(cl, dc.cd_total)
    i = int(np.argmax(ld))
    return float(ld[i])


def make_figure(save_path: Path) -> None:
    wing = representative_geometry()
    AR = wing.aspect_ratio
    sweep_deg = wing.sweep_LE_deg
    sweep_rad = wing.sweep_LE_rad
    cd0 = CD0_DEFAULT
    params = BreakdownParameters()

    ld_ref = _m3_reference_ld(AR, E_EFFICIENCY, sweep_deg, cd0)
    usable_limit_deg = math.degrees(usable_alpha_limit(AR, E_EFFICIENCY, sweep_rad, ld_ref, params=params, cd0=cd0))

    alpha_deg = np.linspace(ALPHA_MIN_DEG, ALPHA_MAX_DEG, 301)
    alpha_rad = np.radians(alpha_deg)

    f_b = np.asarray(vortex_effectiveness(alpha_rad, params), dtype=float)
    aero = post_breakdown_aerodynamics(alpha_rad, AR, E_EFFICIENCY, sweep_rad, params, cd0=cd0)
    ld = np.asarray(aero.lift_to_drag, dtype=float)
    ld_normalized = ld / ld_ref

    fig, ax = plt.subplots(figsize=(9, 6), dpi=150)

    ax.axvspan(0.0, usable_limit_deg, color="#2ca02c", alpha=0.12, zorder=0, label="conceptual usable-AoA region")

    ax.axhline(USABLE_MIN_EFFECTIVENESS, color="#1f77b4", linewidth=0.8, linestyle=":")
    ax.axhline(USABLE_MIN_LD_FRACTION, color="#d62728", linewidth=0.8, linestyle=":")

    ax.plot(alpha_deg, f_b, color="#1f77b4", linewidth=2.2, label=r"vortex effectiveness $f_b(\alpha)$")
    ax.plot(alpha_deg, ld_normalized, color="#d62728", linewidth=2.2, label=r"$L/D(\alpha)\,/\,L/D_{\mathrm{ref}}$ (breakdown-limited)")

    ax.axvline(usable_limit_deg, color="#2ca02c", linewidth=1.6, linestyle="-")
    ax.annotate(
        f"usable-AoA upper edge\n{usable_limit_deg:.1f}°",
        (usable_limit_deg, 0.5),
        textcoords="offset points",
        xytext=(8, 0),
        fontsize=8.5,
        color="#1a6b1a",
    )
    ax.axvline(math.degrees(USABLE_MAX_ALPHA_RAD), color="#888888", linewidth=1.0, linestyle="--")
    ax.text(math.degrees(USABLE_MAX_ALPHA_RAD) + 0.3, 0.05, "original M1-M3\ndomain edge (25°)", fontsize=7.5, color="#666666")

    ax.set_xlabel(r"angle of attack, $\alpha$ [deg]")
    ax.set_ylabel("normalized metric [-]")
    ax.set_title(
        "Generic Delta Wing — Conceptual Usable-AoA Region (Milestone 4)\n"
        rf"$\Lambda_{{LE}}={sweep_deg:.1f}\degree$, assumed $\alpha_b={math.degrees(params.alpha_b_rad):.0f}\degree$ — "
        "predeclared rule, not a safe flight envelope or stall boundary",
        fontsize=10,
    )
    ax.text(
        0.98,
        0.60,
        r"Rule: usable iff BOTH" + "\n"
        rf"  $f_b \geq {USABLE_MIN_EFFECTIVENESS}$  (blue dotted line)" + "\n"
        rf"  $L/D \geq {USABLE_MIN_LD_FRACTION}\,(L/D)_{{\mathrm{{ref}}}}$ past its peak  (red dotted line)" + "\n"
        r"  and $\alpha \leq 25^\circ$" + "\n"
        r"Reference $L/D$ is the pre-breakdown (M3) best-sampled" + "\n"
        r"value over $[0^\circ, 25^\circ]$, NOT this curve's own peak.",
        transform=ax.transAxes,
        fontsize=8,
        va="top",
        ha="right",
        bbox=dict(boxstyle="round", facecolor="white", edgecolor="#888888", alpha=0.92),
    )

    ax.set_xlim(ALPHA_MIN_DEG, ALPHA_MAX_DEG)
    ax.set_ylim(0.0, 1.15)
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax.legend(loc="upper left", fontsize=8.6, framealpha=0.92)

    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "usable_alpha_region.png"
    make_figure(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
