# Portfolio Project 09: Delta Wing Vortex Lift

## Engineering question

> What is a defensible, reduced-order estimate of the lift curve for a
> generic, highly swept delta wing — separating the classical attached-flow
> contribution from the nonlinear vortex-lift contribution that dominates
> delta-wing aerodynamics at moderate-to-high angle of attack?

## Current scope: Milestone 1 only

This milestone establishes the **geometry model, aerodynamic conventions, and
attached-flow baseline** for a generic delta wing.

**Vortex lift is intentionally NOT implemented in this milestone.** It is
deferred until the attached-flow foundation below is independently verified.
See [DESIGN.md](DESIGN.md) for the full derivation, source audit, and
limitations.

## Representative generic geometry

A single symmetric, sharp-edged, straight-sided (true triangular) delta wing
is used throughout, chosen to be clearly illustrative and **not** a
reconstruction of any real aircraft:

| Quantity | Symbol | Value |
|---|---|---|
| Root chord | $c_r$ | 6.43 m |
| Full span | $b$ | 6.00 m |
| Planform area | $S$ | 19.30 m² |
| Aspect ratio | $AR = b^2/S$ | 1.87 |
| Leading-edge sweep | $\Lambda_{LE}$ | 65.0° |

Chosen independent parameters: span $b = 6.0$ m and sweep
$\Lambda_{LE} = 65°$ (middle of the conceptual 55–70° range for a slender
supersonic-type delta). All other quantities are derived — see
[`geometry.py`](src/delta_vortex_lift/geometry.py).

## Aerodynamic conventions

- $\alpha$: geometric angle of attack [rad internally, deg for I/O and plots].
  $\alpha = 0$ is the zero-lift orientation of this symmetric conceptual wing.
  Positive $\alpha$ produces positive lift.
- $C_L = L / (q_\infty S)$, with $q_\infty = \tfrac{1}{2}\rho_\infty V_\infty^2$.

## Attached-flow baseline equation

$$a = \frac{a_0}{1 + a_0/(\pi e\, AR)}, \qquad C_{L,\text{attached}} = a\,\alpha$$

with $a_0 = 2\pi$ /rad (thin-airfoil default) and $e = 0.9$ (declared,
illustrative span-efficiency factor — **not** calibrated to any real
aircraft).

**This is a classical, moderate-to-high-AR finite-wing relation used here
only as a transparent reduced-order reference.** It is explicitly *not* a
high-fidelity prediction for a highly swept, low-AR delta wing, which
develops separated leading-edge vortices and a large nonlinear lift
contribution this formula cannot capture. See [DESIGN.md](DESIGN.md).

## Headline result

For the representative geometry above ($AR = 1.87$, $e = 0.9$):

- Attached-flow lift-curve slope: $a \approx 2.867$ /rad ($\approx 0.0500$ /deg)
- $C_{L,\text{attached}}(\alpha)$: $0$ at $0°$, $\approx 0.250$ at $5°$,
  $\approx 0.500$ at $10°$, $\approx 0.751$ at $15°$

Reproduce with:

```bash
python scripts/manual_check.py
```

## Figures

- [`figures/delta_wing_geometry.png`](figures/delta_wing_geometry.png) —
  planform sketch: span, root chord, leading-edge sweep, generic/illustrative.
- [`figures/attached_flow_lift.png`](figures/attached_flow_lift.png) —
  $C_{L,\text{attached}}$ vs. $\alpha$, clearly labeled as an attached-flow
  baseline with no vortex-lift or total-lift curve.

Regenerate with:

```bash
python scripts/make_geometry_figure.py
python scripts/make_attached_lift_figure.py
```

## Verification status

- 42 automated tests pass under `pytest -W error -q` (geometry identities,
  attached-flow identities, invalid-input rejection, scalar/array
  consistency, radians/degrees consistency).
- `scripts/manual_check.py` independently reconstructs one $C_L$ value
  directly from the documented formula; residual is exactly 0.
- See [DESIGN.md](DESIGN.md) for the full list of verification identities.

## Limitations (read before use)

- The attached-flow model is a classical finite-wing lifting-line
  correction; it is **not** a delta-wing-specific theory and is known to be
  physically incomplete for this geometry once leading-edge vortices form.
- No sweep correction, stall model, or vortex-lift term is included in this
  milestone.
- The linear baseline is plotted from −5° to +20° for comparison purposes
  only; the region beyond a conceptual small-angle guide (≈8°) is explicitly
  marked as extrapolation, not a validated prediction.
- $e = 0.9$ is a stated, illustrative value, not a calibrated one.
- No experimental or CFD validation data is used or implied anywhere in this
  milestone.

## Milestone 2: Polhamus-style vortex-lift contribution

### Engineering question

> How much additional, nonlinear lift does the leading-edge vortex
> contribute beyond the attached-flow baseline, and how sensitive is that
> contribution to leading-edge sweep and to the chosen model coefficient?

### Model equation

The Milestone 1 attached-flow baseline is kept **unchanged**:
$C_{L,\text{attached}}(\alpha) = a\,\alpha$.

A separate, reduced-order **Polhamus-style** vortex-lift term is added:

$$C_{L,\text{vortex}}(\alpha, \Lambda_{LE}) = K_v(\Lambda_{LE})\,\cos\alpha\,\sin^2\alpha,
\qquad K_v(\Lambda_{LE}) = K_{v,\text{ref}}\,\frac{\cos\Lambda_{LE,\text{ref}}}{\cos\Lambda_{LE}}$$

$$C_{L,\text{total}}(\alpha) = C_{L,\text{attached}}(\alpha) + C_{L,\text{vortex}}(\alpha,\Lambda_{LE})$$

with $K_{v,\text{ref}} = 3.30$ (illustrative, at $\Lambda_{LE,\text{ref}} = 65°$).
See [DESIGN.md](DESIGN.md) for exactly what is and is not adopted from the
original theory — **this is a Polhamus-inspired reduced-order model, not the
full validated Polhamus prediction.**

### Source

E. C. Polhamus, *A Concept of the Vortex Lift of Sharp-Edge Delta Wings
Based on a Leading-Edge-Suction Analogy*, NASA TN D-3767, 1966
(<https://ntrs.nasa.gov/citations/19670003842>). The functional form
$C_{L,v} = K_v\cos\alpha\sin^2\alpha$ is his eq. (12); the sweep scaling
$K_v \propto 1/\cos\Lambda_{LE}$ is derived from his eq. (13).

### Representative results ($\Lambda_{LE}=65°$, $AR=1.87$, $e=0.9$, $K_v=3.30$)

| $\alpha$ [deg] | $C_{L,\text{attached}}$ | $C_{L,\text{vortex}}$ | $C_{L,\text{total}}$ | $f_v$ [%] |
|---:|---:|---:|---:|---:|
| 0 | 0.0000 | 0.0000 | 0.0000 | 0.00 |
| 5 | 0.2502 | 0.0250 | 0.2752 | 9.07 |
| 10 | 0.5004 | 0.0980 | 0.5984 | 16.38 |
| 15 | 0.7506 | 0.2135 | 0.9642 | 22.15 |
| 20 | 1.0008 | 0.3627 | 1.3636 | 26.60 |

Vortex-lift increment vs. attached-only: at $\alpha=10°$, $\Delta C_L =
0.0980$ (+19.6%); at $\alpha=15°$, $\Delta C_L = 0.2135$ (+28.4%); at
$\alpha=20°$, $\Delta C_L = 0.3627$ (+36.2%).

Reproduce with:

```bash
python scripts/vortex_lift_study.py
```

### Figures

- [`figures/vortex_lift_decomposition.png`](figures/vortex_lift_decomposition.png)
  — attached, vortex, and total $C_L$ vs. $\alpha$.
- [`figures/vortex_lift_sensitivity.png`](figures/vortex_lift_sensitivity.png)
  — (a) sweep sensitivity ($\Lambda_{LE}=55°,65°,75°$), (b) vortex-lift
  fraction vs. $\alpha$ with $\pm20\%$ $K_v$ sensitivity.

Regenerate with:

```bash
python scripts/make_vortex_decomposition_figure.py
python scripts/make_vortex_sensitivity_figure.py
```

### Limitations

- $K_{v,\text{ref}} = 3.30$ is an explicit, illustrative constant chosen
  within the numerical range Polhamus himself reports (~3.14–3.45); it is
  **not** recomputed from Multhopp lifting-surface theory and **not**
  fitted to any experimental dataset.
- The sweep scaling holds the planform-dependent prefactor in Polhamus's
  eq. (13) fixed at its reference value — a documented simplification, not
  a full re-derivation.
- The vortex term is added to this project's *linear* M1 attached-flow
  baseline, not to Polhamus's own nonlinear potential term
  ($K_p\sin\alpha\cos^2\alpha$) — see [DESIGN.md](DESIGN.md) for why.
- No vortex breakdown or stall model is included; curves are only claimed
  valid over the plotted $\alpha \in [0°, 25°]$ range and must not be
  extrapolated.
- No experimental or CFD validation is used or implied.

## Roadmap

- **Milestone 1:** geometry, conventions, attached-flow baseline. ✅
- **Milestone 2:** Polhamus-style reduced-order vortex-lift contribution,
  combined with the unchanged attached-flow baseline into a total lift
  curve, with sweep/coefficient sensitivity study. ✅
- **Milestone 3 (not started):** out of scope for now — no drag, L/D,
  pitching moment, stability, vortex breakdown, stall, CFD comparison, or
  aircraft sizing has been implemented.
