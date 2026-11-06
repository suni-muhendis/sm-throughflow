# Stage 35–38 rotor and downstream loss attribution

## Whole-stage budget

Use the frozen v16 experiment, including the original and projected
annuli. All 34 family operating-point records in the 108-job experiment
are retained in the attribution. The pair comparisons use the same four
design-speed anchor readings as the original validation.
[Frozen v16 comparison](phase3_geometry_v16.md)

The experiment uses energy-averaged rotor and stage pressure ratios
and the rotor temperature rise in the stage-efficiency denominator.
Let `E_r = PR_rotor^k`, `E_s = PR_stage^k` and `W = TR_rotor - 1`.
Then `eta_stage = (E_r - 1)/W - (E_r - E_s)/W`. The second term is the
downstream penalty, which includes everything between the rotor-outlet
and stage-outlet survey planes. It is a whole-stage pressure budget.
The measurement reduction uses `k = 2/7` and the solver reduction uses
its task-owned `R/cp`. The archived budget keeps the published efficiency
and the residual from recomputing it with the printed ratios.
[NASA TP-1338, Appendix B](https://ntrs.nasa.gov/citations/19790001889)

| Original-annulus pair | Measured rotor Δη (pp) | v16 rotor Δη (pp) | Measured downstream penalty Δ (pp) | v16 downstream penalty Δ (pp) | Measured stage Δη (pp) | v16 stage Δη (pp) |
|---|---:|---:|---:|---:|---:|---:|
| 35 → 36 | −2.077 | +0.531 | +0.338 | −0.026 | −2.416 | +0.558 |
| 37 → 38 | −2.857 | +0.521 | −1.945 | −0.144 | −0.912 | +0.665 |
| 35 → 37 | +0.559 | +0.812 | +1.020 | +0.295 | −0.461 | +0.517 |
| 36 → 38 | −0.221 | +0.802 | −1.263 | +0.178 | +1.043 | +0.624 |

For the two aspect-ratio pairs, inserting the measured rotor budget and
retaining the v16 downstream penalty recovers the stage ranking.
Inserting the measured downstream penalty and retaining the v16 rotor
budget gives **+0.193 and +2.466 pp**, still the wrong signs. Both conclusions
also hold in the projected annulus. These substitutions only separate the
aggregate errors. A predictive solution has a coupled rotor and stator.

The 35 → 37 loading pair needs a separate downstream correction. Its
rotor response already has the observed direction, while the downstream
penalty grows by 0.295 pp against 1.020 pp. The pair members use different
geometries and nearby operating points. These are observed pair responses,
with no claim of an isolated aspect-ratio or loading derivative.
[NASA TP-1337, family geometry and performance](https://ntrs.nasa.gov/citations/19780025165)

## Conditioned row budget and shock multiplier bound

Supply the blade-row closure with the experimental inlet and reconstructed
exit states at the four anchor readings. Average each coefficient over
inlet stream tubes with both measured endpoints in the 15–85% span band.
The tube weights use reconstructed inlet mass flux. This excludes both
extrapolated wall nodes from the integration. The published and
reconstructed loss coefficients provide separate comparisons.

For the 35 → 37 loading pair, the conditioned stator core loss rises
from 0.04777 to 0.08007 in the reported data and from 0.03845 to
0.04248 in v16. The reconstructed rise is 0.03232. This is consistent
with the underestimated downstream penalty in the whole-stage budget.
At stator 37 the reported coefficient exceeds v16 by at least 0.034
at each of the five core samples.

| Rotor | Reported core loss | Reconstructed core loss | v16 core loss | v16 direct shock term before postprocessing |
|---|---:|---:|---:|---:|
| 35 | 0.10970 | 0.11256 | 0.15804 | 0.09826 |
| 36 | 0.13066 | 0.13254 | 0.15321 | 0.09325 |
| 37 | 0.12022 | 0.13230 | 0.17946 | 0.10276 |
| 38 | 0.14287 | 0.14698 | 0.17441 | 0.09558 |

The modeled direct shock term falls from low to high aspect ratio in
both pairs. The remaining profile term rises by only 0.00185 and 0.00261
before leakage, limiting and smoothing. To test the strongest version
of a common-coefficient adjustment at these states, apply a common
nonnegative scale to the direct shock term and recompute the production
cap and pressure-defect smoothing. Hold the other terms, wake and state
fixed. At each span station the cap produces a piecewise affine response,
and smoothing and averaging are linear. The difference therefore reaches
its maximum at zero or at a clipping breakpoint and stays constant after
both rows reach their last breakpoints.

| Rotor pair | Reported core Δ loss | Reconstructed core Δ loss | v16 Δ loss | Largest Δ over all common scales |
|---|---:|---:|---:|---:|
| 35 → 36 | +0.02095 | +0.01998 | −0.00483 | +0.00009 |
| 37 → 38 | +0.02265 | +0.01468 | −0.00506 | +0.00239 |

Both maxima occur with the direct term removed. The bound applies to a
common multiplier at fixed states and says nothing about the full
coupled solution of a different loss law. The measured totals do not
identify how much loss comes from shock entropy, viscous effects or
their interaction.

At the Rotor 37 station 85% from the tip, the zero-direct-shock
coefficient is 0.08247, against the reported 0.07100 and reconstructed
0.07770. The interior smoothing weights are positive. With the other
terms fixed, any nonnegative replacement of the direct shock term can
only increase this local value. The difference is relative to the
reported central values and includes the experimental reduction error.

## Scope of the next coupled candidate

Use the NASA casing pressure histories for the four configurations as a
separate pressure-distribution check. The authors infer smoother post-shock
diffusion for Rotors 35 and 37 and a stronger mid-chord compression with
weaker downstream pressure recovery for Rotors 36 and 38 as flow is
reduced. These are time-averaged casing measurements and qualitative
shock interpretations. A candidate should reproduce the pressure-response
contrast and independently screen loss and blockage against the local
Rotor 37 measurements before the coupled 108-job comparison.
[NASA TM-79280, figures 7–9](https://ntrs.nasa.gov/citations/19800002791)
[Rotor 37 local evidence](phase3_interaction_v16.md)

Screen the signs of both rotor aspect-ratio comparisons and check the
35 → 37 conditioned stator loss and coupled downstream penalty separately.
Retain the frozen family-response and numerical preservation gates for
the full experiment.

The attribution is a validation experiment using frozen v16 states. The
production source and runtime identities are verified and the attribution
repeats exactly. Forty-one distinct tests pass across the final focused
run and the existing numerical regressions, including both eightfold
Stage 35 grids, the repeated 90% Stage 35 point and repeated Stage 53.
The stage ranking and training-label qualification remain open.
Reproduce the audit with
`python -m validation.audit_stage_loss_attribution`.

[Archived budgets, clipping curves and source verification](../validation/campaigns/20261105T191028433910Z_slc_aungier_experimental_v16/analysis.json)
