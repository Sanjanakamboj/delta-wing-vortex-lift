#!/usr/bin/env python3
"""Generate figures/final_load_movement.png -- Milestone 6 final CP/Cm summary.

Panel 1: x_cp/c_r vs alpha (nominal co-located, and a forward-vortex
sensitivity case, breakdown-limited vs unbounded).
Panel 2: C_m,total vs alpha (same cases).

Deterministic: fixed alpha grid, fixed styling, no randomness.
"""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from delta_vortex_lift.attached_flow import attached_flow_CL
from delta_vortex_lift.breakdown import effective_vortex_lift_coefficient
from delta_vortex_lift.geometry import representative_geometry
from delta_vortex_lift.pitching_moment import (
    PitchingMomentParameters,
    center_of_pressure_hat,
    total_moment_coefficient,
)
from delta_vortex_lift.vortex_lift import vortex_lift_coefficient

FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

E_EFFICIENCY = 0.9
ALPHA_MIN_DEG = 0.5
ALPHA_MAX_DEG = 30.0
X_VORTEX_OFFSET = -0.10


def make_figure(save_path: Path) -> None:
    wing = representative_geometry()
    AR = wing.aspect_ratio
    sweep_rad = wing.sweep_LE_rad

    nominal_params = PitchingMomentParameters()
    sensitivity_params = PitchingMomentParameters(x_vortex_hat=nominal_params.x_attached_hat + X_VORTEX_OFFSET)

    alpha_deg = np.linspace(ALPHA_MIN_DEG, ALPHA_MAX_DEG, 301)
    alpha_rad = np.radians(alpha_deg)

    cl_attached = attached_flow_CL(alpha_rad, AR, E_EFFICIENCY)
    cl_vortex_unbounded = vortex_lift_coefficient(alpha_rad, sweep_rad)
    cl_vortex_limited = effective_vortex_lift_coefficient(alpha_rad, sweep_rad)

    xcp_sens_unbounded = center_of_pressure_hat(cl_attached, cl_vortex_unbounded, sensitivity_params)
    xcp_sens_limited = center_of_pressure_hat(cl_attached, cl_vortex_limited, sensitivity_params)

    cm_nominal = total_moment_coefficient(cl_attached, cl_vortex_limited, nominal_params)
    cm_sens_limited = total_moment_coefficient(cl_attached, cl_vortex_limited, sensitivity_params)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=150)

    ax1.axhline(nominal_params.x_attached_hat, color="#888888", linewidth=1.0, linestyle=":")
    ax1.plot(alpha_deg, np.full_like(alpha_deg, nominal_params.x_attached_hat), color="#2ca02c", linewidth=2.0, label="nominal (co-located): constant 2/3")
    ax1.plot(alpha_deg, np.asarray(xcp_sens_unbounded, dtype=float), color="#7f7f7f", linewidth=1.8, linestyle="--", label="sensitivity case, unbounded (M2)")
    ax1.plot(alpha_deg, np.asarray(xcp_sens_limited, dtype=float), color="#d62728", linewidth=2.2, label="sensitivity case, breakdown-limited (M4)")
    ax1.set_xlabel(r"angle of attack, $\alpha$ [deg]")
    ax1.set_ylabel(r"$x_{cp}/c_r$")
    ax1.set_title(r"(a) Center-of-pressure movement", fontsize=10.5)
    ax1.set_xlim(ALPHA_MIN_DEG, ALPHA_MAX_DEG)
    ax1.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax1.legend(loc="lower left", fontsize=7.8)

    ax2.plot(alpha_deg, np.asarray(cm_nominal, dtype=float), color="#2ca02c", linewidth=2.0, label="nominal (co-located)")
    ax2.plot(alpha_deg, np.asarray(cm_sens_limited, dtype=float), color="#d62728", linewidth=2.2, label="sensitivity case (x_vortex - 0.10)")
    ax2.axhline(0.0, color="black", linewidth=0.8)
    ax2.set_xlabel(r"angle of attack, $\alpha$ [deg]")
    ax2.set_ylabel(r"$C_{m,\mathrm{total}}$")
    ax2.set_title(r"(b) Pitching moment", fontsize=10.5)
    ax2.set_xlim(ALPHA_MIN_DEG, ALPHA_MAX_DEG)
    ax2.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax2.legend(loc="lower left", fontsize=8)

    fig.suptitle(
        "Generic 65° Delta Wing — Load Movement Summary (Milestone 6)\n"
        r"$x_{cp}$ movement depends strongly on the ASSUMED vortex-force location — not a measured aerodynamic-center migration",
        fontsize=10.8,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(save_path)
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "final_load_movement.png"
    make_figure(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
