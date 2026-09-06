# Results

A concise, interview-ready summary of the reduced-order delta-wing
vortex-lift study. All numbers were freshly recomputed and independently
verified in Milestone 6 (see [VERIFICATION.md](VERIFICATION.md)).

## Engineering objective

Build a defensible, reduced-order aerodynamic model of a generic, highly
swept delta wing that separates classical attached-flow lift from
Polhamus-style nonlinear vortex lift, extends it to drag and efficiency,
adds a transparent high-angle validity treatment for the uncertain vortex
breakdown, and examines the resulting pitching tendency and load movement —
all with explicit assumptions, independent verification, and honest
limitations, and **no experimental or CFD validation claimed anywhere**.

## Representative delta wing

Generic, illustrative — not a reconstruction of any real aircraft:

| $b$ | $c_r$ | $S$ | $AR$ | $\Lambda_{LE}$ | MAC |
|---:|---:|---:|---:|---:|---:|
| 6.00 m | 6.4335 m | 19.3006 m² | 1.8652 | 65° | 4.2890 m |

## Lift result

$C_{L,\text{attached}} = a\alpha$, $a = 2.867211$ rad⁻¹ ($e=0.9$, classical
lifting-line finite-wing theory, used only as a transparent baseline for
this low-AR, highly-swept wing).

## Vortex-lift contribution

Polhamus-style, $C_{L,\text{vortex}} = K_v\cos\alpha\sin^2\alpha$,
$K_{v,\text{ref}}=3.30$ at $\Lambda_{LE}=65°$ (NASA TN D-3767, 1966):

| $\alpha$ | $C_{L,\text{attached}}$ | $C_{L,\text{vortex}}$ | $C_{L,\text{total}}$ | vortex fraction |
|---:|---:|---:|---:|---:|
| 10° | 0.5004 | 0.0980 | 0.5984 | 16.4% |
| 15° | 0.7506 | 0.2135 | 0.9642 | 22.1% |
| 20° | 1.0008 | 0.3627 | 1.3636 | 26.6% |
| 25° | 1.2511 | 0.5342 | 1.7852 | 29.9% |

## Drag and L/D result

Hybrid, Polhamus-inspired: $C_{Di,\text{attached}}=C_{L,\text{attached}}^2/(\pi e AR)$
(classical induced drag) + $C_{D,\text{vortex}}=C_{L,\text{vortex}}\tan\alpha$
(Polhamus 1968 normal-force resolution, applied to the vortex term) +
$C_{D0}=0.028$ (illustrative, uncalibrated).

| $\alpha$ | $C_{D,\text{total}}$ | $L/D$ |
|---:|---:|---:|
| 10° | 0.0928 | 6.45 |
| 15° | 0.1921 | 5.02 |
| 20° | 0.3500 | 3.90 |
| 25° | 0.5739 | 3.11 |

**Best sampled L/D** (grid maximum, not a claimed optimum): attached-only
**6.86 at 7.7°**; attached+vortex **6.97 at 7.0°**. Vortex lift's effect on
efficiency is *not* uniformly positive: +4.3% at 5° but **−15.2% at 20°**,
since vortex-induced drag grows faster than the lift benefit at higher α.

## Breakdown sensitivity

A conceptual, non-predictive effectiveness factor $f_b(\alpha)$ (default
$\alpha_b=20°$, $\Delta\alpha=4°$, $f_{post}=0.45$; all explicit, assumed
sensitivity parameters, motivated qualitatively by Wentz & Kohlman 1971 —
not a validated breakdown prediction for this specific wing) multiplies the
vortex term only:

| $\alpha$ | unbounded $C_{L,\text{total}}$ | breakdown-limited | difference |
|---:|---:|---:|---:|
| 20° | 1.3636 | 1.2638 | −7.3% |
| 25° | 1.7852 | 1.4934 | −16.4% |
| 30° | 2.2157 | 1.8228 | −17.7% |

**Non-obvious finding:** breakdown-limiting *raises* L/D at high α relative
to the unbounded extrapolation (e.g. +9.7% at 25°), because it strips away
disproportionately drag-heavy vortex lift.

## Pitching tendency / load movement

Nominal, source-motivated force locations: $\hat x_{attached}=\hat
x_{vortex}=2/3$ (co-located; Jones 1946 slender-wing theory for the
attached term, Snyder & Lamar 1972's AR≤2 similar-centroid finding for the
vortex term), $\hat x_{ref}=0.5$, $\hat c_{ref}=$MAC$/c_r=2/3$ (matching
NASA TN D-6994's own convention). Because the nominal model co-locates the
two force resultants, $\hat x_{cp}\equiv2/3$ for every $\alpha$ by
construction; a $\pm0.10$ force-location sensitivity study shows
$C_{m,\text{total}}(20°)$ ranging from −0.277 to −0.355 — a **larger spread
than any numerical precision concern**, confirming the force-location
assumption dominates this part of the model's uncertainty. This describes
the **isolated-wing static pitching tendency about the chosen reference
point only** — not a complete-aircraft stability result (no fuselage,
tail, CG, or control surfaces).

## Conceptual study region

Predeclared rule: $f_b\ge0.9$ AND post-peak $L/D\ge0.9\times$ reference
AND $\alpha\le25°$. **Result: $[0°, 10.6°]$, identical across all three
onset sensitivity cases** — the binding constraint is ordinary
induced-drag-driven L/D decay (already present in M3), not the assumed
vortex-breakdown onset. This is a **predeclared-rule construct**, never a
safe flight envelope, stall boundary, or certified AoA limit.

## Strongest quantified findings

1. Vortex lift adds up to **~30% of total lift** by α=25° for this AR≈1.87, 65° wing.
2. Vortex lift **degrades** L/D by up to 15% at α=20° despite raising $C_L$ — efficiency and lift are not the same story.
3. Breakdown-limiting the vortex term **improves** L/D at high α relative to the unbounded model (+9.7% at 25°) — a genuinely counterintuitive result that emerges honestly from the model, not by design.
4. The conceptual usable-AoA region (0°–10.6°) is bounded by ordinary drag growth, not by the uncertain breakdown assumption — a robustness result for the low/mid-α model.
5. Pitching-moment conclusions at α≥20° are **assumption-dominated**: the $\pm0.10c_r$ force-location uncertainty moves $C_m$ by more than any other modeled effect.

## Important limitations

- Generic, illustrative geometry — not a real aircraft.
- Incompressible, classical lifting-line attached-flow baseline, not a delta-wing-specific theory.
- $K_v$ sweep scaling is illustrative, not recomputed from Multhopp lifting-surface theory.
- Drag model is a documented hybrid (classical induced drag + Polhamus-style vortex-drag resolution), not Polhamus's own combined formula.
- Breakdown onset/width/retained-fraction are assumed sensitivity parameters, not validated predictions.
- Pitching-moment force locations are source-motivated but conceptual, not calibrated to this specific geometry.
- No CFD or experimental validation anywhere in this project.
- No complete-aircraft stability, trim, control-surface, compressibility, or Reynolds-number modeling.
