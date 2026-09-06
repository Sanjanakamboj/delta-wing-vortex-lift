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

## Roadmap

- **Milestone 1 (this milestone):** geometry, conventions, attached-flow
  baseline. ✅
- **Milestone 2 (not started):** vortex-lift contribution (e.g. a
  leading-edge-suction-analogy-type model), independently verified against
  its own analytical limits, combined with the attached-flow baseline into a
  total lift curve, with clear separation of the two physical mechanisms.
