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

## 9. Milestone 2 — Polhamus-style reduced-order vortex lift

### 9.1 What Polhamus (1966) modeled

E. C. Polhamus, *A Concept of the Vortex Lift of Sharp-Edge Delta Wings
Based on a Leading-Edge-Suction Analogy*, NASA TN D-3767, December 1966
(<https://ntrs.nasa.gov/citations/19670003842>) models the total lift of a
thin, sharp-leading-edge delta wing as the sum of two physically distinct
contributions once the leading edge separates and the resulting spiral
vortex sheet **reattaches** on the upper surface inboard of the leading
edge:

1. A **potential-flow ("attached") term**, modified for the fact that a
   sharp, separated leading edge cannot support any leading-edge suction
   (Kutta-type condition), so the normal force reduces to the potential-flow
   normal force resolved through the angle of attack:
   $$C_{L,p} = C_{N,p}\cos\alpha = K_p\sin\alpha\cos^2\alpha \qquad \text{(Polhamus eq. 5)}$$
   where $K_p$ is a lift-curve-slope-like constant determined from
   lifting-surface theory (Polhamus used a modified Multhopp method) and
   depends only on planform. For small $\alpha$, eq. (5) reduces to
   $C_{L,p}\approx K_p\alpha$, so $K_p$ plays the same role as this
   project's attached-flow slope $a$.

2. A **vortex-lift term**, obtained by an analogy: the force needed to
   sustain the separated, reattaching leading-edge vortex is assumed equal
   in magnitude to the leading-edge suction force that *would* have existed
   for attached potential flow around that same leading edge, but rotated
   to act normal to the wing chord (since the vortex flow, unlike attached
   flow, produces no force in-plane). This is his eq. (12):
   $$C_{L,v} = K_v\cos\alpha\sin^2\alpha \qquad \text{(Polhamus eq. 12)}$$
   with, per his eq. (13),
   $$K_v = \frac{K_p - K_p^2 K_i}{\cos\Lambda_{LE}}$$
   where $K_i = \partial C_{D_i}/\partial C_L^2$ is the induced-drag
   parameter, also obtained from lifting-surface theory. His fig. 9 reports
   $K_v$ ranging only slowly with aspect ratio, from about 3.14 at $AR=0$ to
   about 3.45 at $AR=4$, for the family of wings he studied — and states
   explicitly that this weak AR dependence should not be assumed general
   (e.g. it would differ for arrow/diamond planforms).

The total lift is then $C_L = C_{L,p} + C_{L,v}$ (his eq. 14/15), and he
shows excellent agreement with wind-tunnel data for sharp-edge delta wings
of aspect ratio 0.5–2.0 up to $\alpha \approx 20$–$25°$ (his figs. 5, 11,
12) — directly relevant to this project's $AR\approx1.87$ representative
wing.

### 9.2 Why sharp-edged, highly swept wings generate vortex lift

At a sharp leading edge, potential flow theory would require an
infinite velocity (and hence infinite suction) to turn the flow around the
edge. Physically, the flow instead separates right at the edge. For a
highly swept delta wing, this separated shear layer rolls up into a stable,
conical, spiral vortex above the upper surface rather than simply stalling;
flow reattaches on the wing inboard of the vortex core (Polhamus fig. 1),
inducing a strong low-pressure region and hence extra ("vortex") lift not
present in any attached-flow theory. This is fundamentally different from
classical trailing-edge/thickness-driven stall and is the reason this
project's Milestone 1 attached-flow baseline — a theory that assumes
attached flow throughout — cannot capture delta-wing lift once $\alpha$
departs from zero by more than a few degrees.

### 9.3 What this project adopts from the original theory

- The **functional form** of the vortex-lift term, eq. (12):
  $C_{L,v} = K_v\cos\alpha\sin^2\alpha$, used here verbatim as
  `vortex_lift_coefficient` in
  [`vortex_lift.py`](src/delta_vortex_lift/vortex_lift.py).
- The **sweep dependence** implied by eq. (13), $K_v \propto
  1/\cos\Lambda_{LE}$, used here (see §9.4) as the sourced, defensible part
  of the sweep sensitivity.

### 9.4 What is intentionally simplified or deferred

- **$K_p$ and $K_i$ are not recomputed.** Polhamus determined both from a
  full numerical lifting-surface solution (a modified Multhopp method).
  Reproducing that is out of scope for this reduced-order portfolio
  milestone. Instead, $K_v$ is treated as an explicit, illustrative
  reference constant `KV_REFERENCE = 3.30`, chosen within — but not fitted
  to — the numerical range Polhamus himself reports (~3.14–3.45). This
  value is stated plainly everywhere it is used and is never presented as a
  universal delta-wing constant.
- **Sweep scaling holds the $(K_p - K_p^2 K_i)$ prefactor fixed.** Eq. (13)
  shows $K_v$ depends on both $1/\cos\Lambda_{LE}$ *and* on
  $(K_p - K_p^2 K_i)$, which itself depends weakly on planform per
  Polhamus's own fig. 9. This project holds that prefactor fixed at the
  value implied by `(KV_REFERENCE, SWEEP_REFERENCE_RAD=65°)` and varies only
  the $1/\cos\Lambda_{LE}$ factor:
  $$K_v(\Lambda_{LE}) = K_{v,\text{ref}}\,\frac{\cos(65°)}{\cos\Lambda_{LE}}$$
  implemented as `kv_of_sweep`. This is a documented approximation, not a
  full re-derivation of the prefactor's own planform dependence.
- **The vortex term is added to this project's own linear M1 baseline, not
  to Polhamus's nonlinear potential term.** Polhamus's full theory combines
  two *nonlinear* terms ($K_p\sin\alpha\cos^2\alpha$ +
  $K_v\cos\alpha\sin^2\alpha$). This project instead keeps Milestone 1's
  classical, linear, lifting-line attached-flow baseline
  ($C_{L,\text{attached}} = a\alpha$, unchanged) and adds only the Polhamus
  vortex term on top:
  $$C_{L,\text{total}}(\alpha) = \underbrace{a\alpha}_{\text{M1, unchanged}} + \underbrace{K_v(\Lambda_{LE})\cos\alpha\sin^2\alpha}_{\text{Polhamus-style}}$$
  This preserves the project's milestone structure (M1 untouched) at the
  cost of deviating from Polhamus's exact combined formula. The difference
  is small at low $\alpha$ (both $a\alpha$ and $K_p\sin\alpha\cos^2\alpha$
  reduce to a linear term there) and is explicitly documented rather than
  hidden.
- **No vortex breakdown or stall.** Polhamus's own data (fig. 12) shows good
  agreement up to $\alpha\approx20$–$25°$ with some degradation above that
  for higher-AR wings due to trailing-edge separation — a distinct physical
  effect from leading-edge vortex breakdown, and not modeled either way
  here. This project restricts its study range to $\alpha\in[0°,25°]$ for
  this reason and states explicitly, in the figures, the study script, and
  here, that vortex breakdown and stall are not modeled and the curves
  should not be extrapolated further.

This model is referred to throughout the project as **"Polhamus-style" /
"Polhamus-inspired" reduced-order vortex lift** — explicitly not a full,
validated Polhamus aerodynamic prediction.

### 9.5 Sign convention

Consistent with §3: $\alpha\ge0$ in the study domain, $C_{L,\text{vortex}}
\ge 0$ throughout (since $\cos\alpha>0$ and $\sin^2\alpha\ge0$ for
$\alpha\in(-90°,90°)$), so the vortex term never fights the attached-flow
term in sign over the domains used in this project. $C_{L,\text{vortex}}(0)
=0$ exactly, since $\sin(0)=0$.

### 9.6 Coefficient interpretation

- $K_v$ is *not* a lift-curve slope; it has units of $C_L$ per unit
  $\cos\alpha\sin^2\alpha$, i.e. it sets the overall scale of the nonlinear
  vortex contribution. Because $\cos\alpha\sin^2\alpha \sim \alpha^2$ for
  small $\alpha$, the vortex term is second-order in $\alpha$ near zero and
  is negligible compared with the first-order attached-flow term there —
  consistent with vortex lift being a moderate-to-high-$\alpha$ phenomenon.
- The chosen functional form $\cos\alpha\sin^2\alpha$ has an analytical
  interior maximum at $\alpha^\star = \arctan\sqrt2 \approx 54.7°$, a
  property of the trigonometric form itself (verified in
  `test_vortex_lift_analytical_maximum_location`), well outside this
  project's $0$–$25°$ study range and not physically meaningful here (real
  vortex breakdown would intervene long before that angle) — noted so the
  reader does not mistake it for a modeled physical limit.

### 9.7 Sensitivity rationale

Two sensitivities are studied, both requested to isolate what actually
drives the vortex-lift magnitude in this reduced-order model:

- **Sweep**, $\Lambda_{LE}\in\{55°,65°,75°\}$: this is the sourced part of
  the model (§9.4), so showing how strongly $C_{L,\text{vortex}}$ responds
  to sweep is a direct test of the model's most defensible assumption.
- **Coefficient**, $K_v \in \{0.8,1.0,1.2\}\times K_{v,\text{ref}}$: since
  $K_{v,\text{ref}}$ is stated as illustrative rather than derived, a
  $\pm20\%$ sweep quantifies how much the headline vortex-lift fraction
  results depend on that one uncertain choice.

### 9.8 Independent verification

`tests/test_vortex_lift.py` includes (not an exhaustive restatement, see the
file itself): zero-angle identities for both $C_{L,\text{vortex}}$ and
$C_{L,\text{total}}$; the additive identity
$C_{L,\text{total}}=C_{L,\text{attached}}+C_{L,\text{vortex}}$; an
independent hand-formula cross-check; non-negativity and monotonic,
$\alpha^2$-consistent nonlinear growth over the study range; vortex-fraction
behavior at low vs. moderate $\alpha$; monotonic sweep and $K_v$
sensitivity (including an exact linear-scaling identity in $K_v$); absence
of NaN/Inf over the full sweep $\times$ $\alpha$ study grid; scalar/array
consistency; invalid-input rejection (non-finite $\alpha$, sweep outside
$(0°,90°)$, non-positive $K_v$); a hard-coded regression check that the M1
attached-flow numbers are byte-for-byte unchanged; degree/radian
consistency; and the analytical maximum-location identity from §9.6.
`scripts/vortex_lift_study.py` additionally reconstructs one $C_{L,\text{total}}$
value directly from the documented formulas by hand; the residual in the
current run is exactly `0.0`.

### 9.9 Assumptions and limitations (Milestone 2)

- $K_{v,\text{ref}}=3.30$ is illustrative, not derived or calibrated.
- The sweep law $K_v\propto1/\cos\Lambda_{LE}$ holds the
  $(K_p - K_p^2K_i)$ prefactor fixed; the prefactor's own (weak) planform
  dependence per Polhamus's fig. 9 is not reproduced.
- The vortex term is combined with this project's linear M1 baseline rather
  than with Polhamus's own nonlinear potential term (§9.4) — a deliberate
  milestone-preserving simplification.
- No vortex breakdown, no stall, no maximum-$C_L$ cutoff; the model and all
  figures/tables are restricted to and only claimed valid over
  $\alpha\in[0°,25°]$.
- No drag, pitching moment, stability, or supersonic effects are treated —
  out of scope for this milestone, as for Milestone 1.
- No experimental or CFD validation is performed in this project; agreement
  cited from Polhamus's own paper (§9.1) describes *his* validation of the
  full original theory, not a validation of this project's simplified
  reduced-order variant.

## 10. Milestone 3 — reduced-order Polhamus-inspired drag and L/D

### 10.1 Source audit

- E. C. Polhamus, *Application of the Leading-Edge-Suction Analogy of
  Vortex Lift to the Drag Due to Lift of Sharp-Edge Delta Wings*, NASA TN
  D-4739, August 1968
  (<https://ntrs.nasa.gov/citations/19680022518>, primary PDF read directly
  for this milestone). This follow-up to TN D-3767 addresses exactly the
  drag-due-to-lift problem needed here, for the same family of sharp-edge
  delta wings ($AR = 0.25$–$2.0$), and compares three theoretical
  assumptions against wind-tunnel data.
- Classical Prandtl lifting-line induced drag, as presented in standard
  texts (e.g. Anderson, *Fundamentals of Aerodynamics*) and the same
  university course notes cited in §5 for the attached-flow slope: for an
  elliptically-loaded (or $e$-corrected) finite wing,
  $C_{Di} = C_L^2/(\pi e\,AR)$.

### 10.2 What Polhamus (1968) derived

For a thin, sharp leading edge under the Kutta-type (zero-leading-edge-
suction) condition already used in TN D-3767, the resultant aerodynamic
force has no suction component in the wing-chord plane and is therefore
directed perpendicular to the chord. Resolving *that* force into wind axes
(lift = force$\times\cos\alpha$, drag-due-to-lift = force$\times\sin\alpha$)
gives, in coefficient form,
$$\Delta C_D = C_L\tan\alpha \qquad \text{(Polhamus (1968), eq. 4)}$$
which he applies to his own *combined* potential+vortex lift coefficient
(his eq. 3, identical to eq. 15 of TN D-3767) to get
$$\Delta C_D = K_p\sin^2\alpha\cos\alpha + K_v\sin^3\alpha \qquad \text{(eq. 5)}$$
He compares this "zero-leading-edge-suction with vortex lift" assumption
against two others (zero suction with **no** vortex lift, and full
leading-edge suction / classical induced drag) and against experimental
data for $AR = 0.25$–$2.0$. His key findings, directly relevant here:

- The zero-suction-with-vortex-lift assumption (eq. 4/5) matches
  experimental drag due to lift closely across this aspect-ratio range.
- For very slender, highly-swept wings, drag due to lift **can be lower**
  with vortex lift than the classical full-leading-edge-suction (elliptical
  potential-flow) induced-drag prediction — because the vortex lift lets
  the wing reach a given $C_L$ at a lower $\alpha$ than attached flow alone
  would require, more than compensating for the lost leading-edge thrust.

### 10.3 What this project adopts, and the resulting hybrid model

**Adopted:** the geometric argument behind eq. (4) — a force with no
leading-edge suction resolves into drag-due-to-lift equal to its lift
component times $\tan\alpha$ — applied here to the **vortex-lift component
alone**, since `vortex_lift.py`'s $C_{L,\text{vortex}}$ was itself derived
(in TN D-3767) under exactly that same zero-suction assumption:
$$C_{D,\text{vortex}}(\alpha,\Lambda_{LE}) = C_{L,\text{vortex}}(\alpha,\Lambda_{LE})\tan\alpha$$
implemented as `vortex_drag_coefficient` in
[`drag.py`](src/delta_vortex_lift/drag.py).

**Deliberately NOT adopted:** Polhamus's own eq. (4)/(5) applies
$\tan\alpha$ to his *combined* lift coefficient, because in his theory
*both* the potential and vortex terms assume zero leading-edge suction.
This project's Milestone 1 attached-flow baseline
($C_{L,\text{attached}} = a\alpha$) is ordinary lifting-line theory, which
assumes *normal* (non-zero) leading-edge suction — the opposite assumption.
Resolving it via $\tan\alpha$ would therefore misapply the physical
argument behind eq. (4) to a term it was never derived for. Instead, the
attached contribution keeps its own textbook induced-drag relation:
$$C_{Di,\text{attached}}(\alpha) = \frac{C_{L,\text{attached}}(\alpha)^2}{\pi e\,AR}$$
using the same $(e, AR)$ already declared in `attached_flow.py` — no new
efficiency parameter is introduced. The two are then simply summed with an
illustrative profile-drag term:
$$C_{D,\text{total}}(\alpha) = \underbrace{C_{D0}}_{\text{illustrative}} + \underbrace{\frac{C_{L,\text{attached}}^2}{\pi e\,AR}}_{\text{classical, M1-consistent}} + \underbrace{C_{L,\text{vortex}}\tan\alpha}_{\text{Polhamus-style}}$$

This is therefore a **hybrid, reduced-order, Polhamus-inspired drag model**
— explicitly **not** Polhamus's own combined drag-due-to-lift formula — and
is called out as such everywhere it is used. The deviation mirrors, for
drag, exactly the same M1/M2 boundary decision already made and documented
for lift in §9.4.

### 10.4 Force / sign convention

Consistent with §3 and §9.5: for $\alpha \in [0°, 25°)$ (the declared study
range), $\tan\alpha > 0$ and $C_{L,\text{vortex}} \ge 0$, so
$C_{D,\text{vortex}} \ge 0$ throughout; $C_{Di,\text{attached}} \ge 0$
trivially as a squared quantity. Both vanish exactly at $\alpha=0$. Drag
coefficients are defined in the conventional wind-axes sense (drag is
positive opposing the flight direction); no thrust or negative-drag
contribution is modeled.

### 10.5 Profile drag assumption ($C_{D0}$)

$C_{D0} = 0.028$ (module default `CD0_DEFAULT`) is an explicit, illustrative
constant within the stated conceptual 0.02–0.04 range, representing
skin-friction, form, and interference drag that this lift-based reduced-
order model does not otherwise compute. It is **not** calibrated to any
real aircraft, panel code, or wind-tunnel dataset, and is treated purely as
a sensitivity parameter (§10.8) — never presented as a real-aircraft drag
value.

### 10.6 L/D definition

$$L/D = \frac{C_{L,\text{total}}}{C_{D,\text{total}}}$$
implemented as `lift_to_drag_ratio`, which returns exactly `0.0` at
$\alpha=0$ (where $C_L=0$ and $C_D=C_{D0}\ne0$, so $L/D=0$ is the correct
value, not a numerical artifact) and raises `ValueError` for the
mathematically undefined case $C_D=0$ with $C_L\ne0$ (which does not occur
anywhere in this project's declared study range, since $C_{D0}>0$).

### 10.7 Independent verification

`tests/test_drag.py` includes (see the file for the complete set):
$\alpha=0$ identities for every drag term and for L/D; independent
hand-formula checks for both $C_{Di,\text{attached}}$ and
$C_{D,\text{vortex}}$; the additive identity
$C_{D,\text{total}}=C_{D0}+C_{Di,\text{attached}}+C_{D,\text{vortex}}$;
non-negativity and monotonic growth of every drag term with no
discontinuities over $\alpha\in[0°,25°]$; absence of NaN/Inf; scalar/array
consistency; invalid-input rejection (non-finite $\alpha$, $\alpha$ too
close to $90°$, $C_{D0}<0$, invalid $AR$/$e$, $C_D=0$ with $C_L\ne0$); the
L/D identity itself; hard-coded regressions confirming the exact M1
attached-lift and M2 vortex-lift numbers are unchanged; degree/radian
cross-checks against the existing `*_deg` helpers; an exact identity
($C_{D,\text{vortex}} = C_{L,\text{vortex}}\tan\alpha$ pointwise); and
sensitivity-direction checks (higher $C_{D0}$ lowers L/D; higher $K_v$
raises total drag). `scripts/drag_polar_study.py` additionally reconstructs
one $C_{D,\text{total}}$ value directly from the documented formulas by
hand; the residual in the current run is exactly `0.0`.

### 10.8 Sensitivity rationale

- **$C_{D0}$** ($0.02$/$0.03$/$0.04$): this is the single most uncertain,
  purely illustrative input in the whole drag model, so quantifying how
  much it moves the headline best-sampled-L/D result (8.23 → 6.74 → 5.85
  across the three cases) is essential to interpreting the results
  honestly.
- **$K_v \pm20\%$**: reuses the same M2 coefficient-sensitivity rationale
  (§9.7) to show that, unlike $C_{D0}$, the vortex-lift coefficient's
  uncertainty has only a small effect on best-sampled L/D (6.95–7.00) —
  most of the L/D uncertainty in this model comes from $C_{D0}$, not from
  the Polhamus-style vortex terms.

### 10.9 Scope / validity limits

- Restricted to and only claimed valid over $\alpha\in[0°,25°]$, matching
  Milestone 2; no stall, vortex breakdown, or drag-rise model is included,
  and none is implied by any figure or table.
- "Best sampled L/D" values reported anywhere in this project (README,
  study script, figures) are grid-search maxima over the sampled $\alpha$
  range — never claimed aerodynamic optima, and the wording is kept
  explicit throughout for this reason.
- The hybrid drag decomposition (§10.3) is a documented simplification,
  not a reproduction of Polhamus's own combined drag-due-to-lift formula.
- No pitching moment, longitudinal stability, trim, supersonic wave drag,
  or structural consideration is included — out of scope for this
  milestone.
- No experimental or CFD validation is performed in this project; the
  agreement Polhamus reports (§10.2) describes *his* validation of the full
  original theory, not a validation of this project's hybrid, simplified
  variant.

## 11. Milestone 4 — conceptual vortex-breakdown / lift-limit sensitivity

### 11.1 Source audit

- W. H. Wentz and D. L. Kohlman, *Vortex Breakdown on Slender Sharp-Edged
  Wings*, Journal of Aircraft, Vol. 8, No. 3, 1971, based on their
  University of Kansas wind-tunnel study (NASA CR-98737, 1969). A
  systematic schlieren-flow-visualization study of vortex breakdown
  position over sharp-edged delta and modified-delta wings across leading-
  edge sweep 45°–85° at $Re \approx 1\times10^6$. Key findings directly
  relevant here: (i) at low $\alpha$ the leading-edge vortex bursts far
  downstream of the trailing edge; as $\alpha$ increases, the burst point
  moves forward over the wing, eventually reaching the trailing edge and
  then the apex; (ii) increased leading-edge sweep **delays** breakdown
  (a given burst location requires a higher $\alpha$ for more highly swept
  wings); (iii) for sweep angles above about 75°, the breakdown-vs-$\alpha$
  behavior becomes nearly independent of sweep; (iv) breakdown location is
  far more sensitive to changes in planform near the apex than near the
  trailing edge.
- K. D. Visser and R. C. Nelson, *An experimental analysis of critical
  factors involved in the breakdown process of leading-edge vortex flows*
  (NASA/NTRS 19910014797). Crosswire measurements over 70° and 75° delta
  wings identify the vortex's own circulation and accompanying pressure
  field — both of which grow with $\alpha$ — as the dominant factors
  controlling breakdown onset, rather than boundary-layer separation from
  the trailing edge.
- Related NASA vortex-breakdown literature (e.g. NTRS 19920003799,
  *Breaking down the delta wing vortex: The role of vorticity in the
  breakdown process*) reinforces that breakdown is an internal
  hydrodynamic-instability process of the concentrated vortex core (an
  adverse axial pressure gradient causes a rapid, localized expansion —
  a "bubble" or "spiral" disruption — of the core, with a large loss of
  swirl velocity and the associated upper-surface suction).
- E. C. Polhamus, NASA TN D-3767 (1966) and NASA TN D-4739 (1968) remain
  the sources for the *pre-breakdown* vortex-lift and vortex-drag terms
  (unchanged, §9 and §10). Neither report attempts to predict breakdown;
  both explicitly assume the leading-edge vortex reattaches on the upper
  surface.

### 11.2 Vortex breakdown vs. conventional stall

Vortex breakdown is a **distinct physical phenomenon from ordinary 2-D
airfoil (trailing-edge/boundary-layer) stall**: it is an axial-flow
instability internal to the concentrated leading-edge vortex core itself —
governed by the vortex's own circulation and pressure field (Visser &
Nelson) — not a separation of the surface boundary layer from an adverse
pressure gradient along the chord (the classical stall mechanism). Its
onset location and angle depend strongly on planform (especially sweep and
apex shape, per Wentz & Kohlman) and on angle of attack, with some Reynolds-
number sensitivity reported for secondary-vortex/transition behavior even
where primary breakdown location was comparatively Re-insensitive in the
ranges tested.

None of the cited studies characterize this project's own generic,
illustrative wing (never wind-tunnel- or CFD-tested; see §7), so this
repository has **no validated, geometry/Re/Mach-specific data** from which
to derive an exact breakdown-onset angle. Milestone 4 is therefore
explicitly a **sensitivity / high-angle-validity limiting model**, not a
predictive breakdown model. Every onset angle used is labeled an "assumed
breakdown onset" or a "breakdown-onset sensitivity case," never a
prediction.

### 11.3 Mathematical transition model

The pre-breakdown M1–M3 model is preserved exactly (see §11.7 for the
verified below-transition identities); a smooth, monotonically
non-increasing effectiveness factor multiplies only the vortex-lift term:

$$f_b(\alpha) = f_{post} + (1-f_{post})\cdot\frac{1}{2}\Bigl(1-\tanh\bigl(\tfrac{\alpha-\alpha_b}{w}\bigr)\Bigr), \qquad w = \frac{\Delta\alpha}{2}$$

$$C_{L,\text{vortex,effective}}(\alpha) = C_{L,\text{vortex,pre}}(\alpha)\cdot f_b(\alpha), \qquad C_{L,\text{total,effective}}(\alpha) = C_{L,\text{attached}}(\alpha) + C_{L,\text{vortex,effective}}(\alpha)$$

implemented as `vortex_effectiveness` / `effective_vortex_lift_coefficient`
in [`breakdown.py`](src/delta_vortex_lift/breakdown.py). This form is
$C^\infty$ smooth (no discontinuity or kink anywhere), strictly decreasing
in $\alpha$, satisfies $f_b\to1$ as $\alpha\to-\infty$ and $f_b\to f_{post}$
as $\alpha\to+\infty$, and never introduces a hard clip, step, or
oscillation. The width scale $w=\Delta\alpha/2$ is a documented modeling
choice: over $\alpha_b\pm\Delta\alpha$, $\tanh(\pm1)\approx\pm0.76$, placing
most of the transition inside the declared width without being a rigid
cutoff.

**Default illustrative parameters** (assumed sensitivity inputs, not
predictions): $\alpha_b=20°$ — qualitatively consistent with the
Wentz-Kohlman finding that, for sharply-swept (60°–70°) sharp-edged delta
wings, the vortex burst location begins moving onto the wing in roughly
this $\alpha$ region, but **not** a quantitative reproduction of their data
for this project's specific generic wing; $\Delta\alpha=4°$; $f_{post}=0.45$
(within the declared 0.3–0.6 conceptual range).

### 11.4 Drag treatment

Per §10's own logic (the M3 vortex-drag term is itself a resolution of the
vortex *lift* force via $\tan\alpha$), the same effectiveness factor is
applied to that resolved force rather than inventing a new post-breakdown
drag polar:

$$C_{D,\text{vortex,effective}}(\alpha) = C_{L,\text{vortex,effective}}(\alpha)\tan\alpha, \qquad C_{D,\text{total}}(\alpha) = C_{D0} + C_{Di,\text{attached}}(\alpha) + C_{D,\text{vortex,effective}}(\alpha)$$

$C_{Di,\text{attached}}$ and $C_{D0}$ are unchanged from `drag.py`. This
asks only "what happens to the *existing* reduced-order model if vortex
effectiveness degrades" — it does not claim to model separated-flow drag
accurately.

### 11.5 Domain extension

The declared $\alpha$ domain is extended from 0–25° to **0–30°** only for
this milestone's breakdown-sensitivity figures/script, to make the
transition visible. All M1–M3 comparisons and reference values (e.g. the
usable-region L/D reference, §11.6) remain computed on the original 0–25°
domain; the linear attached-flow model is not asserted to be any more valid
in 25°–30° than it already was not validated to be at 20°–25°.

### 11.6 Predeclared conceptual usable-AoA rule

Declared here, in the source code (`usable_alpha_limit`), and in the study
script *before* the resulting numeric envelope was computed or inspected —
consistent with the instruction to fix the rule before seeing the result.
The region $[0,\alpha_{upper}]$ is "usable" (a **conceptual usable-AoA
region** / **pre-breakdown operating region** — never a "safe flight
envelope," "stall boundary," or "certified AoA limit") iff, for every
$\alpha$ in that interval:

1. **Vortex effectiveness remains high**: $f_b(\alpha) \ge 0.9$ — chosen as
   a round, defensible threshold meaning "at least 90% of the pre-breakdown
   vortex lift is still believed effective," consistent with the general
   engineering convention of treating a 10% loss as the threshold of
   material effect.
2. **Efficiency has not meaningfully degraded past its own peak**: for
   $\alpha$ at or beyond the breakdown-limited L/D curve's own maximum
   (chosen so that L/D's natural rise from exactly zero at $\alpha=0$ is
   never misread as "degradation" — an early implementation bug, described
   in §11.9, made exactly this mistake), $L/D(\alpha) \ge 0.9\times$ the
   pre-breakdown (M3) best-sampled reference L/D over $\alpha\in[0°,25°]$.
   The reference is fixed to the pre-breakdown model specifically so the
   rule does not silently redefine its own goalposts as the breakdown
   parameters change.
3. **Never exceeds the original validated domain**: $\alpha \le 25°$,
   regardless of what the breakdown model alone would suggest.

Both numeric thresholds (0.9 and 0.9) are round, conservative, and
declared before computation — not tuned after inspecting the resulting
envelope.

### 11.7 Independent verification

`tests/test_breakdown.py` includes (see the file for the complete set):
below-transition identities showing M4 reduces to M2 (vortex lift) and M3
(total drag) to within $10^{-4}$ absolute tolerance for $\alpha\le10°$;
$f_b$ bounds $(0,1]$, monotonicity, and smoothness (no jump at the
transition boundaries); $f_b\to1$ at low $\alpha$ and $f_b\to f_{post}$ at
high $\alpha$; effective vortex lift never exceeding the pre-breakdown
value and remaining non-negative; scalar/array consistency; absence of
NaN/Inf over the full extended study domain; invalid-input rejection
(non-finite $\alpha$, invalid $\alpha_b$/$\Delta\alpha$/$f_{post}$, invalid
`ld_reference`); sensitivity-direction checks (later $\alpha_b$ delays the
reduction in vortex lift; larger $f_{post}$ retains more vortex lift); an
exact drag identity ($C_{D,\text{vortex,effective}} =
C_{L,\text{vortex,effective}}\tan\alpha$); the L/D identity and its
$\alpha=0$ value; hard-coded regressions confirming the exact M1, M2, and
M3 numbers are unchanged; a degree/radian cross-check; independent
hand-formula checks for both $f_b$ and the effective vortex lift; and a
sanity check that `usable_alpha_limit` always returns a value within the
declared $[0°,25°]$ domain. `scripts/breakdown_study.py` additionally
reconstructs one full $(C_L,C_D)$ pair directly from the documented
formulas by hand; the residual in the current run is exactly `0.0` for
both.

### 11.8 Sensitivity methodology

- **Onset angle** $\alpha_b\in\{17°,20°,23°\}$ (fixed $\Delta\alpha,
  f_{post}$): the single most consequential assumption, since it is
  qualitatively motivated (§11.1) but not quantitatively validated for this
  wing.
- **Transition width** $\Delta\alpha\in\{3°,4°,5°\}$ (fixed $\alpha_b,
  f_{post}$): quantifies how much the sharpness of the assumed transition
  (as opposed to its location) matters.
- For each case, $C_L$, $C_D$, and L/D are tabulated at representative
  $\alpha$, along with the angle at which effective vortex lift has fallen
  10% and 50% below its pre-breakdown value, and — separately from the
  compound usable-region rule — the angle at which $f_b$ alone first drops
  below 0.9, to isolate the breakdown assumption's own sensitivity from the
  rule's other (already-present-in-M3) constraint.

### 11.9 Numerical sanity audit and a bug found/fixed

Before accepting results: M4 was confirmed to equal M1–M3 below the
transition (§11.7); $f_b$ is smooth, monotonic, and bounded; no negative
drag or positive-$\alpha$ lift occurs; no NaN/Inf; no discontinuities or
oscillations; post-breakdown vortex lift is confirmed lower than the
unbounded extrapolation at high $\alpha$ (§13); later assumed onset and
larger retained fraction were confirmed, numerically, to produce weaker
degradation; no hidden clipping was introduced; nothing is called
"validated."

**Bug found and fixed during development**: the first implementation of
`usable_alpha_limit` applied the L/D-fraction criterion across the *entire*
$[0°,25°]$ range, including $\alpha=0$, where $C_L=0$ makes $L/D=0$ by
construction (not a breakdown-related degradation). Since $0 < 0.9\times
L/D_{ref}$ trivially, this made the function return an upper edge of
exactly $0°$ for every onset case — an obviously wrong result caught by
manual inspection before any test was written against it. The fix (§11.6,
item 2) restricts the L/D criterion to the region at or beyond the
breakdown-limited curve's own peak, so the naturally-rising low-$\alpha$
branch is never misread as degradation.

An interesting, non-obvious but fully model-consistent feature also
appeared during review: the breakdown-limited $C_{L,\text{total}}(\alpha)$
curves show a brief near-plateau through the transition region before
resuming a shallower rise (visible in
`figures/lift_with_breakdown.png`). This is not an error — it is the
expected superposition of a rapidly-falling $f_b$ against a still-growing
$C_{L,\text{vortex,pre}}(\alpha) \propto \cos\alpha\sin^2\alpha$ (which
itself keeps increasing until $\alpha\approx54.7°$, well outside this
project's domain); the two effects briefly nearly cancel before $f_b$'s
asymptote to $f_{post}$ makes the pre-breakdown term's growth dominate
again. Per the milestone's own instruction, total lift was not forced to
be monotonic, and it is not.

### 11.10 Validity boundaries

- Restricted to and only claimed valid, as a sensitivity study, over
  $\alpha\in[0°,30°]$; M1–M3 comparisons remain confined to their original
  $[0°,25°]$ domain.
- $\alpha_b$, $\Delta\alpha$, and $f_{post}$ are explicit, illustrative
  sensitivity parameters, never validated breakdown predictions for this
  project's specific generic wing.
- The conceptual usable-AoA region is a predeclared-rule construct, not a
  physical limit, safety margin, or certification boundary of any kind.
- No pitching moment, trim, longitudinal stability, control surfaces, CFD
  comparison, real-aircraft matching, or structural consideration is
  included — out of scope for this milestone.
- No experimental or CFD validation is performed in this project; the
  qualitative trends cited from Wentz & Kohlman and the NASA vortex-core
  literature (§11.1) describe *their* wind-tunnel findings for *their*
  specific wings, not a validation of this project's generic, illustrative
  geometry or its assumed sensitivity parameters.

## 12. Known limitations (Milestone 1)

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
