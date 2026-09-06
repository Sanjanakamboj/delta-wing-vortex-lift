# Verification

This document records a **fresh, independent, end-to-end audit** of the
entire reduced-order delta-wing model, performed as part of Milestone 6.
Every "expected" value below was computed from raw formulas written
independently of the production code path (i.e. not by calling the
function under test to generate its own expected answer), then compared
against the live `delta_vortex_lift` modules. All numbers here were
recomputed in this session — none are copied from earlier milestone
checkpoints without re-derivation.

Across **82 independent fresh checks** spanning geometry, attached flow,
vortex lift, drag/L-D, breakdown, and pitching moment, the **maximum
residual was 5.4e-13** (a numerical-quadrature check with 2,000,001
integration points; every closed-form check was exact to floating-point
precision, residual `0.000e+00`). **No defects were found.**

## Geometry identities

Representative wing: `span=6.00 m`, `Λ_LE=65°` ⇒ independently rederived:

| Quantity | Formula | Value | Residual vs. module |
|---|---|---:|---:|
| Root chord $c_r$ | $(b/2)\tan\Lambda_{LE}$ | 6.4335207615 m | 0.0 |
| Area $S$ | $0.5\,b\,c_r$ | 19.3005622846 m² | 0.0 |
| Aspect ratio $AR$ | $b^2/S$ | 1.8652306326 | 0.0 |
| Sweep $\Lambda_{LE}$ | $\arctan(c_r/(b/2))$ | 1.1344640138 rad (65°) | 0.0 |
| Inverse construction | span from $(c_r,\Lambda_{LE})$ | 6.0000000000 m | 0.0 |
| MAC (analytic) | $(2/3)c_r$ | 4.2890138410 m | 0.0 |
| MAC (numerical quadrature, 2M points) | $(2/S)\int_0^{b/2}c(y)^2dy$ | 4.2890138410 m | 5.365e-13 |
| MAC leading-edge $x$ (distinct quantity) | $c_r/3$ | 2.1445069205 m | 0.0 |

MAC length (4.289 m) and its leading-edge $x$-location (2.145 m) were
confirmed to remain distinct quantities throughout, as required — neither
is used in place of the other anywhere in the codebase or figures.

## Attached-flow verification

$a = a_0/(1+a_0/(\pi e AR))$, $a_0=2\pi$, $e=0.9$:

- $a = 2.8672109799$ rad⁻¹ = $0.0500422719$ deg⁻¹ — residual 0.0.
- $C_L(0°) = 0$ — residual 0.0.
- Antisymmetry $C_L(-\alpha) + C_L(\alpha) = 0$ at $\alpha=12°$ — residual 0.0.
- $C_{L,\text{attached}}$ at 5°/10°/15°: 0.2502113597 / 0.5004227195 / 0.7506340792 — all residuals 0.0.

## Vortex-lift verification

Source equation (Polhamus, NASA TN D-3767 (1966), eq. 12):
$C_{L,\text{vortex}} = K_v\cos\alpha\sin^2\alpha$, $K_v(\Lambda_{LE})=K_{v,\text{ref}}\cos(65°)/\cos\Lambda_{LE}$, $K_{v,\text{ref}}=3.30$.

| $\alpha$ | $C_{L,\text{attached}}$ | $C_{L,\text{vortex}}$ | $C_{L,\text{total}}$ | $f_v$ [%] | % increment vs. attached |
|---:|---:|---:|---:|---:|---:|
| 5° | 0.25021 | 0.02497 | 0.27518 | 9.07 | 9.98 |
| 10° | 0.50042 | 0.09800 | 0.59842 | 16.38 | 19.58 |
| 15° | 0.75063 | 0.21353 | 0.96416 | 22.15 | 28.45 |
| 20° | 1.00085 | 0.36275 | 1.36359 | 26.60 | 36.24 |
| 25° | 1.25106 | 0.53418 | 1.78524 | 29.92 | 42.70 |

All residuals vs. the live module: 0.0. $C_{L,\text{vortex}}(0°)=0$ exactly.
Sweep sensitivity confirmed monotonic increasing: $K_v(55°)=2.4315 <
K_v(65°)=3.3000 < K_v(75°)=5.3885$. No clipping observed anywhere in the
study domain.

## Drag / L-D verification

$C_{Di,\text{attached}}=C_{L,\text{attached}}^2/(\pi e AR)$,
$C_{D,\text{vortex}}=C_{L,\text{vortex}}\tan\alpha$,
$C_{D,\text{total}}=C_{D0}+C_{Di,\text{attached}}+C_{D,\text{vortex}}$, $C_{D0}=0.028$:

| $\alpha$ | $C_{D,\text{total}}$ | $L/D$ | Additive closure residual |
|---:|---:|---:|---:|
| 5° | 0.0420558008 | 6.5432870983 | 0.0 |
| 10° | 0.0927634387 | 6.4510130940 | 0.0 |
| 15° | 0.1920534898 | 5.0202669704 | 0.0 |
| 20° | 0.3499656924 | 3.8963586447 | 0.0 |
| 25° | 0.5738676346 | 3.1108828990 | 0.0 |

$L/D = C_{L,\text{total}}/C_{D,\text{total}}$ identity: residual 0.0 at every
point. Positivity confirmed over the full $[0°,25°]$ grid.

**Freshly located, best-sampled-within-conceptual-range** (2501-point grid,
$\alpha\in[0.01°,25°]$):

- Attached-only: best sampled $L/D = 6.8620$ at $\alpha=7.68°$.
- Attached+vortex: best sampled $L/D = 6.9697$ at $\alpha=6.97°$.

These are grid maxima, **not** claimed mathematical or physical optima.

## Breakdown verification

$f_b(\alpha) = f_{post} + (1-f_{post})\cdot\tfrac12(1-\tanh(\tfrac{\alpha-\alpha_b}{w}))$,
$w=\Delta\alpha/2$; default $\alpha_b=20°$, $\Delta\alpha=4°$, $f_{post}=0.45$.

- Low-angle regression to M2: $f_b(2°)=0.99999999$, $f_b(5°)=0.99999983$, $f_b(8°)=0.99999662$ — all $\to 1$ as required.
- High-angle approach to $f_{post}$: $f_b(60°)=0.45000000$.
- $f_b$ bounds confirmed $\in(0,1]$; smooth, monotonically non-increasing.

| $\alpha$ | $f_b$ | $C_{L,\text{vortex,eff}}$ | $C_{L,\text{total,eff}}$ | $C_{D,\text{total,eff}}$ | $L/D$ | unbounded→limited $\Delta C_L$ |
|---:|---:|---:|---:|---:|---:|---:|
| 15° | 0.9963189320 | 0.2127397095 | 0.9633737888 | 0.1918428810 | 5.0216811988 | −0.08% |
| 20° | 0.7250000000 | 0.2629911488 | 1.2638365878 | 0.3136577459 | 4.0293492011 | −7.32% |
| 25° | 0.4536810680 | 0.2423465418 | 1.4934033405 | 0.4377842919 | 3.4112766682 | −16.35% |
| 30° | 0.4500249688 | 0.3215297707 | 1.8227979291 | 0.6409930903 | 2.8437091706 | −17.73% |

All residuals vs. the live module: 0.0.

## Pitching-moment verification

$C_{m,\text{attached}}=-C_{L,\text{attached}}(\hat x_{attached}-\hat x_{ref})/\hat c_{ref}$,
$C_{m,\text{vortex}}=-C_{L,\text{vortex,eff}}(\hat x_{vortex}-\hat x_{ref})/\hat c_{ref}$,
nominal $\hat x_{attached}=\hat x_{vortex}=2/3$, $\hat x_{ref}=0.5$, $\hat c_{ref}=2/3$:

| $\alpha$ | $f_v$ [%] | $\hat x_{cp}$ | $C_{m,\text{total}}$ | $C_m$-from-$x_{cp}$ residual |
|---:|---:|---:|---:|---:|
| 10° | 16.38 | 0.6666666667 | −0.1496039277 | 5.6e-17 |
| 15° | 22.08 | 0.6666666667 | −0.2408434472 | 0.0 |
| 20° | 20.81 | 0.6666666667 | −0.3159591469 | 1.7e-16 |
| 25° | 16.23 | 0.6666666667 | −0.3733508351 | 0.0 |

The center-of-pressure reconstruction identity
$C_{m,\text{total}} = -C_{L,\text{total}}(\hat x_{cp}-\hat x_{ref})/\hat c_{ref}$
holds to floating-point precision at every point (max residual 1.7e-16).
$\hat x_{cp} \equiv 2/3$ at every $\alpha$ in the nominal (co-located)
model, exactly as the force-location assumption predicts — this is the
correct behavior of a co-located model, not an error.

This describes the **isolated-wing static pitching tendency about the
chosen reference point** — it is not, and must never be read as, a
complete-aircraft longitudinal-stability result (no fuselage, tail, CG, or
control surfaces are modeled).

## Sensitivity synthesis (one-factor-at-a-time; see README/RESULTS for narrative)

| Factor varied | Range | Headline output | Values across range |
|---|---|---|---|
| $\Lambda_{LE}$ ($K_v$ scaling, M2) | 55°/65°/75° | $C_{L,\text{total}}(20°)$ | 1.2681 / 1.3636 / 1.5932 |
| $C_{D0}$ (M3) | 0.02/0.028/0.03/0.04 | $L/D(15°)$ | 5.2385 / 5.0203 / 4.9685 / 4.7250 |
| $\alpha_b$ (M4) | 17°/20°/23° | $C_{L,\text{total}}(20°)$ | 1.1735 / 1.2638 / 1.3541 |
| $\alpha_b$ (M4) | 17°/20°/23° | $C_{m,\text{total}}(20°)$ | −0.2934 / −0.3160 / −0.3385 |
| $\hat x_{vortex}$ (M5) | $2/3\mp0.10$ | $C_{m,\text{total}}(20°)$ | −0.2765 / −0.3160 / −0.3554 |

No parameters are combined into a fabricated probabilistic uncertainty
band; each row is a deterministic, single-factor sweep.

## Conceptual pre-breakdown aerodynamic study region (recomputed fresh)

Predeclared rule (M4, unchanged): usable iff (a) $f_b\ge0.9$, (b) past its
own L/D peak, breakdown-limited $L/D \ge 0.9\times$ the pre-breakdown
reference $L/D$ (freshly recomputed: 6.9697 at $\alpha=6.97°$), (c)
$\alpha\le25°$.

**Result, recomputed fresh for all three onset cases: $[0°, 10.63°]$ —
identical regardless of $\alpha_b\in\{17°,20°,23°\}$.** At the binding
edge, $f_b=1.0000$ — confirming that **ordinary induced-drag-driven L/D
decay (already present in M3), not the M4 breakdown limiter, is the
binding constraint** for this model at these illustrative parameters. This
is **not** a safe flight envelope, stall boundary, or certified AoA limit —
it is a predeclared-rule construct over a reduced-order conceptual model.

## Regression: M1–M5 headline outputs

All headline numbers reported in the Milestone 1–5 checkpoints were
reproduced exactly in this session (see sections above); no prior
milestone conclusion changed as a result of this audit.

## Test suite

- **208 tests pass** under `pytest -W error -q` (warnings treated as errors).
- 0 failures, 0 warnings.
- Test count by module: `test_geometry.py` (26), `test_attached_flow.py`
  (23), `test_vortex_lift.py` (34), `test_drag.py` (33),
  `test_breakdown.py` (51), `test_pitching_moment.py` (41) — total 208,
  matching the full-suite count above.
