#!/usr/bin/env python3
"""Generate figures/vortex_breakdown_effectiveness.png.

Plots the vortex-effectiveness factor f_b(alpha) for the default case and
the three onset-sensitivity cases. Deterministic: fixed alpha grid, fixed
styling, no randomness.
"""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from delta_vortex_lift.breakdown import F_POST_DEFAULT, BreakdownParameters, vortex_effectiveness

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

ALPHA_MIN_DEG = 0.0
ALPHA_MAX_DEG = 30.0
ONSET_CASES_DEG = [17.0, 20.0, 23.0]


def make_figure(save_path: Path) -> None:
    alpha_deg = np.linspace(ALPHA_MIN_DEG, ALPHA_MAX_DEG, 301)
    alpha_rad = np.radians(alpha_deg)

    fig, ax = plt.subplots(figsize=(8.5, 5.8), dpi=150)

    ax.axhline(1.0, color="#888888", linewidth=0.8, linestyle=":")
    ax.axhline(F_POST_DEFAULT, color="#888888", linewidth=0.8, linestyle=":")
    ax.text(0.3, F_POST_DEFAULT + 0.02, rf"$f_{{post}}={F_POST_DEFAULT}$", fontsize=8, color="#666666")

    colors = ["#2ca02c", "#1a1a1a", "#d62728"]
    for onset_deg, color in zip(ONSET_CASES_DEG, colors):
        params = BreakdownParameters(alpha_b_rad=np.radians(onset_deg))
        f_b = vortex_effectiveness(alpha_rad, params)
        label = rf"assumed $\alpha_b={onset_deg:.0f}\degree$"
        ax.plot(alpha_deg, f_b, color=color, linewidth=2.2, label=label)
        ax.axvline(onset_deg, color=color, linewidth=0.8, linestyle="--", alpha=0.5)

    ax.set_xlabel(r"angle of attack, $\alpha$ [deg]")
    ax.set_ylabel(r"vortex-lift effectiveness, $f_b(\alpha)$")
    ax.set_title(
        "Generic Delta Wing — Vortex-Effectiveness Sensitivity Model (Milestone 4)\n"
        "Conceptual sensitivity model — NOT a predicted breakdown boundary",
        fontsize=10.5,
    )
    ax.text(
        0.02,
        0.03,
        rf"$f_b(\alpha) = f_{{post}} + (1-f_{{post}})\cdot\frac{{1}}{{2}}(1-\tanh((\alpha-\alpha_b)/w))$"
        "\nAll onset angles are assumed sensitivity parameters, not predictions.",
        transform=ax.transAxes,
        fontsize=8.2,
        va="bottom",
        ha="left",
        bbox=dict(boxstyle="round", facecolor="white", edgecolor="#888888", alpha=0.9),
    )

    ax.set_xlim(ALPHA_MIN_DEG, ALPHA_MAX_DEG)
    ax.set_ylim(0.0, 1.05)
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax.legend(loc="upper right", fontsize=9, framealpha=0.92)

    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "vortex_breakdown_effectiveness.png"
    make_figure(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
