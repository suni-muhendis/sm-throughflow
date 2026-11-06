# V16 investigation: rejected candidates; production remains v15

**The Stage 35–38 efficiency-ordering defect is not fixed.** Two geometry/shock
hypotheses were implemented as research oracles and tested. Neither supports
promotion. There is no `slc_aungier_experimental_v16` simulator in this work:
the `v16` filenames identify the investigation. Production remains byte-identical
to v15, including its sonic-cell integration, Stage 53 recovery and grid solver.
Scores and design-ranking qualification remain disabled.

## What was isolated

### Native conical geometry

`validation/conical_reference_v16.py` reconstructs constant-local-turn paths
on a cone from the printed NASA meanline angles and axial positions, then
constructs thickness paths and surfaces tangent to intrinsic edge circles.
It uses source KIC/KTC/KOC, not PHISS or measured performance. The construction
follows [NASA TN D-7345](https://ntrs.nasa.gov/api/citations/19740009588/downloads/19740009588.pdf),
printed p. 10. Cylinder limits, constant-angle cone paths, isometric development
and the cone example in [TN D-5437](https://ntrs.nasa.gov/api/citations/19690027504/downloads/19690027504.pdf)
are checked independently. Full manufacturing-coordinate reproduction is still
outstanding; the intrinsic edge-circle convention is an approximation.

Eight coupled anchor solves compare local and developed-plane shock-foot
directions, with 24 conditional row evaluations. The developed variant predicts
stage efficiencies of 81.5722%, 82.1024%, 82.0715% and 82.7021% for 35–38.
Both aspect-ratio signs remain wrong. The local variant has the same problem.
This rejects **this isolated shock-foot geometry correction** as sufficient;
it does not prove that every aspect of conical geometry is already correct.

[Frozen geometry probe](../validation/campaigns/20261105T105832187471Z_slc_aungier_experimental_v15/manifest.json).

### Shock position from flow and geometry

`validation/shock_reference_v16.py` transcribes the continuity, Prandtl–Meyer
and approximate tangential-momentum construction in
[Schobeiri (1997), Part I, equations 42–52](https://doi.org/10.1155/S1023621X9700016X).
The circular reference at M1=1.2, pitch/radius=0.5 and 30-degree metal angle
from circumferential gives 9.7388 degrees of expansion, consistent with the
paper's approximately 9.5-degree value. Independent mass and momentum balances
are checked. The research extension uses the supplied MCA meanline and linear
stream-sheet height variation, without fitted stage coefficients.

This extension assumes sharp leading edges, a uniform shock-face state,
approximate pressure-force cancellation and conserved relative total
temperature. It omits detached bow shocks, explicit rotation through the
passage and shock-induced separation. Missing or multiple admissible roots are
retained as failures. It samples shock loss at nodes; it does **not** replace
or qualify v14's conservative sonic-cell integration.

With measured/reconstructed inlet and exit states, contracting-height rotor
loss means become 0.14087, 0.17665, 0.17768 and 0.19241. The two aspect-ratio
directions become correct. This apparent improvement disappears in the coupled
solver. The supplied-state result is therefore not evidence of a successful
throughflow correction. No inlet measurements were substituted into production.

[Conditional probe](../validation/campaigns/20261105T110934330514Z_slc_aungier_experimental_v15/manifest.json)
and [coupled pilot](../validation/campaigns/20261105T111232905801Z_slc_aungier_experimental_v15/manifest.json).

## Same experiment against v15

The final research campaign uses exactly the **108 v15 design/task pairs**, plus
the same **96 conditional rows and six sensitivities**. Only MCA rows receive
the research override; DCA rows retain v15. Results explicitly carry a research
identifier and `release_evidence=false`. Source archives include the override
scripts as well as the unchanged production package. Runtime production version
alone must not be used to pool these probe results with normal v15 evaluations.

| Outcome | v15 | Rejected candidate |
|---|---:|---:|
| Converged jobs | 75/108 | 75/108 |
| Previously converged jobs lost | — | 0 |
| Unresolved capacity limits | 20 | 14 |
| Numerical failures | 7 | 14 |
| Unsupported conditions | 5 | 5 |
| Invalid states | 1 | 0 |
| Conditional rows evaluated | 96/96 | 92/96 |

Six unresolved-capacity outcomes and one invalid-state outcome become numerical
failures. This is not evidence that a physical limit has moved or disappeared.
The successful job IDs remain unchanged, and failures are not removed from
the comparison. Four conditional evaluations lack an admissible closure.

These are the original-annulus anchors at each machine's **measured** peak-flow
reading; no predicted optimum was selected:

| Stage | Measured eta (%) | v15 | Rejected candidate |
|---|---:|---:|---:|
| 35 | 84.5000 | 81.4291 | 76.8008 |
| 36 | 82.1000 | 81.9867 | 78.8217 |
| 37 | 84.0000 | 81.9464 | 78.6801 |
| 38 | 83.1000 | 82.6104 | 80.1613 |

| Eta difference (percentage points) | Measured | v15 | Rejected candidate |
|---|---:|---:|---:|
| 35 to 36 | -2.4000 | +0.5576 | +2.0209 |
| 37 to 38 | -0.9000 | +0.6640 | +1.4812 |
| 35 to 37 | -0.5000 | +0.5174 | +1.8793 |
| 36 to 38 | +1.0000 | +0.6237 | +1.3396 |

The projected representation also retains the same three wrong directions.
On the identical converged experimental cohorts, P90 absolute efficiency error
worsens from 3.8722 to 7.2185 points (original, 23 readings), and from 3.7094 to
6.8790 points (projected, 28 readings). Full pressure and temperature errors are
retained in the analysis. The 108 jobs include repeats, sensitivities and grids;
they are not 108 independent experiments.

`validation/screen_candidate_v16.py` now checks the signed family differences,
missing predictions and lost converged jobs explicitly. Passing this necessary
development screen never grants experimental or training-label qualification.
The candidate fails the screen and is not promoted.

## Stage 53, grids and determinism

The matched candidate preserves all v15 Stage 53 classifications and performance
metrics. In particular, original Stage 53 at 100% speed/reading 2993 retains
PR=1.3301689232790066 and eta=0.8726614205804744, bitwise identical to v15.
This is preservation of an unchanged DCA branch, not new model validation.

Stage 35 at 90% speed, both fourfold duct grids and both 21-surface grids converge
in the matched candidate. Both anchor repeats are bitwise identical, including
station and row diagnostics. Independent regression tests additionally exercise
the **unchanged production v15** on both eightfold grids, repeated Stage 53 and
Stage 35 at 90%, with the existing convergence and conservation tolerances.
Candidate eightfold-grid behavior is not qualified by those production tests.

The first focused run found a research-only inverse-Prandtl–Meyer endpoint
error: at zero angle, Newton iteration returned M=1+3.7e-11 instead of exactly
1. The endpoint was corrected without relaxing the test. Earlier failed logs
and research campaigns are retained; the final numerical campaign was rerun
after the fix and after correcting the prototype's expansion-angle diagnostics.

## What the source evidence changes

[NASA TM-79280](https://ntrs.nasa.gov/api/citations/19800002791/downloads/19800002791.pdf),
printed p. 4 and figures 7–9, links the high-aspect-ratio machines' casing-pressure
gradients to a strong passage shock and poor diffusion downstream, interpreted
as separation/recirculation. The lower-aspect-ratio machines show smoother
downstream diffusion. These are qualitative interpretations of measured casing
pressures, not measured shock-foot coordinates for every span.

That observation is consistent with a missing shock/diffusion/separation
interaction in the present closure. It is a stronger next hypothesis than a
case-specific aspect-ratio multiplier. It is **not** a numerical proof that this
single mechanism explains all four efficiency differences. Inlet incidence,
stream-sheet contraction, scalar blade-edge planes and wall modeling remain
coupled sources of uncertainty.

## Required next implementation, with exit criteria

1. Validate the entire conical section against source manufacturing coordinates,
   including edge conventions, instead of promoting an isolated foot shift.
2. Establish an operating-point-dependent transonic passage model that covers
   relevant attached/detached shock configurations and post-shock diffusion.
   Check gas-dynamic balances and independent cascade measurements before using
   the four NASA machines to judge design response.
3. Couple shock/boundary-layer interaction to both entropy production and
   blockage consistently. Prevent double counting with existing profile,
   supercritical-Mach and endwall terms. Document unsupported solution branches.
4. Retain the conservative sonic-cell treatment and verify its generalization
   with independent quadrature, sonic crossings and grid refinement. Keep
   Stage 53 as a preservation check; do not hide regressions by changing tolerances.
5. Repeat the frozen experiment, inspect signed family responses and absolute
   errors, then assess uncertainty and held-out machines under the existing gates.

This remains a development solver for balance/equation studies. These results
must not label the relative efficiency merit of compressor designs for training.

## Final evidence

The final targeted suite passes **40 tests** in 171.17 seconds.
This is a focused regression run, not a rerun of the entire 290-test v15 suite.
The failed first oracle test and successful reruns are archived separately.

- [Final 108-job candidate campaign](../validation/campaigns/20261105T112426241310Z_slc_aungier_experimental_v15/manifest.json).
- [Full paired analysis, failures and row results](../validation/campaigns/20261105T112934185300Z_slc_aungier_experimental_v15/comparison.json).
- [Final frozen audit and test logs](../validation/campaigns/20261105T113152950217Z_slc_aungier_experimental_v15/verification.json).

![Measured versus v15 and rejected candidate efficiencies](../validation/campaigns/20261105T112934185300Z_slc_aungier_experimental_v15/family_efficiency.png)

The audit checks 811 protected historical files, the frozen protocol, all
pre-existing v15 tests (including historical goldens), source archives and
identical experiment inputs. The final diagnostic/sonic-endpoint correction
leaves all 108 candidate classifications unchanged; 28 scalar performance
values differ, with maximum absolute change 4.30624e-11. They are not
called bitwise-identical reruns. The final campaign's internal repeats are
bitwise identical. Production has no changed files.

Production SHA256: `fbc4d57167f594f98a92dd8765fb63913e4c7da35cfb2ccfc08a0f7a261eb719`.
