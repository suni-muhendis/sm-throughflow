# v14: sonic-cut shock integration and continuous foot geometry

This investigation targets the Stage 53 convergence regression and the
incorrect Stage 35–38 efficiency ordering seen in v13. The simulator is
`slc_aungier_experimental_v14`. Experimental qualification and design-ranking
qualification remain false; the score remains disabled.

## Identified defects and changes

### A sonic contour crossing a stream surface

The passage-shock formula has a finite right-hand limit at inlet relative
Mach 1 for a nonzero suction-surface expansion. The implementation returns
zero on its subsonic branch. At 18 degrees of expansion the jump exceeds
0.05 in loss coefficient. The sonic limit of the supersonic formula is real:
[NACA RM E57A30](https://ntrs.nasa.gov/api/citations/19930089514/downloads/19930089514.pdf)
gives about 0.02 for ten degrees of turning at Mach 1. Extending that formula
to subsonic inlet flow would require an additional physical model.

The captured unsuccessful Stage 53 full-loss iteration repeatedly moves
rotor surface 9 between Mach 0.999802 and 1.001477. Its point-sampled shock
loss switches between zero and 0.067845. Changing the inner relaxation,
Anderson history or conditioning does not remove this constitutive jump.
A restart from the v12 solution also fails. This is distinct from the
first inner-profile failure, which Aitken acceleration alone can resolve.

v14 integrates the existing pressure-defect correlation over dual cells in
cumulative inlet mass. It interpolates Mach, flow turning and relative
dynamic head along the span, splits every interval at the sonic contour,
and integrates each smooth piece using four-point Gauss quadrature. The
cell boundaries bisect neighboring mass coordinates. Their weights are
the nodal trapezoid weights, and the summed pressure defect equals the
integrated defect to quadrature accuracy. The node's dynamic head converts
the cell mean pressure defect back to the row-model loss basis.

This introduces no empirical Mach blending width, no subsonic extension of
the supersonic correlation and no relaxation of the convergence criteria.
The pointwise loss is retained as `pointwise_shock_loss`; `shock_loss` is the
integrated value. A subsonic bounding surface can carry a nonzero dual-cell
average when part of its cell is supersonic. This is a cell average, not a
prediction of a shock at the subsonic point. Existing loss limiting and
span smoothing occur afterward and are not claimed to preserve this
pressure-defect integral in general.

### The geometric shock foot

v13 chose the nearest sampled surface vertex and then projected its tangent
onto the row cone. This quantizes small design changes, and a closest point
in the cylindrical metric is generally not closest in the conical metric.

v14 carries the constructed suction surface, sampled at common arc-length
coordinates, into the row model. It interpolates the surface at inlet span,
projects the whole surface onto the current row cone, and locates the foot
on a C1 cubic Hermite interpolant. Shared tangents remove the polygon-vertex
plateaus. The cylindrical legacy-angle input remains supported for low-level
callers without a constructed surface. Roundoff-only negative normal-shock
loss is clipped to zero at the sonic, zero-turn limit.

The geometric approximation still assumes a normal from the adjacent
leading edge. It is not an exact developed-cone blade layout or a coupled
shock-position/back-pressure solution. It does not resolve all in-row
streamline migration or three-dimensional shock/endwall interactions.

## What the family investigation establishes

The measured and predicted rotor losses already use the same inlet relative
dynamic-head basis; changing that reference is not a correction. NASA
TP-1338 Appendix B5 was checked directly in the source equation image.

The source reports' PHISS is camber ahead of an **assumed** shock location.
The low-aspect-ratio rows use smaller assumed surface turning than the
present normal-foot model produces, whereas the high-aspect-ratio rows are
closer. Substituting those tabulated values improves the aspect-ratio
ordering, as the frozen v13 counterfactuals show, but supplies no general
shock-position rule for a new blade. It was not adopted in v14.

[NASA TP-1337](https://ntrs.nasa.gov/api/citations/19780025165/downloads/19780025165.pdf)
describes the interdependence of shock loss and boundary-layer development,
and places the MCA transition near but aft of the assumed shock.
[NACA RM E58A14b](https://ntrs.nasa.gov/api/citations/19930089934/downloads/19930089934.pdf)
shows measured shock location moving with operating condition. These
sources support treating the fixed geometric foot as an approximation;
they do not identify a universal aspect-ratio correction coefficient.

The corrected geometry and shock-source integration do **not** resolve the
measured family ordering. In particular, numerical continuity is not evidence that
the model predicts the efficiency benefit of aspect ratio correctly. No
case-specific offsets, PHISS substitutions, fitted aspect-ratio multiplier,
modified experimental targets or changed acceptance thresholds are used.

## Remaining scope

The cell treatment cannot remove the underlying correlation's discontinuity
when an entire uniform span crosses Mach 1 at once. That physical closure
needs separate transonic modeling and validation. Unmeasured wall closures,
source-reconstructed rotor exits, and simplified cone/edge-plane geometry
remain uncertainties. Stage 35–38 peak-flow comparisons are coupled changes
in geometry and operating point, not isolated partial derivatives.

For design-model training, these results remain development evidence with
explicit version, convergence and model-limit labels. They are not reliable
labels for the relative efficiency merit of the Stage 35–38 design changes.
Closing that gap requires an independently specified and checked transonic
loss/geometry closure and tests on machines not used to select it.

## Matched results and verification

The same **108 jobs**, **96 measured-state row closures** and **six inlet/wall
sensitivities** were rerun. Every design and task matches v13 except the
simulator version. The 108 jobs include 54 original and 54 projected research
inputs, including repeats, geometry perturbations and resolution checks; they
are not 108 independent experimental measurements.

| Outcome | v13 | v14 |
|---|---:|---:|
| Converged, all comparison jobs | 74/108 | 75/108 |
| Original inputs | 34/54 | 35/54 |
| Projected research inputs | 40/54 | 40/54 |
| Original experimental operating points | 22/33 | 23/33 |
| Projected experimental operating points | 28/33 | 28/33 |
| Previously successful jobs lost | — | 0 |

The only recovered success is `original__nasa_stage53_100_2993`. All 17
Stage 35–38 experimental points converge in both representations. Stage 35
90% speed, the matched fourfold duct grids and the repeat anchors are retained.
Both repeat anchors are bitwise identical. No supersonic compression clipping
appears in the returned coupled solutions. Unsupported inputs and numerical
or unresolved-capacity failures remain visible.

### Stage 53

The original 100% speed point at 32.71 kg/s, reading 2993, now converges with
unchanged tolerance and iteration limits. The full-loss continuation finishes
in 22 outer iterations; all failed startup attempts remain in the telemetry.
Its stage pressure ratio is **1.330169** (measured 1.329), stage efficiency
**87.266%** (measured 87.9%, error **−0.634 percentage point**). The maximum
mass residual is below 2e-15 and the energy residual below 3e-16 in the
matched run. An independent Aitken inner-iteration counterfactual reaches
the same metrics within 2e-14. Aitken is **not** part of the production change.

### Family ordering

| Stage | Measured efficiency (%) | v13 (%) | v14 (%) |
|---|---:|---:|---:|
| 35 | 84.500 | 81.210 | 81.300 |
| 36 | 82.100 | 81.701 | 81.775 |
| 37 | 84.000 | 81.719 | 81.809 |
| 38 | 83.100 | 82.300 | 82.366 |

| Change | Measured delta (pp) | v13 (pp) | v14 (pp) |
|---|---:|---:|---:|
| 35 → 36 | -2.400 | +0.491 | +0.475 |
| 37 → 38 | -0.900 | +0.581 | +0.557 |
| 35 → 37 | -0.500 | +0.509 | +0.510 |
| 36 → 38 | +1.000 | +0.599 | +0.591 |

Both aspect-ratio comparisons remain reversed. The 35→37 loading comparison
also remains reversed; 36→38 already had the measured sign in v13. The
frozen family-response gate therefore still fails. This is **partial
completion of the requested repair**, not a solution of the family physics.

Conditioning the rotor model on the experimental inlet and exit meridional
states does not remove the reversal either:

| Stage | Measured core loss | v13 | v14 |
|---|---:|---:|---:|
| 35 | 0.10820 | 0.15981 | 0.15927 |
| 36 | 0.13180 | 0.15591 | 0.15543 |
| 37 | 0.11860 | 0.18388 | 0.18313 |
| 38 | 0.14480 | 0.18262 | 0.18204 |

These are equal-weight means of the measured core radial samples, not a
mass-weighted efficiency budget. Rotor-exit data were reconstructed by the
source reports and are not independent direct measurements. Conditioned
predicted deviation is unchanged, so that closure remains a separate source
of error. The surface treatment and cell integral alone do not reproduce the
additional high-aspect-ratio losses.

### Accuracy on identical successful cohorts

The original comparison uses the same 22 successful experimental points in
both versions; the projected comparison uses the same 28. The recovered
Stage 53 point is reported separately rather than added only to v14's cohort.

| Representation | Pressure-rise error P90 (%) | Efficiency error P90 (pp) | Rotor temperature-rise error P90 (%) |
|---|---:|---:|---:|
| original | 23.139 → 23.147 | 4.017 → 3.998 | 14.923 → 15.015 |
| projected | 21.571 → 21.638 | 3.895 → 3.830 | 15.025 → 15.100 |

Efficiency P90 improves slightly; pressure-rise and rotor temperature-rise
P90 worsen slightly. The results do not justify a broad accuracy claim.

### Evidence

- [v13 baseline](../validation/campaigns/20261104T232522087684Z_slc_aungier_experimental_v13/manifest.json).
- [Full matched v14 campaign](../validation/campaigns/20261105T085249763272Z_slc_aungier_experimental_v14/manifest.json).
- [v14 analysis](../validation/campaigns/20261105T090638716941Z_slc_aungier_experimental_v14/manifest.json).
- [Captured v13 sonic oscillation](../validation/campaigns/20261105T083500953790Z_slc_aungier_experimental_v13/manifest.json).
- [Alternative iteration, diagnostic only](../validation/campaigns/20261105T085140237027Z_slc_aungier_experimental_v14/manifest.json).

![Family efficiency comparison](../validation/campaigns/20261105T090638716941Z_slc_aungier_experimental_v14/family_efficiency.png)

New tests use an analytic discontinuous integrand, independent adaptive
quadrature, nonlinear-profile refinement, radial reversal, uniform limits,
sonic-contour perturbations, invalid-input checks, an independently minimized
ellipse and tiny solidity perturbations. The Stage 53 production regression
also checks repeatability and unchanged conservation tolerances.

## Final frozen audit

The full suite passes **271 tests with one import-order skip**. The
entry-point module passes all five tests in isolation, including that skip,
for **272 distinct tests verified**. The seven Mattingly checks were
also rerun after adding the explicit v14 reference alias.

The audit verifies 811 protected historical files, 114 v13 baseline JSON
artifacts, all prior golden assignments and the frozen protocol unchanged.
All 108 design/task pairs match v13 except the simulator version.
The numerical campaign and final production files are byte-identical.

Production SHA256: `56b73b5c45c432029ef34e656ce93dd6d368ea71b41274bd0fe4e988df1fe321`.

[Frozen audit](../validation/campaigns/20261105T091815599857Z_slc_aungier_experimental_v14/manifest.json) includes
test logs, input hashes, source archive and verification results.
The interrupted damped counterfactual and superseded initial test runs
remain explicitly distinguished; they are not completed evidence.
