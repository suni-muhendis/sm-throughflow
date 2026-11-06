# Post-v16 shock / separation / blockage investigation

## Decision

**The Stage 35–38 efficiency-ordering defect is not fixed. No candidate is
promoted and no v17 simulator is declared.** Production remains exactly
`slc_aungier_experimental_v16`, with its historical source hash
`96c0037b6c7ab70a5124b1bd8ef4a9cbbab452ed355743aea6afae98108ac43e`.
The disabled score and qualification restrictions remain in force.

The work adds inspectable research code, source evidence, checks and frozen
comparisons. A successful algebraic solve, preserved convergence, or smaller
efficiency error does not establish correct design response. These candidates
must not provide training labels for relative compressor efficiency merit.

## What the source investigation establishes

The production shock term is an inlet/geometry approximation. The viscous
loss bucket and wake blockage come from separate diffusion correlations.
There is no resolved blade-surface boundary-layer state, moving shock foot,
or common entropy/displacement-thickness closure. In the v16 Stage 35 anchor,
all nine interior rotor nodes have zero modeled wake blockage even though
the assumed normal-shock pressure jump exceeds the historical turbulent
interaction indicator 1.89. This is evidence of uncoupled model structure,
**not a proof that all those sections physically separate**.

[Suder, NASA TM-107310](https://ntrs.nasa.gov/citations/19970001675),
printed pp. 195–196 and 200, supplies more discriminating evidence. At 70%
span and design speed the reported residual profile-loss coefficient is
0.108 at low flow, 0.038 at high flow and 0.048 at maximum flow; the associated
normal Mach numbers are 1.396, 1.385 and 1.341. The shock/profile decomposition
has a stated possible bias of about 0.01. Profile loss does not follow normal
Mach alone: shock location, surface curvature and downstream pressure
gradient matter. Low-speed diffusion/loss correlations are insufficient for
shock-dominated loading.

Table 7 is preserved verbatim in
[`nasa_rotor37_shock_interaction`](../validation/cases/nasa_rotor37_shock_interaction/notes.md),
with source hash, page provenance, ditto marks and rounding inconsistencies.
It is a separate measurement campaign on the same rotor family, **not a
held-out machine**. Table 7 supplies no quantitative blockage validation by
itself and is not inserted into the frozen 108-job comparison.

The additional Table 6 (printed p. 183) preserves regional blockage averages:
at high flow, core values are 9% at design speed and 4% at 80% and 60% speed;
endwall values are 17%, 14% and 10%. The radial averaging regions differ and
the values are rounded integer percentages. These are future local-model
checks, not interchangeable with the solver's separate nodal wake/endwall
factors or a new whole-stage validation point.

[Source evidence and v16 diagnostics](../validation/campaigns/20261105T140100314641Z_slc_aungier_experimental_v16/analysis.json).

The following sources constrain possible extensions:

- [Banjac et al. (2022), DOI 10.1115/1.4053852](https://doi.org/10.1115/1.4053852)
  resolves several inviscid shock regimes; its MISES comparisons do not
  validate viscous separation. Its AVDR correction must not be extrapolated
  over the present measured range of approximately 1.086–1.469 without tests.
- [Schobeiri (1997), Part I](https://doi.org/10.1155/S1023621X9700016X),
  eqs. 31 and 34–37, supplies a linearized density correction to circulation.
  Reusing Aungier's loss/blockage curves with that correction is a new hybrid,
  not the complete published Schobeiri correlation system.
- [Boyer (2001), dissertation](https://vtechworks.lib.vt.edu/bitstream/handle/10919/27507/dissertation_final.pdf)
  uses externally specified blockage and adjustments to some deviation/loss
  parameters. Its performance comparisons cannot establish a general
  predictive shock/separation/blockage closure here.
- [Seddon, ARC R&M 3565](https://reports.aerade.cranfield.ac.uk/handle/1826.2/2832)
  concerns external boundary layers entering intakes. Its empirical loss
  formula is not a compressor-passage blockage correlation.

## Detached and internal passage-shock candidate

[`passage_shock_candidate.py`](../validation/passage_shock_candidate.py)
extends the earlier unchoked oracle with the normal and oblique internal
shock reference states, exit-area calculations and back-pressure
interpolation. Exact isentropic area inversion replaces the paper's
approximate inverse fit. Both constructed blade contours supply passage
openings. These choices are explicitly unqualified geometric extensions.

The exit area inversion retains the subsonic or supersonic branch of its
upstream state. An area below critical area is rejected rather than clipped.
Reference states are evaluated only when needed: an inadmissible hypothetical
low-pressure CO state no longer invalidates a valid U or U/CN query.

The [final conditioned probe](../validation/campaigns/20261105T135347389077Z_slc_aungier_experimental_v16/results.json)
evaluates all 44 rotor span points: 16 unchoked and 28 back-pressure-dependent
choked states. Eight points are extrapolated walls. On the seven central
sample indices, the unweighted shock coefficients are:

| Rotor | v16 pointwise shock | Candidate |
|---|---:|---:|
| 35 | 0.096770 | 0.307436 |
| 36 | 0.092229 | 0.293258 |
| 37 | 0.101414 | 0.310352 |
| 38 | 0.093263 | 0.301474 |

These are conditioned shock diagnostics, not complete losses or stage
efficiencies. The adverse aspect-ratio response persists. No empirical
blend is introduced to conceal the regime transition or excessive losses.
Subsonic supercritical completion, regime continuity, annular contraction
and viscous interaction remain unresolved.

The separate [coupled feasibility pilot](../validation/campaigns/20261105T134804943498Z_slc_aungier_experimental_v16/manifest.json)
is labeled `passage_shock_backpressure_nodewise_r2`. It keeps the v16 viscous
background and evaluates the replacement shock at nodes; it deliberately
does not claim sonic-cell integration or a complete interaction model.
An unsupported intermediate iterate is not proof of a machine's physical
operating limit. The first r1 attempt was interrupted before any completed
job because contour/inlet work was repeated for every exit iteration; its
archive and interruption record are retained. Revision r2 caches only
inlet/geometry quantities, returns copies of cached states and limits each
pilot to 1000 row evaluations. Exhaustion is a numerical failure, not a
physical-limit result. Exit angle and pressure remain uncached.

Under that explicit pilot budget, only Stage 38 converges (eta 80.01290%).
Stages 35, 36, 37 and 53 do not return a converged prediction. All four
encounter the row-evaluation budget; Stage 35's top-level retained outcome
is an earlier **unresolved** quasi-normal capacity condition, with numerical
budget failures visible in its subsequent attempts. None establishes a
physical choke or stall. This pilot fails the preservation gate, so it is
not expanded into a full experiment or promoted. The 108-job experiment
below is the separate compressible-circulation hybrid, not this shock model.

## Compressible-circulation attribution experiment

[`compressible_diffusion_candidate.py`](../validation/compressible_diffusion_candidate.py)
applies the source density correction to the circulation contribution in
both reference and actual maximum-velocity calculations. Loss and wake
blockage therefore respond to the same modified diffusion measure. The
shock closure and its conservative sonic-cell integration remain v16.
No machine name, measured efficiency, PHISS table or fitted coefficient
enters the model.

The [full repeated experiment](../validation/campaigns/20261105T133202417353Z_slc_aungier_experimental_v16/manifest.json)
uses exactly the 108 v16 jobs, 96 conditioned rows and six row sensitivities.
Every overridden record is marked as research and unqualified. It is a
rejected hypothesis, not an additional simulator version or release.

At the original-annulus anchor readings:

| Stage | Measured eta (%) | v16 (%) | Hybrid (%) |
|---|---:|---:|---:|
| 35 | 84.500000 | 81.428993 | 80.994565 |
| 36 | 82.100000 | 81.986560 | 81.503321 |
| 37 | 84.000000 | 81.946198 | 81.315658 |
| 38 | 83.100000 | 82.610931 | 81.989601 |

The 35→36 and 37→38 differences remain positive, +0.50876 and +0.67394
percentage points, against measured −2.4 and −0.9. The 35→37 direction also
remains wrong. Increasing the general compressibility/diffusion response
does not close the family-ordering gate.

The full hybrid run retains all **75/108** v16 successes, including the
recovered Stage 53 design-speed point, Stage 35 at 90% speed, both fourfold
duct grids and both 21-surface cases. Both anchor repeats are bitwise
identical. All 96 conditioned rows evaluate. Stage 53 at 90% speed remains
a numerical failure in both versions; preservation does not mean its
whole map is solved.

Five unsuccessful jobs change failure category. Aggregate outcomes are
75 converged, 10 numerical failures, 18 unresolved capacity limits and
five unsupported conditions, compared with v16's 75, 7, 20, 5 plus one
invalid state. Failed jobs are retained in the comparison.

On the same paired successful experimental points (23 original, 28
projected), P90 absolute efficiency error worsens from **3.87229 to 4.05216
percentage points** and from **3.70969 to 4.16957**, respectively. Pressure-
rise and temperature-rise errors decrease slightly, but still fail the
experimental gate. No metric alone is used to override the wrong design
response. Full outcomes, pair identifiers, all metric errors and preservation
checks are in the [comparison](../validation/campaigns/20261105T133202417353Z_slc_aungier_experimental_v16/analysis.json).

## Work still required before a physical correction can be promoted

1. Establish an annular passage shock solution with common mass flow,
   rothalpy and pressure compatibility; verify the geometry and every
   supported flow branch. A failed intermediate state must be distinguished
   from a proven physical limit.
2. Supply a blade-surface boundary-layer state before the shock and a
   post-shock pressure distribution. Couple separation, reattachment,
   displacement thickness and entropy. Avoid adding a loss multiplier while
   retaining an unrelated blockage law or counting the same viscous loss twice.
3. Check independent local shock positions/strengths and wake/blockage data,
   then whole-stage results and held-out machines. Record uncertain data
   interpretation and the admissible range rather than fitting these four
   anchor efficiencies.
4. Preserve conservative source integration, deterministic repeated solves,
   Stage 53 and the eightfold grids under unchanged residual/conservation
   tolerances. Promote only a successful candidate under a new simulator
   version and new reference values.

The requested complete shock–separation–blockage correction remains open.

## Final verification

**332 distinct tests are verified on the retained production and final
research code.** The final full run records 331 passed and one
import-order skip in 1446.84 seconds, with zero errors or
failures in its per-test XML record. The entry-point module passes all
five checks in a fresh process. All 13 candidate tests pass. The earlier
incomplete run and two temporary-directory setup errors are retained in
the audit logs; the final suite uses a fresh repository-local temporary
directory. No solver assertion or tolerance was relaxed.

The production suite includes both eightfold grids, repeated Stage 53,
Stage 35 at 90% speed and unchanged conservation checks. The audit
confirms byte-identical v16 production, unchanged historical goldens,
811 protected evidence files and all frozen v16 campaign files. The
cached conditioned-shock rerun is exactly equal to its earlier results.

[Final audit and logs](../validation/campaigns/20261105T142211039689Z_slc_aungier_experimental_v16/verification.json).
