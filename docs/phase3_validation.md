# Phase 3: empirical physics and design-response audit

Date: 2026-11-04. Frozen simulator: `slc_aungier_experimental_v8`;
physics profile: `axial_compressor_aungier_v2`.

## Decision

**No experimentally qualified operating envelope has been established.** The
Phase 3 experiments are implemented, but the empirical acceptance gate remains
open work. A converged calculation is not, by itself, validated design feedback.
The score remains disabled and successful environment results remain
`empirical_validation="pending"`, `score_eligible=false`.

The production source hash is
`5f1180923dba7379622d77bf035dc03fe9925ad9f6c6da857fe043e0ec425f8b`.
No production physics, constants, numerical algorithms or historical results
were changed in this phase. This is an audit of v8, not a newly calibrated model.
Validation adapters, analysis definitions and their tests are versioned by the
new campaign source archives; their quantities must not be pooled with legacy
validation analyses.

## Frozen experiment and evidence boundaries

[The protocol](../validation/phase3_protocol.json) was archived before new model
outcomes in
[the preregistration campaign](../validation/campaigns/20261104T182834171075Z_slc_aungier_experimental_v8/protocol.json).
It fixes the selected cases, operating points, perturbations, numerical budgets,
error thresholds and development/holdout policy. Thresholds are project
screening requirements, not an industry standard. No threshold was fitted to
this campaign's outcomes.

The seven machines with blade-element data are NASA Stages 35, 36, 37, 38, 52,
53 and 55. Their 48 readings give 96 rotor/stator closure evaluations and 864
radial locations. Related variants share rig families; 864 probes do not become
864 independent experiments. Previously exposed Lewis cases are development
data, not independent holdout.

The full-solver selection consists of each machine's measured peak-efficiency
reading at every transcribed speed, plus Stage 35's measured flow endpoints.
These are **measured** peak locations, not newly optimized model peaks. Eight
Stage 8E clearance comparisons use the midpoint of the common measured-flow
interval at 70% and 100% speed, interpolating observations without extrapolation.
Thirteen additional jobs examine the Stage 35 design-speed peak, including
clearance, gap, inlet blockage, metal-angle/chord perturbations, two refinements
and an identical-input repeat. The complete request has 54 jobs.

Every job retains its effective design/task, admission outcome, classification,
all cold/homotopy attempts and effort, and successful station/row fields. A
numerical failure or current-iterate capacity failure is not a physical choke
or surge measurement. No failed point is dropped or flow-matched to a guessed
choke anchor. The fixed budget is 200 outer iterations **per attempt**, 200
endwall passes, 11 surfaces and tolerance 1e-7; built-in deterministic fallback
can make total effort much larger. Runtime is telemetry, never an acceptance
criterion.

## Geometry coverage is a separate failure

The exact existing adapters for all 20 registered machines, covering 293
transcribed operating points, fail the current in-row wall-contour admission
rule. They contain wall vertices inside the model's single-gap blade rows.
No source CSV, admission rule or contour was silently changed to admit them.

Research inputs insert the original interpolated wall radii at every blade edge
and replace only the in-row contour with its straight edge-to-edge segment;
duct vertices and blade-edge planes are retained. Each input records wall
displacement relative to local span and annulus-area change. This is a changed
geometry and carries `release_evidence=false`. Small displacement does not
establish a small aerodynamic error.

Projected Stages 35-38 pass DRC. Projected 52/53 and the clearance family still
violate the provisional span-trend admission rule; Stage 55 violates the
thickness range. Their direct research solves deliberately bypass DRC, while
retaining the production convergence, balance and gas-scope checks. Those
outcomes are diagnostics, not accepted applications of the environment.

## What the isolated-row comparison means

The validation-only row factory uses the same production closures, sections,
Reynolds/viscosity treatment, throat, shock and clearance configuration. Its
equivalence to the production assembler is tested. It evaluates the original
row geometry without requiring an admissible whole annulus.

Inlet and exit states are reconstructed from printed total pressure/temperature,
meridional and tangential velocities, radii and actual rpm. Centimetres become
metres and N/cm2 become Pa. Rotor relative swirl is `C_theta - omega*r`.
Per-span axial coordinates come from the geometry table, retaining the cone
projection. Two explicitly unmeasured wall values close the radial arrays;
constant and linear extrapolation are compared at the anchor.

The closure receives **measured inlet and measured exit meridional state**.
Thus deviation, loss, conditional Euler work, wake blockage and downstream
angle error can be diagnosed, but meridional velocity and wake blockage are not
independently validated by this test. The downstream-angle error is a local
incidence perturbation proxy, not a solved inter-row redistribution. Coupled
exit-velocity profiles are checked separately.

NASA TP-1338 states that the close rotor/stator spacing prevented a station-2
probe survey. Rotor-exit states were inferred from downstream measurements and
design streamlines; pressure and temperature use different circumferential
averaging conventions. Therefore the row tests are conditioned on reduced
experimental states, not independent direct rotor measurements. The report's
Appendix B5 and the solver both normalize loss by inlet relative dynamic head.
Printed loss is retained as the observation; loss reconstructed from conservative
Euler work and an alternative actual-relative-enthalpy ideal state are also
reported to expose reduced-state inconsistencies. Neither diagnostic replaces
the printed observations. See
[NASA TP-1338, printed pp. 3-4 and Appendix B](https://ntrs.nasa.gov/api/citations/19790001889/downloads/19790001889.pdf).

Five questionable transcription marks remain visible in provenance. Stage 37,
reading 4188, has unprinted derived quantities at radial position 9. Its
available flow state is retained, absent deviation/loss values stay null, and
95% span is explicitly inferred from the report's radial-position numbering.
There is no invented loss/deviation value and no edit to the transcription.

Statistics first average the selected radial samples within each reading and
row, then compute bias, sample standard deviation and the 90th percentile of
absolute error across readings. Radial RMS is retained separately. Joint cells
split machine family, row, blade family, damper reporting, speed, Mach, Reynolds,
loading and core/endwall zone. A diagnostic candidate needs at least five
readings and two machine variants; these are still not independent rig families.
Core means use 15-85% span from the tip. Endwall statistics are separate and do
not inherit a core qualification claim.

| Conditional core result | Mean deviation error | Mean work error | Interpretation |
|---|---:|---:|---|
| Stage 35 rotor, 70% speed | -1.708 deg | +9.45% | Low-speed work bias persists at supplied measured Vm |
| Stage 35 rotor, 90% speed | +0.677 deg | -2.84% | Speed-dependent bias, not a constant offset |
| Stage 35 rotor, 100% speed | +0.722 deg | -2.21% | Work-error spread 4.26%, above the 2% screen |
| Stage 38 rotor, 100% speed | -1.864 deg | +8.96% | Core loss bias +0.0502 also exceeds the 0.02 screen |
| Stage 52 rotor, 100% speed | +1.287 deg | -7.68% | Passing mean deviation/loss does not validate rotor work |
| Stage 55 stator, 100% speed | -4.816 deg | not applicable | Large exit-angle bias despite small mean loss error |

The 36 occupied joint **core** cells contain ten with the minimum development
support; **zero** of those ten pass both deviation and loss screens. There are
another 38 endwall cells, 12 with that sample support, which are reported
separately. Looking only at marginal means can conceal these joint failures.

## Coupled results and design response

Of 33 selected full-solver experimental comparisons, 12 converge, 16 return
numerical failure, three return unresolved current-iterate capacity and two
return invalid state. There is no independent physical-limit conclusion among
those failures. On the subset whose **projected** geometry passes DRC, coverage
is 12/17 (70.6%), below the frozen 95% requirement. Overall research coverage is
12/33 (36.4%). All 16 fan-family jobs remain unresolved; the two Stage 52 invalid
states specifically report negative/non-finite loss after smoothing.

| Projected machine | Converged/requested | Pressure-rise errors at successful selected points | Stage-efficiency errors |
|---|---:|---:|---:|
| Stage 35 | 4/8 | -3.23% to +36.44% | -2.49 to +4.40 percentage points |
| Stage 36 | 3/3 | -1.01% to +19.63% | -2.35 to +2.90 pp |
| Stage 37 | 2/3 | +1.23% to +19.63% | -1.44 to +2.44 pp |
| Stage 38 | 3/3 | +1.39% to +18.49% | -2.39 to +2.05 pp |
| Stage 52 | 0/6 | unavailable | unavailable |
| Stage 53 | 0/5 | unavailable | unavailable |
| Stage 55 | 0/5 | unavailable | unavailable |

The intervals above describe successes only; failures still enter coverage and
prevent a statistics cell from passing. Low-speed pressure rise is systematically
high even where convergence and balances pass. At the Stage 35 design-speed
anchor, PR is 1.814835 against 1.842 and efficiency 0.820102 against 0.845.
Its core P0/T0-rise shape RMS values are 0.03956/0.03152, within the 0.05 shape
screen, but exit-angle RMS is 2.593 deg, above 1.5 deg, and Vm-shape RMS is
0.10448. Overall agreement cannot substitute for radial-profile agreement.

Nominal design rankings can reverse. At each machine's measured design-speed
peak, Stage 36 minus Stage 35 is **-0.025 PR and -2.40 efficiency pp in the data**,
but **+0.01438 PR and +0.249 pp in the model**. The delta errors are +0.03938 PR
and +2.649 pp, exceeding the frozen 0.02/1.5 pp screens. Different peak flows,
geometry projection and measurement uncertainty mean this is not a controlled
hardware derivative or a statistically resolved physical ranking. It does show
that the current predicted ranking is not qualified supervision for a designer.
Stage 37/38 pressure-ratio deltas also miss the 0.02 absolute delta screen.

All eight Stage 8E common-flow clearance jobs fail numerically. Their six
measured variant-minus-baseline deltas are retained, but no model delta or
validated clearance ranking is manufactured. At 100% speed the observed PR
deltas span -0.0732 to -0.1415 and efficiency deltas -3.15 to -5.85 pp. At 70%
speed the small measured changes do not follow that simple ordering. This is
another reason not to impose universal monotonicity, particularly when casing
recess and the part-span damper are unmodelled.

The identical-input Stage 35 repeat reproduces all six overall metrics exactly.
Stage 37's design-speed point converges only after ten cold/homotopy attempts,
1285 total outer iterations and 39333 station solves. Its approximately 544 s
runtime is machine-specific telemetry; it is not a timeout-based physics label.

## Averaging and uncertainty

Overall pressure ratio uses the report's energy average:
`mean_mass((P0/P01)^k)^(1/k)`, `k=R/cp`. Temperature ratio is mass averaged.
Stage efficiency uses rotor temperature ratio for the core-stage reports and
stage temperature ratio for the fan reports, as their definitions require.

Radial blade-element exit profiles are compared at the **stator trailing edge**,
not silently at a different downstream plane. Pressure/temperature-rise shapes
are normalized with common experimental mass-flux quadrature weights,
proportional to `rho*Vm*r*dr` over the measured span. This includes density and
unequal probe spacing, unlike the legacy `r*Vm` weighting. It is a quasi-axial
radial integration of the reported meridional state, not a claim to reconstruct
unmeasured wall layers or a full probe-plane coordinate transform. RMS is over
the available reported core samples; missing samples remain explicit.

For Stage 35, the stated instrument bounds are mass flow +/-0.3 kg/s, speed
30 rpm, angle 1 deg, temperature 0.6 K, inlet total pressure 100 Pa and exit
total pressure 1700 Pa (static-pressure bounds are also archived). Arithmetic
extreme combinations are reported, but they are **not confidence intervals**:
covariance, rotor-exit reconstruction, geometry/model-form uncertainty and
ambiguous transcriptions are not supplied by these bounds.

Anchor isolated-row sensitivity is modest for the two investigated assumptions:
linear rather than constant wall extension changes core rotor loss by about
0.00006; homogenizing the measured inlet changes rotor core deviation by about
-0.107 deg and loss by -0.00369. This does not establish a small uncertainty for
other machines or for coupled inlet/endwall redistribution.

For coupled geometry perturbations, unchanged numerical settings and explicit
effective inputs prevent a candidate from selecting its evaluator. The signed
metal-angle offsets are added to both rotor axial-plane angles; chord factors
keep edge planes, blade count and t/c fixed. These are local contract-parameter
responses, not experimentally measured derivatives of altered hardware.
Clearance and gap variations with a failed side yield an unresolved sensitivity
interval, not a zero effect. Predicted improvements below the observed numerical,
input or instrumental band are marked indistinguishable; exceeding a sampled
band alone is not proof of a design improvement.

| Anchor perturbation | Result | Delta stage PR | Delta stage efficiency |
|---|---|---:|---:|
| Clearance x0.5 | converged | +0.00440 | +0.209 pp |
| Clearance x1.5 | unresolved capacity | unavailable | unavailable |
| Row gap x0.5 | numerical failure | unavailable | unavailable |
| Row gap x1.5 | converged | +0.00692 | +0.122 pp |
| Inlet blockage -0.01 | converged | +0.01782 | +0.049 pp |
| Inlet blockage +0.01 | converged | -0.02411 | -0.217 pp |
| Signed rotor metal angles -0.5 deg | converged | -0.03650 | -0.223 pp |
| Signed rotor metal angles +0.5 deg | unresolved capacity | unavailable | unavailable |
| Rotor chord x0.98 | converged | -0.00608 | -0.118 pp |
| Rotor chord x1.02 | converged | +0.00716 | +0.185 pp |
| Radial surfaces 11 to 21 | numerical failure | unavailable | unavailable |
| Duct subdivisions 1 to 4 | numerical failure | unavailable | unavailable |

Both chord-response magnitudes are below the sampled input/instrumental band.
The negative-angle PR change exceeds the observed successful-input PR band,
but its other side and part of that uncertainty band are unresolved. None of
these trials establishes a usable design improvement. Instrument-only arithmetic
extremes at the anchor give PR 1.82342-1.86061 and conditional efficiency
0.81197-0.87701; they exclude substantial unknown uncertainty and must not be
presented as statistical confidence bounds.

The 21-surface solve exhausts the prescribed iteration budget; its returned
outer changes are 5.11e-5 and 6.10e-4, above 1e-7. The duct-refined solve cannot
find a hub velocity satisfying the required flow. Thus this real-machine anchor
has **no demonstrated radial or axial grid independence**, despite the earlier
synthetic refinement evidence. The two must not be conflated.

## Scope that can actually be claimed

| Region or capability | Evidence in this audit | Allowed interpretation |
|---|---|---|
| Algebraic balances and deterministic successful solves | Production verification plus regression tests | Numerical/internal consistency within the checked model |
| Row closures at relative Mach 0.444-1.501 and chord Re 4.72e5-1.67e6 | 48 experimental readings; data concentrated at 100% speed outside Stage 35 | Tested diagnostic range, **not** a validated rectangular Mach/Re domain |
| Below Re 2.5e5 | No experimental coverage here | Reynolds-correction branch is unit tested only |
| Core-stage coupled research inputs | Projected geometries; some successful points and unresolved points | Case-specific diagnostics requiring reported errors and flags |
| Exact experimental machines in the current public contract | 0/20 admitted | No whole-tool experimental qualification |
| Stage 8E clearance ranking | Unmodelled part-span damper and casing recess, plus solver outcomes | No pure-clearance derivative or ranking qualification |
| Independent holdout, multistage design ranking, stall/surge boundaries | No acceptance evidence in this campaign | No claim; score remains disabled |

The existing structural/temperature restrictions in
[the domain document](throughflow_domain.md) still apply. In particular, the
200 K static/400 K total-temperature bounds are provisional model restrictions,
not experimentally established accuracy limits. Stage-count/schema limits do
not establish industrial multistage capability.

## Work required before an empirical acceptance claim

1. Establish an exact, qualified geometry representation for experimental
   machines, or qualify a documented approximation with independent evidence.
   Do not relax DRC solely to admit the data. Span-trend restrictions and the
   single-gap row limitation need distinct treatment.
2. Diagnose the coupled failure mechanisms and the measured-state deviation/work
   bias separately. Use the saved attempts/fields to distinguish root-finding,
   endwall coupling, negative smoothed loss and current-iterate capacity failures.
   A converged result still has to pass profile and absolute/spread screens.
3. Resolve missing clearance, inlet and station-location information, and repeat
   the sensitivity/refinement comparisons through both sides of the proposed
   domain. A failed perturbation cannot certify a finite uncertainty band.
4. Improve a source-supported physical closure only in a new simulator version;
   select/calibrate on development data, then freeze it before independent
   evaluation. A speed-specific offset fitted to these rows would not resolve
   the current lack of independent evidence.
5. Implement and qualify independent case adapters before using holdout. P&W's
   three-stage exit rigs already have transcribed measured overall performance;
   they need geometry, angle, station and running-clearance matching. LSAC needs
   complete geometry/profiles; NACA Langley uses Freon-12 and cannot be silently
   treated as fixed-property air. E3 also requires hotter-gas, bleed and vane
   schedule support. Design-analysis tables are not experimental observations.
6. After empirical acceptance, complete Phase 4 generated-design qualification
   before enabling any score or generating trusted performance supervision.
   Current outputs can support diagnosis and failure-class supervision, but
   successful values should not be labelled reliable design-optimum targets.

No independent holdout outcomes were inspected or fitted in this phase. Existing
holdout metadata/data availability was inventoried; the held-out comparison
remains pending, and at least two independent families are required.

## Reproduction and verification

The following archives contain exact inputs, source snapshots, runtime identity
and exclusively created outcomes:

- [Coupled jobs, effective inputs and geometry inventory](../validation/campaigns/20261104T184527810503Z_slc_aungier_experimental_v8/manifest.json)
- [Final measured-state row campaign](../validation/campaigns/20261104T184542071838Z_slc_aungier_experimental_v8/rows.json)
- [Final quantitative summary and acceptance gates](../validation/campaigns/20261104T190425436546Z_slc_aungier_experimental_v8/summary.json)
- [Joint and marginal row groups](../validation/campaigns/20261104T190425436546Z_slc_aungier_experimental_v8/row_groups.json)
- [Radial profiles](../validation/campaigns/20261104T190425436546Z_slc_aungier_experimental_v8/profiles.json),
  [family deltas](../validation/campaigns/20261104T190425436546Z_slc_aungier_experimental_v8/family_deltas.json),
  [uncertainty and ranking](../validation/campaigns/20261104T190425436546Z_slc_aungier_experimental_v8/uncertainty.json)
- [Failure details](../validation/campaigns/20261104T190425436546Z_slc_aungier_experimental_v8/failures.json),
  [reduced-measurement consistency](../validation/campaigns/20261104T190425436546Z_slc_aungier_experimental_v8/measurement_consistency.json),
  [holdout availability](../validation/campaigns/20261104T190425436546Z_slc_aungier_experimental_v8/holdout_inventory.json)
- [Checksums of input evidence](../validation/campaigns/20261104T190425436546Z_slc_aungier_experimental_v8/input_evidence_sha256.json)

![Measured-state rotor closure errors](../validation/campaigns/20261104T190425436546Z_slc_aungier_experimental_v8/row_errors.png)

![Coupled performance and coverage](../validation/campaigns/20261104T190425436546Z_slc_aungier_experimental_v8/overall_errors.png)

Commands are in [validation/README.md](../validation/README.md). No production
source changed, so the simulator version stays v8. The 811 baseline measurement,
historical result and report files remain byte-for-byte unchanged.

Fifteen new tests cover loss/frame/unit conventions, production row-factory
equivalence, geometry projection invariants, frozen numerics, measured-state
reconstruction, missing cells, quadrature, independent-sample counting,
no-extrapolation interpolation, family-delta units/signs and closed acceptance
gates. The complete regression invocation returned **210 passed, 1 skipped,
3 setup errors** in 875.05 s: all three setup errors were inability to create a
Windows sandbox temporary directory, before the affected tests ran. Those
three tests subsequently passed with a fresh repository-local `--basetemp`
(3 passed in 1.04 s). The final Phase 3 tests, including the later family-delta
test, passed separately (15 passed in 1.87 s). This is aggregate coverage, not
a claim that one full invocation returned an all-green result.
The final combined affected check passed **18 tests** (15 Phase 3 tests plus
the three recovered fixture tests) in 2.06 s with a fresh local temporary
directory. Python compilation and `git diff --check` also passed.

Earlier row adapter runs at `20261104T183800073333Z` and
`20261104T184220744908Z` retained a whole-row failure for missing derived cells;
they are superseded by the final row campaign's explicit null handling. The
first analysis at `20261104T190225696528Z` is superseded by the linked analysis,
which adds input-artifact checksums and explicit plot coverage. Their stored
results were not overwritten, and no production-model tuning occurred between
these audits.
