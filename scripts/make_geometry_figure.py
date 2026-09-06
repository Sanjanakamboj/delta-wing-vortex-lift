#!/usr/bin/env python3
"""Generate figures/delta_wing_geometry.png: a top-view planform sketch.

Deterministic: no random elements, fixed figure size/DPI, fixed annotation
layout, so re-running this script reproduces the same PNG (given the same
matplotlib version).
"""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from delta_vortex_lift.geometry import representative_geometry

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"


def make_figure(save_path: Path) -> None:
    wing = representative_geometry()
    c_r = wing.root_chord
    b = wing.span
    half_b = wing.semi_span

    # Planform vertices: apex at (0,0), trailing-edge corners at (c_r, +-b/2).
    apex = (0.0, 0.0)
    right_tip = (c_r, half_b)
    left_tip = (c_r, -half_b)

    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)

    # Planform outline
    x = [apex[0], right_tip[0], left_tip[0], apex[0]]
    y = [apex[1], right_tip[1], left_tip[1], apex[1]]
    ax.fill(x, y, color="#8fb8de", edgecolor="#1f3b57", linewidth=2.0, zorder=2)

    # Centerline
    ax.plot([apex[0], c_r], [0, 0], linestyle="--", color="#444444", linewidth=1.0, zorder=3)

    # Root chord (trailing edge) annotation
    ax.annotate(
        "",
        xy=(c_r, half_b),
        xytext=(c_r, -half_b),
        arrowprops=dict(arrowstyle="<->", color="black", linewidth=1.2),
    )
    ax.text(c_r + 0.15, 0.0, r"$c_r$" + f" = {c_r:.2f} m", va="center", ha="left", fontsize=11)

    # Span annotation (offset below the planform)
    span_y = -half_b - 0.9
    ax.annotate(
        "",
        xy=(0.0, span_y),
        xytext=(c_r, span_y),
        arrowprops=dict(arrowstyle="-", color="black", linewidth=0.8),
    )
    ax.annotate(
        "",
        xy=(-0.05, span_y),
        xytext=(-0.05, -half_b),
        arrowprops=dict(arrowstyle="-", color="gray", linewidth=0.6, linestyle=":"),
    )
    ax.annotate(
        "",
        xy=(c_r + 0.05, span_y),
        xytext=(c_r + 0.05, half_b),
        arrowprops=dict(arrowstyle="-", color="gray", linewidth=0.6, linestyle=":"),
    )
    ax.annotate(
        "",
        xy=(0.0, span_y),
        xytext=(c_r, span_y),
        arrowprops=dict(arrowstyle="<->", color="black", linewidth=1.2),
    )
    ax.text(c_r / 2.0, span_y - 0.35, r"$b$" + f" = {b:.2f} m (full span)", ha="center", fontsize=11)

    # Leading-edge sweep annotation (arc at apex, right-hand leading edge)
    sweep_rad = wing.sweep_LE_rad
    arc_radius = 1.1
    # angle measured from the +y (spanwise) axis, sweeping toward +x
    theta = np.linspace(0.0, sweep_rad, 50)
    arc_x = arc_radius * np.sin(theta)
    arc_y = arc_radius * np.cos(theta)
    ax.plot(arc_x, arc_y, color="#b03a2e", linewidth=1.4, zorder=4)
    label_theta = sweep_rad / 2.0
    ax.text(
        1.35 * arc_radius * np.sin(label_theta),
        1.35 * arc_radius * np.cos(label_theta),
        r"$\Lambda_{LE}$" + f" = {wing.sweep_LE_deg:.1f}°",
        color="#b03a2e",
        fontsize=11,
        ha="left",
        va="center",
    )
    # reference axis along +y from apex, for the sweep angle to be measured against
    ax.plot([0, 0], [0, half_b * 0.4], color="#b03a2e", linewidth=0.8, linestyle=":", zorder=4)

    # Apex marker
    ax.plot(*apex, marker="o", color="black", markersize=4, zorder=5)

    ax.set_xlim(-1.0, c_r + 2.2)
    ax.set_ylim(span_y - 1.0, half_b + 1.0)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("streamwise direction, x [m]")
    ax.set_ylabel("spanwise direction, y [m]")
    ax.set_title(
        "Generic Delta Wing — Planform Geometry (Milestone 1)\n"
        f"AR = {wing.aspect_ratio:.2f},  S = {wing.area:.2f} m²\n"
        "Illustrative geometry only — not a manufacturing drawing or real-aircraft reconstruction",
        fontsize=9.5,
    )
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)

    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "delta_wing_geometry.png"
    make_figure(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
