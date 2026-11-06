# Throughflow reliability and validation plan

Date: 2026-11-04. Status: Phases 0 and 1 implemented in part; Phase 2 machinery implemented for v8;
Phase 3 audit completed with failed gates; v9 geometry and v10 wall/coupled numerical repairs evaluated;
v11–v12 curvature/grid repairs and v13–v14 family-response work are recorded separately;
acceptance gates remain open as detailed below. Historical audit observations
describe the pre-change working copy.

The [v14 shock integration milestone](phase3_family_v14.md) recovered
Stage 53 convergence with unchanged tolerances. The
[v16 comparison](phase3_geometry_v16.md) retains 75 of 108 converged
jobs and the [back-pressure passage study](phase3_backpressure_passage_v16.md)
documents the remaining pressure, loss and blockage discrepancies.
The Stage 35–38 design-response gate remains open.

The immediate goal is a physically credible, internally consistent
axial-compressor throughflow environment with an explicit validated domain.
The initial scope covers generated-design evaluation within that domain.
Industrial preliminary design and off-design analysis remain the broader goal.

The required fidelity is that of a throughflow method with empirical closures.
Success means that conservation, geometry, numerical convergence, model validity,
and useful design trends are demonstrated together. It does not require resolving
three-dimensional flow structures or matching CFD everywhere. Completing the code
changes below is necessary but does not by itself establish this capability; the
acceptance gates must pass in a declared domain.

The score stays disabled until the
[physical acceptance gate](compressor_validation.md) and the applicable
gates below pass.

## Evidence and starting point

The audit examined the working copy based on commit `77ba795`, including an existing
uncommitted adaptive loss-homotopy change and untracked internal-consistency studies.
Those changes were not created by the audit. On that working copy, the test suite
completed with **140 passed and 1 skipped in 31.57 seconds**. The skip was the
entry-point lazy-import check when another test had already imported the solver.

The full experimental validation campaign was not rerun during the audit. The
following counts and error statistics describe the existing result files, whose
metadata does not fully identify the producing working copy:

- There are 30 case directories; `validation/run.py` registers 20 cases/variants.
- The saved results contain 63 speed lines, including two with no solution found.
  On the other 61 lines, 242 of 282 measured-flow readings converged. The 282-point
  denominator excludes the two wholly failed lines.
- A model stall anchor was found on four of those 61 lines, within the sampled
  range. Failure to find one does not establish that no stall boundary exists.
- The internal-consistency admission study records 60 successes, 22 DRC rejections,
  and 15 simulation failures in 97 evaluations.
- The saved one-parameter study records 1,013 successes in 1,240 evaluations,
  including 39 failed interior points in 17 sweeps with successful points on both
  sides. These need classification; a hole alone does not prove a numerical bug.

Recomputed sample standard deviations of the saved anchor errors are:

| Anchor error | Saved spread | Existing plan target | Sample count |
|---|---:|---:|---:|
| Relative pressure-rise error at peak efficiency, using PR - 1 | 9.03% | 2% | 61 lines |
| Peak-efficiency error | 3.97 percentage points | 1.5 percentage points | 61 lines |
| Relative peak-efficiency flow error | 3.89% | 1.5% | 61 lines |
| Relative choke-flow error | 4.25% | 1% | 25 comparable lines |

These pooled statistics mix machine families and speeds and are diagnostic, not
an independent release verdict. Excluding the cases with part-span dampers still
leaves pressure-rise and peak-efficiency spreads of 9.90% and 2.64 percentage
points over 31 lines. Missing damper physics does not explain the whole gap.

Sources: [validation plan](validation_plan.md),
[experimental report](../validation/reports/consistency.md),
[internal consistency](../validation/reports/internal_consistency.md), and
`validation/results/*.json`. The internal-consistency report and studies were
untracked at audit time; preserve their provenance before relying on them for a
release. Historical results must not be overwritten by a new campaign.

## What reliable design feedback requires

The environment must distinguish five properties:

1. **Physical verification:** mass, energy, angular momentum, and thermodynamic
   admissibility satisfy the equations and assumptions being implemented.
2. **Numerical reliability:** a declared solution has converged at all coupled
   levels, is adequately resolved, and is reproducible under the declared setup.
3. **Empirical validity:** losses, deviation, blockage, and resulting performance
   have measured error bounds over a stated machine and operating domain.
4. **Design-response validity:** changes in geometry produce credible changes in
   performance. Family deltas, local sensitivities, and rankings must be checked;
   conservation or small average error alone does not establish them.
5. **Resistance to invalid optimization:** generated designs cannot improve their
   score through ignored geometry, unvalidated extrapolation, numerical clipping,
   inconsistent averaging, or hidden changes to the evaluator.

Repeatability can reproduce a wrong model exactly. Internal consistency must
therefore be paired with independent physical evidence. Conversely, one good
experimental match does not establish numerical robustness over a design space.
The release claim must describe the intersection of these demonstrated properties.

## Phase 0 Preserve the baseline and declare the first scope

- [x] Record the code commit, dirty patch identity, inputs, source-data hashes,
  Python and dependency versions, platform, numerical settings, and all active
  physics options for every campaign. Hidden switches such as the class-level
  mixing option must be represented in the effective configuration.
- [x] Preserve existing studies and results. Write new campaigns to distinct
  locations; do not mix or overwrite results from different simulator versions.
- [ ] Establish a reproducible dependency set and portable numerical tolerances.
  Test deterministic repeatability within a fixed environment separately from
  cross-platform numerical agreement.
- [x] Define the initial supported subset: axial compressors, gas and temperature
  range, blade families, geometry ranges, stage count, speed range, Mach/Reynolds
  ranges, clearances, and supported inlet conditions. Dynamic quantities require
  checks after the flow is solved as well as geometry checks before solving.
- [x] Mark unsupported features explicitly, including dampers, bleed, variable
  geometry, or modern sections where they are not represented and validated.

Deliverable: an executable baseline and a domain specification with each limit
marked as physical, correlation-derived, numerical, or validation-derived.
An omitted mechanism that materially affects a case excludes that case from the
release claim until its effect is represented or bounded.

## Phase 1 Make successful results trustworthy

### P1.1 Resolve the supplied passage geometry

`SlcAungierSimulator.build()` currently places quasi-normals only at inlet, outlet,
and row edges. Intermediate contour features can disappear from the solution.
In an audit probe, a local inlet-duct contraction reduced the minimum annulus area
to about 8.05% of the original while leaving existing quasi-normal radii unchanged.
DRC and the simulation passed; the pressure ratio changed by only about 2e-15.

- [x] Include critical contour stations and provide axial refinement appropriate
  to duct curvature, area changes, and blade-row modelling assumptions.
- [x] Replace hard-coded row-to-station index arithmetic with an explicit mapping.
- [x] Check geometric resolution and reject unresolved or unsupported passages.
- [x] Verify a local constriction affects capacity or triggers an explicit limit.
  Also verify that redundant collinear contour points do not materially change
  results once the geometry and discretization are equivalent.
- [ ] Demonstrate axial and radial grid convergence independently.
  V7 resolves the iteration failure on all tested axial refinements (1/2/4/8/16)
  and records independent radial sensitivity (11/21/41). A defensible numerical
  uncertainty bound across the proposed design domain is still outstanding.

Acceptance: no admitted geometric feature can silently disappear; numerical
uncertainty is small relative to the smallest design improvement being claimed.

### P1.2 Use one geometric definition throughout

DRC uses the general camberline stagger calculation for MCA rows, while the
simulator uses the constructed MCA shape. Audit differences reached 4.38 degrees
on Stage 37's rotor and 5.61 degrees on Stage 18-13's stator. The audit also found
that crossed stator stage labels pass the current schema and DRC.

- [x] Share section geometry between DRC, throat, expansion-angle, and row-model
  calculations, including MCA shape and projection conventions.
- [x] Validate stage membership and supported row topology; stage reporting must
  not silently span unrelated rows.
- [x] Validate constructed sections and positive passages. Set explicit limits
  on unsupported spanwise oscillations and interpolation behaviour.
  V7 checks 41 sections and provisionally excludes repeated spanwise trend
  reversals. These are discrete admission checks, not a continuous-span proof;
  broader generated-geometry qualification remains in Phase 4.
- [x] Separate physically invalid geometry from correlation-range exclusions.
  Do not relax correlation limits merely to make a validation case pass.

Acceptance: accepted geometry has one consistent interpretation in every layer;
equivalent representations produce equivalent physical results.

### P1.3 Connect Reynolds effects and declare gas assumptions

The main simulator leaves blade-row `viscosity=None`, which sets the profile-loss
Reynolds correction to zero. The endwall model independently uses Sutherland's law
for air. Thus the gap is specifically the blade-row correction, not all viscous
effects.

- [x] Supply viscosity consistently with local thermodynamic states and the
  declared gas model; report per-row Reynolds numbers and range violations.
- [x] Verify pressure, temperature, and size changes with the expected Reynolds
  effects and similarity limits, without assuming Reynolds-independent similarity.
- [x] Declare a valid temperature range for constant cp. Add temperature-dependent
  properties before claiming regimes where the approximation is inadequate.

Acceptance: Reynolds corrections are demonstrably active, thermodynamic and
transport assumptions agree, and operating conditions outside their validated
range are identified.

### P1.4 Enforce coupled convergence and physical admissibility

The endwall march can exhaust its iteration limit without returning an explicit
failure. This did not occur in the audited reference solution. Separately, the
wall extrapolation in `smooth_loss` can produce negative values from nonnegative
input: `[0, 0, 0, 1, 0, 0, 0]` gives -0.25 at the two endpoints. This was reproduced
at function level, not in the complete compressor cases exercised by the audit.

- [x] Propagate inner-row, quasi-normal, endwall, mixing, and outer-loop convergence
  status with residuals, station/row identity, and iteration counts.
- [x] Validate mass and energy balances, Euler work, positive thermodynamic states,
  and loss/entropy admissibility under the active model. With radial mixing,
  test the correct global entropy production and flux balance rather than imposing
  a false requirement that every individual stream surface gain entropy.
- [x] Investigate positivity-preserving loss treatment consistent with the source
  model and its intended conservation properties. Do not hide a failed physical
  closure with an undocumented numerical floor.
- [x] Report loss, Mach, blockage, and other limiter activations. Distinguish
  calibrated model limits from numerical safeguards; define which activations are
  validated and which exclude a point from usable design feedback.

Acceptance: a successful result includes evidence of adequate convergence and
physical admissibility. A finite summary alone is insufficient.

## Phase 0/1 implementation evidence (2026-11-04)

The checked items above refer to implementation and declared restrictions, not
experimental acceptance. See [the scope specification](throughflow_domain.md)
and [v6 implementation results](phase01_implementation.md). Subsequent changes and
frozen v7 evidence are in [the refinement report](phase1_refinement.md).

- Baseline: `validation/campaigns/20261104_phase01_baseline/` captures the v5
  commit, dirty/untracked source, historical results, dependencies and complete
  synthetic inputs/results. Existing data and v5 goldens were preserved.
- v6 uses all genuine passage vertices, explicit row indices and task-owned duct
  refinement. Nonlinear wall contours inside a single-gap row are rejected.
  Redundant collinear points give identical operating-point results.
- Constructed MCA stagger and section definitions are shared. V7 checks sampled
  blade intersections and projected chord at 41 span positions, reconstructing
  sections from interpolated inputs. Monotone or single-extremum input fields
  are admitted; repeated reversals are explicitly unsupported. This provisional
  scope restriction is not a calibrated physical limit or a CAD certificate.
- Sutherland viscosity is active in blade-row Re corrections. Pressure,
  temperature and geometric similarity probes check its response. The 200-400 K
  constant-cp restriction is provisional; a validated Mach/Re envelope is still
  empty and every result explicitly says so.
- All required iteration levels and final balance checks are enforced. Negative
  smoothed loss causes rejection; no positivity-preserving replacement closure
  is claimed. Final loss, blockage and meridional-Mach limiter flags remain
  unqualified for usable design feedback. Optional mixing is checked globally.
- Fixed-runtime determinism and portable tolerances are tested locally. The
  dependency constraints and CI matrix are configured; cross-platform execution
  remains to be observed, so that combined checklist item is still open.
- V7 resolves the v6 refined-grid iteration failures with bounded coupled
  Anderson acceleration, retaining unchanged residual tolerances and deterministic
  Novak fallback. All five axial refinements pass within 400 iterations; original
  and accelerated iteration agree on a common refined root. Local +/-3% flow
  probes also pass. The finest axial pair differs by about 0.0404% of predicted
  pressure rise and 0.000825 efficiency percentage points. These observations
  do not establish an asymptotic error bound, resolution of every admitted
  geometry, or experimental accuracy; the general resolution gate stays open.

## Phase 2 Separate physical limits from numerical failures

At audit time, `validation/run.py` collapsed `ChokedError`, numerical failures, and some
input/model failures into `None`. Its choke search therefore located a reachable
solution boundary without independently proving a physical choke boundary.

- [x] Preserve structured reasons for invalid geometry, unsupported physics,
  numerical nonconvergence, physical choking, and stall-criterion crossing.
  Keep them compatible with sm-core through structured diagnostics where possible;
  a shared-contract change requires a separately authorized task.
- [x] Add continuation from neighbouring operating points with adaptive steps,
  while retaining a deterministic initialization and fallback policy.
- [x] Compare cold starts, continuation from both flow directions, and admissible
  restart states. Diagnose differences instead of selecting a favourable branch.
- [x] Distinguish throat/flow-capacity evidence from failed iteration. If the
  boundary remains numerical, label it as such and do not use it as measured choke.
- [x] Resolve or explicitly bound the recorded interior holes. Preserve partial
  maps and per-point outcomes rather than losing subsequent points after one error.
- [x] Report total fallback effort and runtime, not only the final outer iteration
  count. Profile representative successful and difficult cases before optimizing.

Acceptance: the declared stable operating region has adequate solution coverage;
boundaries have a physical or numerical classification; path sensitivity and any
remaining gaps are documented. Stall indicators are not presented as a validated
system surge prediction.

Implementation evidence: [Phase 2 off-design report](phase2_offdesign.md).
V8 preserves all outcomes, checks independent inlet-duct capacity, compares cold
and both continuation directions, bounds adaptive searches, and records aggregate
effort plus separate wall-time telemetry. All 39 historical interior-hole brackets
were reconstructed and found outside the current geometry scope; they are not
claimed repaired. The synthetic local map passes the path checks. General stable
map coverage and empirical boundary accuracy remain open acceptance gates.

## Phase 3 Validate physics and design response within the scope

The existing diagnosis identifies speed-dependent rotor deviation/work errors:
excess work below design speed and insufficient work in some high-speed cases.
It also records unsuccessful trials of alternative corrections. Use that evidence
when selecting new experiments rather than repeating the same adjustments.

- [x] Test row models at measured inlet states to separate closure errors from
  the coupled throughflow response. Track deviation, meridional velocity, work,
  loss, blockage, and downstream incidence together.
- [x] Keep subsonic/transonic, dampered/undampered, speed, loading, Reynolds, and
  machine-family groups separate. Report failures as well as successful-point errors.
- [x] Evaluate changes against both total quantities and measured radial profiles,
  using explicit averaging definitions consistent with each experiment.
- [x] Check family deltas, geometry sensitivities, and meaningful ranking changes.
  Do not impose universal monotonicity where physical coupling can reverse a trend;
  use controlled cases and experimentally supported trends.
- [ ] Quantify uncertainty from missing clearance, axial location, inlet profiles,
  and measurement uncertainty. Keep source transcriptions unchanged.
- [x] Freeze acceptance thresholds and development/holdout membership before
  looking at new holdout outcomes. Related variants from one rig must not be
  treated as independent evidence without justification.
- [x] Set both absolute error and spread limits appropriate to each claimed use.
  The existing spread targets are a starting point, not industrial standards.
  If calibration is justified, keep it source-supported or independently validated,
  explicit, versioned, task-owned, and frozen before holdout evaluation.
- [x] Treat predicted improvements smaller than the relevant numerical/model
  uncertainty as indistinguishable for the supported claim, not proven gains.

Acceptance: a frozen model passes the stated error, coverage, profile, and
design-response criteria on independent cases within the declared domain.
If it fails, improve the model or narrow the domain; do not silently weaken the
criteria after inspecting the holdout.

Phase 3 audit executed on 2026-11-04; see [results and evidence](phase3_validation.md).
The completed checkboxes denote implemented experiments/diagnostics, **not a
passed empirical acceptance gate**. There are 96 measured-state row closures
and 54 coupled/sensitivity jobs. Exact geometries fail admission; only 12/33
selected projected experimental comparisons converge (12/17 among projected
DRC-admitted cases), and no supported joint core cell passes deviation and loss
together. Nominal family rankings can reverse. Isolated tests supply exit Vm;
they do not independently validate meridional velocity or wake blockage.

The uncertainty item remains partial: sensor bounds and controlled input
sensitivity were quantified, but failed perturbations/refinements, missing
covariance and reconstructed rotor-exit states prevent a complete bound.
Independent holdout acceptance has not been attempted or earned. Phase 3
acceptance remains open; these results do not establish Phase 4 acceptance or
justify score activation. No calibration or simulator-source change was made
in this audit.

## Phase 4 Qualify the environment for generated designs

Experimental reference machines sample a limited part of the geometry admitted by
the schema. An automated designer will also explore unusual combinations and
boundaries. The public environment path must therefore be tested in addition to
the direct solver path used in the current experimental validation.

- [ ] Run matched cases through both the environment and direct solver; explain
  intentional DRC exclusions and check agreement where both admit the case.
- [ ] Exercise generated and perturbed designs inside the proposed domain,
  including sharp spanwise changes, nearly closed throats, contour features between
  stations, extreme clearances, and conditions near model/solver limits.
- [ ] Search deliberately for implausibly high efficiency or pressure rise,
  missing geometry effects, loss clipping benefits, and other exploitable results.
  Recheck apparently best designs with finer resolution and independent evidence.
- [ ] Verify that design inputs cannot select physics, numerical tolerances,
  calibration, operating requirements, or the score definition.
- [ ] Distinguish inability to evaluate a design from established physical
  infeasibility. Preserve that distinction in the feedback consumed downstream.
- [ ] Require physical validity and domain eligibility before any performance
  score is made usable; do not score by favourable metrics alone.
- [ ] Enable a separately versioned score only after the physical acceptance gate
  and the above generated-design checks pass. Freeze simulator and score versions
  before producing training data; retain their provenance in every record.

Acceptance: the environment provides useful, reproducible design feedback without
known routes to gaining score through unrepresented geometry or invalid physics.
Top candidates still carry the model's stated uncertainty. This establishes a
credible training evaluator within scope; it does not guarantee the resulting
model's engineering competence, which requires separate evaluation.

## Phase 5 Expand multi-stage and industrial capabilities

These items extend scope after the initial reliable evaluator is established.
Bring an item forward only when the first declared task family requires it.

| Capability | Work and evidence required |
|---|---|
| Measured multi-stage machines | Validate stage matching and error accumulation on a measured three-stage case, then a longer compressor. Synthetic repeated stages are verification, not experimental validation. NASA 74A's cited report tests the first three stages, not the complete five-stage design. |
| Spanwise mixing | Keep the existing optional model explicit; validate its effect on multi-stage profiles and conservation before making it part of a supported profile. |
| Inlet profiles | Expose task-owned radial P0, T0, and swirl with a consistent inlet boundary-layer state; the solver core already accepts profiles. |
| VIGV and VSV | Add operating-point schedules with correct geometry updates and measured off-design matching. |
| External bleed | Add explicit mass, energy, and angular-momentum accounting; validate the extraction model and downstream response. |
| Working-point solution | Support corrected flow/speed and operating-point searches by pressure ratio or outlet pressure with classified failures. |
| Gas and modern blade scope | Extend gas properties and blade families only with supporting validity evidence; lean/sweep effects require an appropriate physical model as well as geometry fields. |
| Preliminary design assistance | Generate initial annulus, stage loading, and blading from engineering targets; this is optional for a workflow in which the model supplies the design. |
| Engineering reporting | Export station fields, velocity triangles, loading/reaction, losses, residuals, maps, and uncertainty. Build interactive tooling over the stable API. |

## Completion and release decision

All of the following must be satisfied for the initial usable evaluator:

- [ ] The supported input and operating domain is explicit and enforced.
- [ ] Admitted geometry is represented, all required sub-solves converge, and
  physical balances/admissibility checks pass.
- [ ] Resolution, initialization, determinism, and map coverage meet stated limits.
- [ ] Frozen experimental validation passes for both performance and design response.
- [ ] Generated-design searches reveal no unresolved route to favourable scores
  through known implementation or validity gaps in that domain.
- [ ] Success, unsupported conditions, numerical failure, and estimated physical
  limits are distinguishable in the returned evidence.
- [ ] A tagged, reproducible simulator and score identify every usable result.

Any change capable of moving results requires the appropriate simulator or score
version boundary under repository rules. Historical records and old tags remain
unchanged. Code and documentation completion must not be reported as physical
acceptance until the evidence above exists.

The first implementation package is Phases 0 and 1: baseline provenance, passage
representation, shared geometry, Reynolds coupling, topology, and trustworthy
convergence/validity diagnostics. Phases 2 through 4 establish suitability for
model-generated compressor design. Phase 5 expands the supported engineering use.

## V9 geometry and numerical follow-up (2026-11-04)

See [the matched v8/v9 report](phase3_geometry_convergence_v9.md) and its archived
108 outcomes. This follow-up does not close the empirical acceptance gate.

- [x] Preserve original interior wall controls separately from blade-edge flow
  stations; include them in stream-surface geometry and mid-chord section radii.
- [x] Reject an unresolved internal annulus throat instead of silently omitting it.
- [x] Repair one-sided hub-speed bracketing and the lagged inverse-velocity
  instability; verify captured real-machine station failures and analytic flows.
- [x] Rerun the same 54 jobs on v9 with identical inputs and with original annuli,
  retaining every failure and separating changed geometry from changed numerics.
- [ ] Resolve remaining endwall/outer-loop failures and recover lost Stage 37/38
  points without changing physics coefficients or loosening residual tolerances.
- [ ] Obtain a converged axial refinement sequence for the experimental anchor;
  21 radial surfaces now converge, but four duct subdivisions still fail.
- [ ] Establish full empirical accuracy, design-response and independent holdout
  acceptance. More successful perturbations alone do not qualify an evaluator.

The next numerical work should isolate the divergent endwall states and couple
them to safeguarded outer updates, then repeat the frozen comparisons. Keep
finite-state failures distinct from independently established physical limits.
Before altering curvature treatment, test close-station sensitivity against
analytic geometry and conservation; do not erase real contour features to gain
convergence. Stage 55's internal annulus throat needs an internal row-flow model
or an explicitly justified scope restriction, not an admission bypass.

## V10 wall and coupled-iteration follow-up (2026-11-04)

See [the v10 report](phase3_convergence_v10.md). The original-annulus Stage 37/38
points are recovered, but the earlier broad endwall/outer-loop item is not fully
closed: the half-gap and axial refinement problems persist, and the projected
anchor regresses.

- [x] Capture actual failing wall intervals and demonstrate why a large
  trapezoidal step can have no positive boundary-layer root under deceleration.
- [x] Add task-owned wall subintervals and full-state residual acceptance with
  bounded effort; retain numerical/physical failure distinctions.
- [x] Restore wall corrections, mixing and row state after rejected coupled
  trials; verify rollback with an injected failure and identical recovered root.
- [x] Repeat all 108 v9 jobs and run 16/32-subinterval sensitivity separately.
- [ ] Establish asymptotic wall-resolution convergence and qualify the
  interpolated in-row edge fields/collateral correction. Small measured spreads
  alone are insufficient.
- [ ] Resolve the projected Stage 35 anchor regression and the four-subdivision
  core-flow failure, using preserved attempt summaries and targeted captures.
  Export detailed rejection traces in campaign outcomes and thrown attempts;
  currently they are only available on returned solver convergence objects. Test any
  curvature or interpolation change against analytic geometry and conservation
  before repeating the same experimental selection.
- [ ] Pass the existing absolute-accuracy, radial-profile, design-response and
  independent-holdout gates before using performance scores for training.

## V11 curvature and iteration follow-up (2026-11-04)

See [the v11 report](phase3_curvature_v11.md). The model coefficients and
acceptance thresholds remain unchanged. Smooth-path discretization accuracy,
nonlinear iteration success and empirical validity are separate requirements.

- [x] Demonstrate the alternating-mode nullspace and inconsistent endpoint
  curvature in the composed first-difference operator before replacing it.
- [x] Use direct local quadratic derivatives; verify circles on uniform and
  smoothly stretched grids, rigid-motion invariance and straight paths.
- [x] Derive and verify the high-frequency damping restriction on an independent
  near-planar flow; use B*=4 with the new stencil rather than reusing B*=16.
- [x] Preserve detailed rejected-step evidence on failed coupled-map attempts and in
  experimental campaign output, including failed wall subintervals.
- [ ] Extend trace coverage to exceptions outside the coupled-map guard,
  including construction of an acceleration step.
- [x] Complete and audit the matched 108-job v10/v11 campaign and separate wall
  and axial-resolution studies. Keep the axial study's 400-iteration budget
  and interpolated starting positions distinct from the 200-iteration cold
  comparisons; no automatic production mesh-continuation policy is introduced.
  The separate 1000-iteration study recovers projected four-subdivision flow
  after 787 accelerated iterations. Original four-subdivision and both
  eight-subdivision cases remain unresolved; none is called physical choke.
- [ ] Recover projected Stage 35 reading 3979 without hiding its cold-start hub
  endwall failure at station 5 (a duct interval), and qualify wall integration
  across both blade and duct intervals. Revisit whether collateral correction
  should be enforced at row exit or at every auxiliary wall subinterval; do not
  infer resolution independence from the current small non-asymptotic spreads.
- [ ] Improve the conditioning of fine-grid coupled iteration. The independent
  modal test supports B*=4, but original-annulus four-subdivision continuation
  still misses tolerance after 1000 accelerated iterations. Distinguish this
  slow iteration from the failed cold-start capacity bracket and assess any
  preconditioner on analytic nonuniform grids before experimental reruns.
- [ ] Qualify corner treatment and the single-gap blade-row approximation on
  axial refinement. A piecewise-linear wall corner has no classical point
  curvature; retaining vertices is not the same as resolution independence.
- [ ] Pass absolute-accuracy, profile, family-response and independent-holdout
  gates before enabling scores. No numerical recovery alone closes those gates.

## V12 completion of the requested numerical recovery (2026-11-04)

See [the v12 report](phase3_iteration_v12.md) for the complete matched comparison.
This section supersedes the numerical recovery items above; it does not close
their remaining physical-resolution and empirical qualification requirements.

- [x] Capture the actual v11 reading 3979 duct-wall failure; recover it with
  task-owned duct substeps at the original wall residual tolerance. Verify the
  local replay and an independent exponential ODE, including second-order error.
- [x] Add an elliptic position preconditioner and raw-residual Anderson fit;
  verify low/high grid modes and continuous solutions on stretched grids.
- [x] Recover original and projected Stage 35 4/8-subdivision solutions under
  the existing 400-iteration research protocol, without tolerance changes.
- [x] Add bounded, deterministic production coarse-grid initialization after
  failed fine-grid attempts; retain failed starts, all seed grids, physical
  checks and complete effort. Test failed seeds and proven physical limits.
- [x] Extend failure trace coverage to construction of iteration steps.
- [x] Rerun the same 108 jobs against frozen v11: 52 to 75 successful outcomes,
  no lost successes, unchanged 96 measured-state closures and six sensitivities.
  Keep production startup, research refinement and wall resolution separate.
- [ ] Establish full wall/in-row spatial accuracy, especially the location
  of collateral blade-force closure. The small 8/16/32 whole-machine spreads
  still do not have a demonstrated asymptotic order.
- [ ] Qualify corner treatment and single-gap blade rows; the remaining
  Stage 35 4-to-8 differences are small but not a universal grid-independence
  result. Extend resolution checks to recovered higher-loading cases.
- [ ] Resolve the remaining numerical/scope failures and pass the unchanged
  absolute-accuracy, profile, family-response and independent-holdout gates.
  Performance scores and an empirically trusted Mach/Reynolds envelope remain
  unavailable until those gates pass.

## V13 family-response investigation (2026-11-05)

See [the v13 report](phase3_family_v13.md). The family-efficiency gate remains open.

- [x] Isolate shock, profile/endwall, Reynolds, leakage and incidence contributions
  with explicit counterfactuals on frozen v12; distinguish model probes from evidence.
- [x] Correct the tangent-entry substitution in DCA/MCA shock expansion using actual
  relative inlet angle and a surface tangent in the same meridional frame.
- [x] Keep all frozen measured readings, numerical settings and historical results
  separate; compare the same 108 requests with v12 and preserve unfavorable changes.
- [ ] Resolve the measured low/high aspect-ratio efficiency ordering. The v13
  correction does not do this, and it must not be represented as empirical progress.
- [ ] Validate a transonic loss closure with shock/endwall interaction and actual
  surface/foot geometry on independent machines before using efficiency ordering
  for design-training labels. A fit to these four development anchors is insufficient.

## v14 follow-up: sonic-cut integration and shock-foot geometry

See [the v14 report](phase3_family_v14.md) for the matched v13 comparison.

- [x] Separate the Stage 53 inner-iteration failure from the full-model sonic
  loss jump; retain both captured failures and alternative-iteration evidence.
- [x] Integrate the shock pressure defect across each sonic-cut mass cell and
  recover the original Stage 53 design point without changing tolerances.
- [x] Replace quantized foot vertices with a continuous interpolant and locate
  the foot after projection of the complete surface onto the row cone.
- [x] Repeat all 108 frozen jobs, 96 row closures and six sensitivities against
  v13, preserving failures and slightly worsened pressure/temperature errors.
- [ ] Resolve the Stage 35–38 efficiency ordering. Both aspect-ratio pairs
  and the 35→37 loading pair still have the wrong sign.
- [ ] Independently validate a general operating-point-dependent transonic
  loss/geometry closure and its design response on held-out machines. Do not
  substitute source PHISS tables or case-specific efficiency offsets.

## v15 follow-up: equivalent camber and reference-loss consistency

See [the v15 report](phase3_family_v15.md).

- [x] Inspect the original NASA BLADE program and invert its equivalent-camber
  design rule while preserving absolute angular momentum.
- [x] Verify the inverse against forward-designed synthetic blades, cylinder
  limits, rotation signs, similarity, valid domain and exit-cache updates.
- [x] Apply the same annular deviation to reference loss and actual exit flow;
  keep the off-design incidence extension explicit and version the change.
- [ ] Resolve the reversed Stage 35–38 efficiency ordering. The equivalent-
  camber correction does not close this item.
- [ ] Reproduce NASA conical section coordinates before changing planar blade
  geometry again; validate any operating-point-dependent shock/boundary-layer
  closure with independent measurements and held-out machines.

- [x] Repeat the frozen 108 jobs, 96 row closures and six sensitivities against
  v14: 75/108 still converge with no lost successes. Record worsening family
  differences and pressure/temperature errors alongside smaller eta errors.

## Post-v15 investigation: candidates rejected (2026-11-05)

See [the candidate report](phase3_candidate_v16.md). Production remains v15.

- [x] Build source-native conical and flow-dependent shock reference probes;
  verify independent analytic limits and retain negative coupled results.
- [x] Repeat all 108 frozen jobs, 96 row closures and six sensitivities for the
  MCA shock candidate. Preserve all 75 successes and Stage 53, but reject the
  worsened family response; do not publish it as a simulator correction.
- [x] Add a necessary development screen for signed efficiency responses,
  omitted predictions and lost successes, separate from qualification.
- [ ] Resolve the Stage 35-38 ordering. This remains unfinished.
- [ ] Verify full source manufacturing coordinates, then validate a general
  transonic shock/diffusion/separation closure on independent cascade data.
  Couple entropy and blockage without double counting existing loss terms.
- [ ] Preserve sonic-cell integration, Stage 53 and eightfold-grid regressions
  when promoting a future numerical change under a new simulator version.

## v16 analytic geometry correction (2026-11-05)

See [the v16 geometry report](phase3_geometry_v16.md). This production version
is distinct from the rejected research candidates described above.

- [x] Remove nearest-sample MCA thickness/transition constraints, sampled
  maximum camber and finite-difference edge tangents. Verify analytic geometry
  and small design responses against independent circular limits and frozen v15.
- [x] Fix small-camber cancellation exposed by the independent geometry tests.
- [x] Repeat all 108 v15 jobs, 96 row closures and six sensitivities. Preserve
  every job classification, Stage 53 metrics and bitwise repeatability.
- [x] Investigate a detached-shock model and explicitly delimit its incomplete
  unchoked branch. Do not promote it or extrapolate its AVDR correction.
- [ ] Resolve the Stage 35–38 efficiency ordering. The analytic geometry
  correction does not resolve the family-response or absolute-accuracy gates.
- [ ] Complete and independently validate the transonic operating branches,
  contraction and shock/diffusion/separation interaction; preserve sonic-cell
  integration and convergence tolerances before promoting a physical closure.

## Post-v16 interaction investigation (2026-11-05)

See [the interaction report](phase3_interaction_v16.md). Production is unchanged.

- [x] Add explicit choked internal-shock reference states and back-pressure
  queries to the research oracle; test area/mass/energy relations, admissible
  branch selection and exit-dependent cache boundaries.
- [x] Preserve a visually checked primary Rotor 37 loss-budget table, including
  the uncertainty and non-independent shock/profile decomposition.
- [x] Test a source-based compressible-circulation hybrid on the same 108 jobs,
  96 conditioned rows and six sensitivities. Preserve all 75 successes and
  reject the unchanged wrong response directions and worse eta errors.
- [ ] Resolve Stage 35–38 ordering with an independently validated annular
  shock / blade-boundary-layer / entropy / displacement-thickness closure.
  A general Mach multiplier or a diffusion correction alone is insufficient.
- [ ] Complete subsonic supercritical and regime-transition treatment; verify
  sonic-cell integration, startup, Stage 53 and fine grids before promotion.
