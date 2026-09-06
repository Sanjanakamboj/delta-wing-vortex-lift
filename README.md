# Delta Wing Vortex Lift — Reduced-Order Aerodynamic Study

A from-scratch, reduced-order aerodynamic model of a **generic, illustrative
65° delta wing**, built up in verified stages: classical attached-flow
lift, Polhamus-style nonlinear vortex lift, drag-due-to-lift and L/D, a
conceptual vortex-breakdown sensitivity treatment, and a pitching-moment /
center-of-pressure force-location model. Every equation has an independent
verification route; every uncertain parameter is explicit and studied via
sensitivity rather than presented as fact.

**This is a conceptual, reduced-order engineering study — not a validated
aerodynamic prediction.** It uses no experimental or CFD data, does not
model a real aircraft, and does not perform a complete-aircraft stability
analysis. See [Limitations](#limitations) before using any number here for
anything beyond illustration.

## Engineering objective

> How much does the nonlinear, Polhamus-style leading-edge vortex change
> the lift, drag, efficiency, and pitching behavior of a highly swept,
> low-aspect-ratio delta wing relative to classical attached-flow theory —
> and how much of that picture is robust versus assumption-dependent once
> vortex breakdown and force-location uncertainty are taken into account?

## Final representative geometry

A single symmetric, sharp-edged, straight-sided triangular delta wing, used
throughout and never changed:

| $b$ | $c_r$ | $S$ | $AR$ | $\Lambda_{LE}$ | MAC |
|---:|---:|---:|---:|---:|---:|
| 6.00 m | 6.4335 m | 19.3006 m² | 1.8652 | 65° | 4.2890 m ($=\tfrac23c_r$) |

Chosen as (span, sweep) = (6.0 m, 65°): 65° sits mid-range in the 55–70°
conceptual band for a slender supersonic-type delta; 6.0 m is a round,
purely illustrative scale (irrelevant to any $C_L$/$C_D$/$C_m$ result,
which depend only on dimensionless ratios).

## Main findings

1. **Vortex lift adds up to ~30% of total lift** by $\alpha=25°$ for this wing (Polhamus-style, $C_{L,\text{vortex}}=K_v\cos\alpha\sin^2\alpha$).
2. **Vortex lift does not uniformly improve efficiency** — it raises L/D by ~4% at 5° but *lowers* it by ~15% at 20°, since vortex-induced drag grows faster than the lift benefit.
3. **Limiting vortex effectiveness above an assumed breakdown onset actually raises L/D at high α** relative to the unbounded extrapolation (+9.7% at 25°) — because it strips away disproportionately drag-heavy lift. This fell out of the model; it was not designed in.
4. **The conceptual usable-AoA region (0°–10.6°) is bounded by ordinary induced-drag decay, not by the uncertain breakdown assumption** — a genuine robustness result for the low/mid-angle model.
5. **High-angle pitching-moment conclusions are dominated by the assumed vortex force-location**, not by any other modeled effect: a $\pm0.10c_r$ sensitivity moves $C_m(20°)$ from −0.277 to −0.355.

See [RESULTS.md](RESULTS.md) for the full quantitative summary and
[VERIFICATION.md](VERIFICATION.md) for the independent audit behind every
number.

## Model architecture

### Attached-flow baseline

Classical finite-wing lifting-line correction, used as a transparent
reference — **not** a delta-wing-specific theory:
$$a = \frac{a_0}{1+a_0/(\pi e AR)}, \quad a_0=2\pi,\ e=0.9 \;\Rightarrow\; a=2.867211\ \text{rad}^{-1}, \qquad C_{L,\text{attached}}=a\alpha$$

### Vortex lift

Polhamus's leading-edge-suction analogy (NASA TN D-3767, 1966), eq. (12),
combined with the *unchanged* linear attached term above (a documented
simplification of Polhamus's own combined nonlinear formula — see
[DESIGN.md](DESIGN.md)):
$$C_{L,\text{vortex}} = K_v(\Lambda_{LE})\cos\alpha\sin^2\alpha, \qquad K_v(\Lambda_{LE}) = K_{v,\text{ref}}\frac{\cos65°}{\cos\Lambda_{LE}},\ K_{v,\text{ref}}=3.30$$

### Drag / L-D

Hybrid: classical induced drag for the attached term, Polhamus's (NASA TN
D-4739, 1968) normal-force resolution applied to the vortex term only:
$$C_{Di,\text{attached}}=\frac{C_{L,\text{attached}}^2}{\pi e AR}, \quad C_{D,\text{vortex}}=C_{L,\text{vortex}}\tan\alpha, \quad C_{D,\text{total}}=C_{D0}+C_{Di,\text{attached}}+C_{D,\text{vortex}},\ C_{D0}=0.028$$

### Breakdown sensitivity

**Not a breakdown prediction.** A smooth, assumed effectiveness factor
multiplies the vortex lift term only, motivated qualitatively by
Wentz & Kohlman (1971) and NASA vortex-core literature:
$$f_b(\alpha) = f_{post}+(1-f_{post})\tfrac12\bigl(1-\tanh(\tfrac{\alpha-\alpha_b}{\Delta\alpha/2})\bigr), \quad \alpha_b=20°,\ \Delta\alpha=4°,\ f_{post}=0.45$$
$$C_{L,\text{vortex,eff}} = C_{L,\text{vortex}}\cdot f_b(\alpha)$$

### Pitching moment / center of pressure

**Isolated-wing conceptual model only** — no tail, trim, CG, or control
surfaces. Force-location convention derived, not guessed (force aft of
reference ⇒ nose-down):
$$C_m = -C_L\frac{\hat x_{\text{force}}-\hat x_{ref}}{\hat c_{ref}}, \qquad \hat x_{cp}=\frac{C_{L,\text{attached}}\hat x_{attached}+C_{L,\text{vortex,eff}}\hat x_{vortex}}{C_{L,\text{total}}}$$
Nominal: $\hat x_{attached}=\hat x_{vortex}=2/3$ (Jones 1946 slender-wing
theory; Snyder & Lamar 1972's AR≤2 similar-centroid finding), $\hat
x_{ref}=0.5$, $\hat c_{ref}=$MAC$/c_r=2/3$ (matching NASA TN D-6994's own
convention exactly).

## Conceptual study region

A predeclared rule (fixed *before* computing the result): usable iff
$f_b\ge0.9$ AND post-peak $L/D\ge0.9\times$ the pre-breakdown reference
L/D AND $\alpha\le25°$. **Result: $[0°,10.6°]$**, unchanged across
$\alpha_b\in\{17°,20°,23°\}$ — ordinary drag-driven L/D decay binds first,
not the breakdown assumption. This is a **predeclared-rule construct**,
never a "safe flight envelope," "stall boundary," or "certified AoA limit."

## Verification

Every equation has an independent test-side or hand-calculation
verification route. Milestone 6 performed a **fresh, independent, 82-check
audit** of the entire model (raw formulas, not production-code
self-comparison); maximum residual **5.4e-13** (a numerical-integration
check — every closed-form check was exact). See
[VERIFICATION.md](VERIFICATION.md) for the full table. **208 tests pass**
under `pytest -W error -q`.

## Featured figures

- [`figures/final_delta_wing_summary.png`](figures/final_delta_wing_summary.png) — single-page 4-panel summary (geometry, lift, L/D, load movement).
- [`figures/final_lift_decomposition.png`](figures/final_lift_decomposition.png) — attached / vortex / pre-breakdown / breakdown-limited lift.
- [`figures/final_aerodynamic_trade.png`](figures/final_aerodynamic_trade.png) — $C_L$/$C_D$/$L/D$, attached-only vs. attached+vortex.
- [`figures/final_load_movement.png`](figures/final_load_movement.png) — center-of-pressure and pitching-moment sensitivity.

20 figures total across all milestones live in `figures/` — see
[Repository structure](#repository-structure).

## Limitations

- **Generic, illustrative geometry** — not a reconstruction of any real aircraft.
- **Incompressible, classical lifting-line attached-flow baseline** — not a delta-wing-specific theory, and known to be physically incomplete once the leading-edge vortex forms.
- **Illustrative $K_v$ sweep scaling** — not recomputed from Multhopp lifting-surface theory, not fitted to experimental data.
- **Hybrid drag model** — documented departure from Polhamus's own combined drag-due-to-lift formula.
- **Assumed breakdown parameters** ($\alpha_b$, $\Delta\alpha$, $f_{post}$) — explicit sensitivity inputs, not validated predictions for this wing.
- **Conceptual pitching-moment force locations** — source-motivated but not calibrated to this specific geometry.
- **No CFD or experimental validation anywhere in this project.**
- **No complete-aircraft longitudinal-stability, trim, or control-surface analysis.**
- **No compressibility or Reynolds-number corrections.**

## Reproducing the analysis

```bash
pip install -e ".[dev]"
pytest -W error -q

python scripts/manual_check.py
python scripts/vortex_lift_study.py
python scripts/drag_polar_study.py
python scripts/breakdown_study.py
python scripts/pitching_moment_study.py
```

Regenerate any figure with its `scripts/make_*.py` script; all figure
generation is deterministic (byte-identical output on rerun).

## Repository structure

```
src/delta_vortex_lift/   geometry, attached_flow, vortex_lift, drag, breakdown, pitching_moment
tests/                   independent pytest suite (208 tests)
scripts/                 manual_check.py, *_study.py, make_*.py figure generators
figures/                 20 deterministic PNGs (per-milestone + 4 final summary figures)
README.md                this file — engineering story and reproduction guide
RESULTS.md               concise, interview-ready quantitative summary
VERIFICATION.md          fresh independent audit and residuals (Milestone 6)
DESIGN.md                full derivations, source audit, conventions, and per-milestone rationale
```

## Development history

Built incrementally across six verified milestones, each committed and
pushed separately with its own test suite and figures:

1. **Geometry & attached-flow baseline** — triangular planform, classical lifting-line reference.
2. **Polhamus-style vortex lift** — NASA TN D-3767 (1966), sweep sensitivity.
3. **Drag, polar, and L/D** — NASA TN D-4739 (1968), attached-only vs. vortex-inclusive comparison.
4. **Vortex-breakdown sensitivity** — Wentz & Kohlman (1971), predeclared usable-AoA rule.
5. **Pitching moment / center of pressure** — Jones (1946), Snyder & Lamar (1972).
6. **Final audit, synthesis, and portfolio release** — fresh independent re-verification, final documentation and figures (this milestone; development stops here).

Full derivations, the complete source audit, and per-milestone design
rationale are in [DESIGN.md](DESIGN.md).
