#!/usr/bin/env python3
"""Generate figures/drag_sensitivity.png (optional Figure D).

Two panels:
  (a) L/D vs alpha (Model B) for C_D0 = 0.02, 0.03, 0.04.
  (b) Best sampled L/D vs C_D0, for both models -- shows how strongly the
      illustrative profile-drag assumption alone moves the headline
      efficiency result.

Deterministic: fixed alpha grid, fixed styling, no randomness.
"""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from delta_vortex_lift.attached_flow import attached_flow_CL_deg
from delta_vortex_lift.drag import attached_only_drag_coefficient, drag_components, lift_to_drag_ratio
from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.vortex_lift import total_lift_coefficient_deg

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

E_EFFICIENCY = 0.9
ALPHA_MIN_DEG = 0.01
ALPHA_MAX_DEG = 25.0
CD0_CASES = [0.02, 0.03, 0.04]
CD0_SWEEP = np.linspace(0.015, 0.045, 31)


def make_figure(save_path: Path) -> None:
    wing = representative_geometry()
    AR = wing.aspect_ratio
    sweep_deg = wing.sweep_LE_deg

    alpha_deg = np.linspace(ALPHA_MIN_DEG, ALPHA_MAX_DEG, 251)
    alpha_rad = np.radians(alpha_deg)
    cl_B = total_lift_coefficient_deg(alpha_deg, AR, E_EFFICIENCY, sweep_deg)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.5), dpi=150)

    colors = ["#2ca02c", "#1a1a1a", "#d62728"]
    for cd0_case, color in zip(CD0_CASES, colors):
        dc = drag_components(alpha_rad, AR, E_EFFICIENCY, np.radians(sweep_deg), cd0=cd0_case)
        ld = lift_to_drag_ratio(cl_B, dc.cd_total)
        ax1.plot(alpha_deg, ld, color=color, linewidth=2.0, label=rf"$C_{{D0}}={cd0_case:.2f}$")

    ax1.set_xlabel(r"angle of attack, $\alpha$ [deg]")
    ax1.set_ylabel(r"$L/D$ (Model B: attached + vortex)")
    ax1.set_title(r"(a) $L/D$ vs. $\alpha$ for $C_{D0} \in \{0.02, 0.03, 0.04\}$", fontsize=10)
    ax1.set_xlim(0.0, ALPHA_MAX_DEG)
    ax1.set_ylim(bottom=0.0)
    ax1.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax1.legend(loc="upper right", fontsize=9)

    best_ld_A = np.zeros_like(CD0_SWEEP)
    best_ld_B = np.zeros_like(CD0_SWEEP)
    for i, cd0_case in enumerate(CD0_SWEEP):
        cl_A_fine = attached_flow_CL_deg(alpha_deg, AR, E_EFFICIENCY)
        cd_A_fine = attached_only_drag_coefficient(alpha_rad, AR, E_EFFICIENCY, cd0=cd0_case)
        best_ld_A[i] = np.max(lift_to_drag_ratio(cl_A_fine, cd_A_fine))

        dc_fine = drag_components(alpha_rad, AR, E_EFFICIENCY, np.radians(sweep_deg), cd0=cd0_case)
        best_ld_B[i] = np.max(lift_to_drag_ratio(cl_B, dc_fine.cd_total))

    ax2.plot(CD0_SWEEP, best_ld_A, color="#1f77b4", linewidth=2.0, linestyle="--", label="Model A: attached-only")
    ax2.plot(CD0_SWEEP, best_ld_B, color="#d62728", linewidth=2.0, label="Model B: attached + vortex")
    ax2.set_xlabel(r"$C_{D0}$ [dimensionless]")
    ax2.set_ylabel(r"best sampled $L/D$ within $\alpha\in[0,25]\degree$")
    ax2.set_title(r"(b) Best sampled $L/D$ vs. $C_{D0}$" + "\n(NOT a claimed optimum)", fontsize=10)
    ax2.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax2.legend(loc="upper right", fontsize=9)

    fig.suptitle(
        "Generic Delta Wing — Drag-Assumption Sensitivity (Milestone 3)\n"
        "Reduced-order / conceptual model — stall and vortex breakdown not modeled",
        fontsize=11.5,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(save_path)
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "drag_sensitivity.png"
    make_figure(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
