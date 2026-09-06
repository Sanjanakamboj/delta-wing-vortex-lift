#!/usr/bin/env python3
"""Generate figures/attached_flow_lift.png: C_L,attached vs alpha.

Deterministic: fixed alpha grid, fixed styling, no randomness.
"""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from delta_vortex_lift.attached_flow import attached_flow_CL_deg
from delta_vortex_lift.geometry import representative_geometry

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

E_EFFICIENCY = 0.9

# Conceptual small-angle region within which a linear, attached-flow model is
# conventionally considered reasonable for a well-behaved wing. This is a
# reduced-order modeling judgment call, not a measured stall boundary, and is
# drawn only as a soft visual guide.
SMALL_ANGLE_LIMIT_DEG = 8.0


def make_figure(save_path: Path) -> None:
    wing = representative_geometry()
    AR = wing.aspect_ratio

    alpha_deg = np.linspace(-5.0, 20.0, 251)
    cl_attached = attached_flow_CL_deg(alpha_deg, AR, E_EFFICIENCY)

    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=150)

    # Shade the extrapolated region beyond the small-angle guide.
    ax.axvspan(
        SMALL_ANGLE_LIMIT_DEG,
        alpha_deg.max(),
        color="#d9534f",
        alpha=0.08,
        zorder=0,
        label=r"baseline extrapolation ($\alpha$ beyond small-angle region)",
    )
    ax.axvspan(alpha_deg.min(), SMALL_ANGLE_LIMIT_DEG, color="#5cb85c", alpha=0.06, zorder=0)

    ax.axhline(0.0, color="black", linewidth=0.8, zorder=1)
    ax.axvline(0.0, color="black", linewidth=0.8, zorder=1)

    ax.plot(
        alpha_deg,
        cl_attached,
        color="#1f3b57",
        linewidth=2.2,
        label="attached-flow baseline: " + r"$C_{L,\mathrm{attached}} = a\,\alpha$",
        zorder=3,
    )

    ax.axvline(
        SMALL_ANGLE_LIMIT_DEG,
        color="#b03a2e",
        linewidth=1.0,
        linestyle="--",
        zorder=2,
        label=rf"conceptual small-angle guide ($\alpha \approx {SMALL_ANGLE_LIMIT_DEG:.0f}\degree$, not a stall boundary)",
    )

    ax.set_xlabel(r"angle of attack, $\alpha$ [deg]")
    ax.set_ylabel(r"$C_{L,\mathrm{attached}}$")
    ax.set_title(
        "Generic Delta Wing — Attached-Flow Lift Baseline\n"
        "Vortex lift not included; reduced-order reference only",
        fontsize=11.5,
    )
    ax.text(
        0.02,
        0.02,
        rf"AR = {AR:.2f}, $e$ = {E_EFFICIENCY}, $a_0$ = $2\pi$ /rad"
        "\nClassical finite-wing slope used as a transparent baseline for this"
        "\nhighly swept, low-AR wing — not a high-fidelity delta-wing prediction."
        "\nNo experimental data; no stall model applied.",
        transform=ax.transAxes,
        fontsize=8.2,
        va="bottom",
        ha="left",
        bbox=dict(boxstyle="round", facecolor="white", edgecolor="#888888", alpha=0.85),
    )

    ax.set_xlim(alpha_deg.min(), alpha_deg.max())
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax.legend(loc="upper left", fontsize=8.5, framealpha=0.9)

    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "attached_flow_lift.png"
    make_figure(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
