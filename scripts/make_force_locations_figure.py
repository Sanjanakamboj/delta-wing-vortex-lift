#!/usr/bin/env python3
"""Generate figures/delta_wing_force_locations.png.

An explanatory (not manufacturing) top-view schematic showing the apex,
root chord, MAC leading-edge reference, x_ref, the attached-flow and
vortex-lift resultant locations, representative lift arrows, and the
positive pitching-moment sign convention.

Deterministic: fixed geometry, fixed styling, no randomness.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.pitching_moment import DEFAULT_MOMENT_PARAMS

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"


def make_figure(save_path: Path) -> None:
    wing = representative_geometry()
    c_r = wing.root_chord
    half_b = wing.semi_span
    params = DEFAULT_MOMENT_PARAMS

    x_ref = params.x_ref_hat * c_r
    x_attached = params.x_attached_hat * c_r
    x_vortex = params.x_vortex_hat * c_r
    mac_le_x = wing.mac_leading_edge_x
    mac = wing.mean_aerodynamic_chord

    fig, ax = plt.subplots(figsize=(9, 6.5), dpi=150)

    # Planform outline.
    apex = (0.0, 0.0)
    right_tip = (c_r, half_b)
    left_tip = (c_r, -half_b)
    ax.fill(
        [apex[0], right_tip[0], left_tip[0], apex[0]],
        [apex[1], right_tip[1], left_tip[1], apex[1]],
        color="#dbe9f7",
        edgecolor="#1f3b57",
        linewidth=1.8,
        zorder=1,
    )
    ax.plot([0, c_r], [0, 0], linestyle="--", color="#888888", linewidth=0.9, zorder=2)

    # MAC strip: the spanwise station where local chord == MAC, at y* such
    # that c(y*) = mac -> y* = semi_span*(1 - mac/c_r).
    y_star = half_b * (1.0 - mac / c_r)
    ax.plot([mac_le_x, mac_le_x + mac], [y_star, y_star], color="#6a3d9a", linewidth=2.2, zorder=4)
    ax.text(mac_le_x + mac / 2.0, y_star + 0.18, "MAC", color="#6a3d9a", fontsize=8.5, ha="center")

    arrow_len = half_b * 0.55

    def draw_force(x_pos, label, color, y_off=0.0):
        ax.annotate(
            "",
            xy=(x_pos, y_off - arrow_len),
            xytext=(x_pos, y_off),
            arrowprops=dict(arrowstyle="-|>", color=color, linewidth=2.4),
            zorder=6,
        )
        ax.plot(x_pos, y_off, marker="o", color=color, markersize=5, zorder=7)
        ax.text(x_pos, y_off - arrow_len - 0.55, label, color=color, fontsize=9, ha="center", va="top")

    # Reference point marker (on centerline).
    ax.plot(x_ref, 0.0, marker="s", color="#1a1a1a", markersize=7, zorder=7)
    ax.text(x_ref, 0.35, r"$x_{ref}$", color="#1a1a1a", fontsize=9.5, ha="center")

    # Force resultant locations. Both act at the same x in the nominal
    # (co-located) model; they are drawn at different y purely so both
    # arrows are visible, NOT to imply different spanwise force locations.
    draw_force(x_attached, r"$L_{\mathrm{attached}}$" + "\n" + r"$x_{\mathrm{attached}}/c_r=%.3f$" % params.x_attached_hat, "#1f77b4", y_off=0.9)
    draw_force(x_vortex, r"$L_{\mathrm{vortex}}$" + "\n" + r"$x_{\mathrm{vortex}}/c_r=%.3f$" % params.x_vortex_hat, "#d62728", y_off=-0.9)
    ax.text(
        x_attached + 0.55,
        0.05,
        "(shown at different y only for visual clarity;\nboth act at the same x in the nominal model)",
        fontsize=7,
        color="#555555",
        ha="left",
        va="bottom",
    )

    # Positive pitching-moment convention (curved arrow at x_ref).
    theta = np.linspace(-40, 220, 100) * np.pi / 180.0
    r_arc = 0.9
    arc_x = x_ref + r_arc * np.cos(theta) * 0.35
    arc_y = 0.0 + r_arc * np.sin(theta)
    ax.plot(arc_x, arc_y, color="#2ca02c", linewidth=1.6, zorder=5)
    ax.annotate(
        "",
        xy=(arc_x[-1], arc_y[-1]),
        xytext=(arc_x[-6], arc_y[-6]),
        arrowprops=dict(arrowstyle="-|>", color="#2ca02c", linewidth=1.6),
        zorder=5,
    )
    ax.text(x_ref - 1.3, 0.0, "+$C_m$\n(nose-up)", color="#2ca02c", fontsize=8.5, ha="center", va="center")

    # Root chord annotation.
    ax.annotate("", xy=(c_r, half_b + 0.6), xytext=(0.0, half_b + 0.6), arrowprops=dict(arrowstyle="<->", color="black", linewidth=1.0))
    ax.text(c_r / 2.0, half_b + 0.85, r"$c_r$" + f" = {c_r:.2f} m", ha="center", fontsize=9.5)

    ax.set_xlim(-1.0, c_r + 1.5)
    ax.set_ylim(-half_b - 2.5, half_b + 1.6)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("streamwise direction, x [m] (apex at x=0, positive aft)")
    ax.set_ylabel("spanwise direction, y [m]")
    ax.set_title(
        "Generic Delta Wing — Force-Location Schematic (Milestone 5)\n"
        "Explanatory diagram only, not a manufacturing drawing — conceptual force-location model",
        fontsize=10,
    )
    ax.grid(True, linestyle=":", linewidth=0.4, alpha=0.5)

    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "delta_wing_force_locations.png"
    make_figure(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
