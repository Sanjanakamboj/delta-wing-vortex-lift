# DESIGN.md — Milestone 1: Geometry, Conventions, Attached-Flow Baseline

## 1. Scope

This document records the derivations, conventions, source audit, and
verification identities behind Milestone 1 of the delta-wing lift analysis.
**Vortex lift is explicitly out of scope for this milestone** and is not
present anywhere in `src/delta_vortex_lift/`.

Two physically distinct things are named throughout this project and must
not be conflated:

- **Classical attached-flow baseline** (this milestone): a linear,
  small-angle, moderate/high-AR finite-wing lift model, used purely as a
  transparent reduced-order reference curve.
- **Delta-wing vortex lift** (Milestone 2, NOT YET IMPLEMENTED): the
  nonlinear lift contribution from separated, reattached leading-edge
  vortices that dominates delta-wing behavior at moderate-to-high $\alpha$.

## 2. Geometry derivation

The wing is modeled as a symmetric, sharp-edged, straight-sided (true
triangular) planform with:

- apex at $(0,0)$,
- trailing-edge corners (wingtips) at $(c_r, \pm b/2)$,

where $x$ is streamwise and $y$ is spanwise.

**Area.** The planform is a triangle with base $b$ (the trailing edge) and
height $c_r$ (the streamwise extent), so

$$S = \tfrac{1}{2} b\, c_r$$

**Aspect ratio.** By definition, $AR = b^2/S$. Substituting $S$:

$$AR = \frac{b^2}{\tfrac12 b c_r} = \frac{2b}{c_r}$$

which is used only as a cross-check identity in tests, not as the primary
computation path (the code computes $AR$ directly from $b^2/S$ so that any
future generalization of $S$ automatically propagates correctly).

**Sweep convention.** Leading-edge sweep $\Lambda_{LE}$ is measured, per
standard aircraft convention, as the angle between the leading edge and the
spanwise ($y$) axis. For the right leading edge — the segment from $(0,0)$
to $(c_r, b/2)$ — the streamwise run is $c_r$ and the spanwise run is $b/2$,
so

$$\tan(\Lambda_{LE}) = \frac{c_r}{b/2}$$

This matches the usual convention where $\Lambda_{LE} \to 0$ for an unswept
wing (leading edge running purely spanwise) and $\Lambda_{LE} \to 90°$ for an
infinitely slender, highly swept planform — consistent with real delta wings
having $\Lambda_{LE}$ in the 50–80° range.

**Minimal independent parameter set.** The implementation
(`DeltaWingGeometry`) takes $(c_r, b)$ as the two independent parameters and
derives $S$, $AR$, $\Lambda_{LE}$ from them, which makes inconsistent
combinations of these quantities structurally impossible. Two inverse
constructors, `from_span_and_sweep` and `from_root_chord_and_sweep`, invert
the sweep relation above to build a wing starting from a sweep angle.

## 3. Aerodynamic sign/angle conventions

- $\alpha$: geometric angle of attack, radians internally, degrees for
  display/plots. $\alpha = 0$ is the (assumed) zero-lift attitude of this
  symmetric, uncambered conceptual wing.
- Positive $\alpha$ produces positive lift (right-hand convention, standard
  body/wind-axis lift definition).
- $C_L = L/(q_\infty S)$, $q_\infty = \tfrac12 \rho_\infty V_\infty^2$.
- All internal aerodynamic computation uses SI units and radians; degrees
  are a display/input convenience layer (`attached_flow_CL_deg`).

No source uses a conflicting sign convention for $\alpha$ or $C_L$ in this
milestone, so no reconciliation was needed here. (The sweep-angle convention
reconciliation, where it matters, is discussed in §5.)

## 4. Attached-flow baseline derivation

The classical finite-wing (lifting-line) result for lift-curve slope is

$$a = \frac{a_0}{1 + a_0/(\pi e\, AR)}$$

where $a_0$ is the 2D (infinite-span) lift-curve slope (thin-airfoil theory:
$a_0 = 2\pi$ /rad), $e$ is a span-efficiency factor ($e=1$ for elliptical
loading, $e<1$ otherwise), and $AR$ is the wing aspect ratio. This is the
standard lifting-line correction found in introductory aerodynamics texts
and course notes (see source audit, §5). The small-angle attached-flow lift
coefficient then follows from $C_L = a\,\alpha$ (linear, through the origin
for this symmetric wing).

**Efficiency factor.** $e = 0.9$ is used throughout as a declared,
illustrative constant within the commonly cited $0.8$–$1.0$ range for
efficient (non-elliptical but well-behaved) planforms. It is **not** fit or
tuned to produce any particular result — it is fixed before any figure is
generated and stated explicitly everywhere it is used
(`scripts/manual_check.py`, `scripts/make_attached_lift_figure.py`).

**Why this is only a baseline, not a delta-wing prediction.** The
$a_0/(1+a_0/(\pi e AR))$ relation was derived under classical lifting-line
assumptions: attached flow, moderate-to-high aspect ratio, and a smooth
spanwise circulation distribution. A highly swept, low-AR, sharp-edged delta
wing violates these assumptions almost immediately as $\alpha$ increases:
the flow separates at the sharp leading edge and re-forms into two stable
leading-edge vortices, which produce substantial additional ("vortex")
lift not captured by any linear, attached-flow theory. This is precisely the
physical mechanism analyzed by Polhamus (1966) — see §5. This milestone
therefore uses the finite-wing relation only as a transparent, textbook
reference curve, and says so on every figure and in the README.

**Sweep correction: deliberately deferred.** Per the project brief, no
sweep-dependent correction (e.g. a $\cos\Lambda$-type factor) is introduced
in Milestone 1, because a defensible, sourced swept-wing correction specific
to this planform was not established with sufficient confidence to include
without risking an arbitrary tuning constant. The unswept classical relation
is kept as the sole, independently testable attached-flow reference; a more
specialized swept/delta attached-flow correction is left for a possible
future milestone, sourced and switchable, rather than being invented here.

**No stall model.** The linear relation $C_L = a\alpha$ is evaluated across
the full plotted range $\alpha \in [-5°, 20°]$ for visual comparison, but is
explicitly marked (in the figure and in text) as extrapolated baseline
beyond a conceptual small-angle guide (~8°). No clipping, no maximum-$C_L$
cutoff, and no stall model of any kind is implemented.

## 5. Source audit

**Finite-wing lift-curve slope / lifting-line baseline:**

- The lifting-line correction $a = a_0/(1+a_0/(\pi e AR))$ (equivalently
  written $C_{L_\alpha} = c_{l_\alpha}/(1+c_{l_\alpha}/(\pi e AR))$) is the
  standard finite-wing lift-curve-slope result from classical lifting-line
  theory, presented in numerous university aerodynamics course notes, e.g.
  Georgia Tech AE (Sankar, *Lifting Line Theory* lecture notes,
  `sankar.gatech.edu`) and Stanford AA200b (*Finite Wing Theory*,
  `aero-comlab.stanford.edu`), both of which give the same
  $c_{l_\alpha}/(1+c_{l_\alpha}/(\pi e AR))$ form with $e$ as the
  span-efficiency (Oswald-type) factor. This is textbook material
  traceable to Prandtl's classical lifting-line theory, consistent with the
  treatment in standard texts such as Anderson, *Fundamentals of
  Aerodynamics*.
- Convention check: these sources define $\alpha$, $c_{l_\alpha}$
  (2D slope) and $AR$ identically to this project (radians for slope units,
  $AR=b^2/S$), so no convention reconciliation was needed.

**Delta-wing / vortex-lift context** (motivating why attached-flow theory
alone is insufficient here, even though vortex lift itself is not modeled
until Milestone 2):

- E. C. Polhamus, *A Concept of the Vortex Lift of Sharp-Edge Delta Wings
  Based on a Leading-Edge-Suction Analogy*, NASA TN D-3767, 1966. NASA
  Technical Reports Server:
  <https://ntrs.nasa.gov/citations/19670003842>. This is the foundational
  NASA report establishing that sharp-edge delta wings develop a large,
  nonlinear "vortex lift" contribution from separated, reattached
  leading-edge vortices — a mechanism entirely absent from classical
  attached-flow lifting-line theory.
- E. C. Polhamus, *Application of the Leading-Edge-Suction Analogy of
  Vortex Lift to the Drag Due to Lift of Sharp-Edge Delta Wings*, NASA
  Technical Report, 1968:
  <https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/19680022518.pdf>.
  Extends the same analogy and reinforces that classical linear theory
  under-predicts delta-wing lift once leading-edge vortices form.
- Convention check: Polhamus's reports use the same sharp-edge delta
  planform idea (streamwise root chord, spanwise leading edge) and the same
  sign convention for $\alpha$ (positive $\alpha$ → positive lift); no
  reconciliation beyond noting that Polhamus's $\Lambda$ notation for sweep
  is consistent with the $\Lambda_{LE}$ convention adopted here.

No equations from these sources are implemented in this milestone — they are
cited purely as the physical/motivational basis for why vortex lift will be
needed in Milestone 2, and for why the attached-flow baseline here is
labeled a "baseline," not a delta-wing theory.

## 6. Units

SI units throughout (m, m², rad, m/s, kg/m³, Pa, N). Degrees appear only at
the input/output/plotting boundary via `attached_flow_CL_deg` and the
`*_deg` properties on `DeltaWingGeometry`.

## 7. Representative geometry rationale

$b = 6.0$ m and $\Lambda_{LE} = 65°$ were chosen as the two independent
parameters because:

- $65°$ sits in the middle of the $55$–$70°$ conceptual range specified for
  a slender, supersonic-type delta wing — swept enough to be clearly
  vortex-lift-relevant in a later milestone, without being a degenerate
  sliver.
- $b = 6.0$ m is a round, purely illustrative absolute scale. It does not
  affect $C_L$ (which depends only on the dimensionless $AR$), and is
  explicitly not tied to any real aircraft.

The resulting derived quantities ($c_r \approx 6.43$ m, $S \approx 19.30$
m², $AR \approx 1.87$) were not independently chosen or tuned — they are a
direct consequence of the two chosen independent parameters.

## 8. Verification identities

Implemented as independent tests (not calling the implementation to generate
its own expected values):

- Geometry: $S = \tfrac12 b c_r$; $AR = b^2/S$;
  $\tan(\Lambda_{LE}) = c_r/(b/2)$ (including the exact $45°$ case
  $c_r = b/2$); inverse construction from $(b, \Lambda_{LE})$ and
  $(c_r, \Lambda_{LE})$ recovers the expected root chord/span and round-trips
  the sweep; invalid geometry (non-positive/NaN/inf dimensions, sweep
  outside $(0°, 90°)$) is rejected.
- Attached-flow: $C_L(0) = 0$; $C_L(-\alpha) = -C_L(\alpha)$; $C_L$ equals an
  independently written $a\alpha$; slope decreases as $AR$ decreases (fixed
  $e$); slope increases with $e$ (fixed $AR$); slope $\to a_0$ as
  $AR \to \infty$; degrees vs. radians consistency (and a check that
  degrees fed in as if they were radians do *not* match); scalar input
  returns a Python `float`, array input returns an `ndarray` matching
  elementwise scalar evaluation; dimensional lift helper satisfies
  $L = q_\infty S C_L$; invalid parameters ($AR \le 0$, $e \le 0$, NaN/Inf)
  are rejected.

`scripts/manual_check.py` additionally reconstructs one $C_L$ value directly
from the hand-written formula (not by calling the module's own
`attached_flow_CL` function for that specific value) and prints the
residual, which is exactly `0.0` in the current run.

## 9. Known limitations

- The attached-flow model is a classical, moderate/high-AR lifting-line
  result; its assumptions are known to be violated by this low-AR,
  highly-swept, sharp-edged delta planform, especially away from
  $\alpha \approx 0$.
- No sweep correction is applied to the attached-flow baseline (deliberately
  deferred — see §4).
- No stall or maximum-$C_L$ model is implemented; the linear relation is
  plotted (clearly marked as extrapolation) across the full $\alpha$ range
  requested.
- No vortex lift, nonlinear lift, leading-edge-suction analogy, Polhamus
  model, CFD comparison, drag, pitching moment, or supersonic correction is
  implemented in this milestone.
- $e = 0.9$ is a stated illustrative constant, not derived from or
  calibrated against any specific planform or experimental dataset.
- No experimental validation data is used, referenced numerically, or
  implied by any figure in this milestone.
