# Phase 3 follow-up: direct curvature and iteration stability, v11

Date: 2026-11-04. This changes the numerical geometry operator and base
iteration step. It does not recalibrate any blade-row correlation or qualify
an industrial operating envelope. The score remains disabled.

## Isolated defects and repairs

V10 evaluated curvature by differentiating the pointwise slope, itself obtained
from centered coordinate differences. Two centered first differences miss an
alternating station-displacement mode: on the test grid, a perturbation requiring
curvature magnitude 0.064/m instead produced about 3.6e-14/m. On a unit circular
arc the endpoint curvature approached -0.5/m instead of -1/m as the grid was
refined. Both defects are independent of compressor measurements.

V11 fits local parametric quadratics to three adjacent positions and evaluates
`kappa = -(z' r'' - r' z'') / (z'^2 + r'^2)^(3/2)` directly. The parameter is
polygonal arc length. Three-point one-sided fits close the two endpoints;
one/two-point paths have zero curvature. Nonpositive or nonfinite segment
lengths are rejected. No contour vertex is removed or rounded by this change.

Circular paths on uniform and smoothly stretched grids show second-order
convergence including the endpoints. Rigid-motion invariance, straight paths
and the alternating mode are tested separately. Abrupt mesh grading does not
guarantee second-order accuracy, and a true polyline corner has no classical
point curvature. Those qualifications matter for the experimental annuli.

The numerical choice is consistent with the direct differentiation of local
polynomials described in [NIST's numerical differentiation reference](https://dlmf.nist.gov/3.4).
The coupling of stencil, grid aspect ratio and damping is also the subject of
[Wilkinson's 1969 throughflow stability analysis](https://doi.org/10.1243/PIME_CONF_1969_184_168_02);
only its public abstract was consulted, not the unavailable full paper. The
following stability result is independently derived and tested in this repo.

## Why the base damping changes

For near-planar low-Mach flow of height L, a radial sine displacement and axial
wavenumber k give a linearized mass-position residual approximately
`-(1 + k^2 L^2/pi^2) * displacement`. The direct second difference resolves an
axial eigenvalue approaching `4/h^2`; the old composed first difference had a
different spectrum. With Novak's local damping asymptotic to `B* h^2/L^2`,
the high-frequency relaxed gain approaches `1 - 4 B*/pi^2`. This motivates
`B* < pi^2/2` for this model problem, rather than reusing B*=16.

V11 uses B*=4. In the independent near-planar annulus test, the measured mode
gains are -4.7064 versus -0.59135 for B*=16 and 4 (31 axial stations); at 61
stations they are -5.2627 versus -0.61222. The smaller step contracts the mode.
This is not a general nonlinear compressor convergence theorem. Anderson's
safeguards, all residual checks and conservation tests remain necessary.

The spherical-source-flow angular error changes with the corrected endpoint
operator: at 11 radial surfaces it is 0.00011634 degrees. The test keeps its
0.0001-degree target at 21 surfaces and additionally requires second-order
convergence over 11/21/41, rather than retaining the old coarse-grid boundary
error as a golden. The independent velocity and conservation checks also remain.

## Failure evidence

Rejected coupled-map trial traces now survive failures handled by the outer
safeguard, not just successful returned solver objects. These attempts record their repositioning method, accepted
and rejected steps, backtracking fractions and causes. Every trial still counts
against the outer budget. Wall failures also identify the failing subinterval.
The experimental serializer exports this evidence and wall residuals. Tests
inject persistent failures and verify eight recorded backtracks followed by the
terminal eleventh evaluation; failure classification remains numerical.
Exceptions raised outside the coupled-map guard, such as an error constructing
the acceleration step itself, still retain their cause and effort but may lack
the local rejection history. Extending that trace coverage is a remaining
observability task; it is not counted as a resolved failure path here.

## Reproducible campaigns

All paths below are under `validation/campaigns/`.

- Frozen v10 baseline: `20261104T203655068245Z_slc_aungier_experimental_v10`.
- V10 curvature research: `20261104T215514244640Z_slc_aungier_experimental_v10`.
- V10 research with interpolated coarse starts and B*=16:
  `20261104T215715167304Z_slc_aungier_experimental_v10`.
- Same research with B*=4: `20261104T220027199709Z_slc_aungier_experimental_v10`.
- V11 five-point pilot: `20261104T220510506824Z_slc_aungier_experimental_v11`.
- Matched 108 jobs: `20261104T220638956907Z_slc_aungier_experimental_v11`.
- Separate wall study: `20261104T220719303107Z_slc_aungier_experimental_v11`.
- Separate axial continuation study: `20261104T220809961902Z_slc_aungier_experimental_v11`.
- Separate higher-effort axial study: `20261104T221411788920Z_slc_aungier_experimental_v11`.
- Matched comparison analysis: `20261104T221939144850Z_slc_aungier_experimental_v11`.
- Axial resolution/effort analysis: `20261104T222547982708Z_slc_aungier_experimental_v11`.
- Production SHA-256: `81cba25a32cdff525c48bb8ca110d7f7a50b85b11aad6df4e2d5111b04ec5dd2`.

The three v10 research campaigns contain explicit overrides, are marked as
prototypes and are never pooled with standard v10 or v11 outcomes. V11's matched
campaign retains all 108 designs and operating points, 200 outer iterations per
attempt, 1e-7 outer tolerance and the same wall resolution/budget. It separately
repeats the 96 measured-state closure records and six adapter sensitivity records.

The axial continuation study uses 400 iterations per attempt and initializes
finer grids by interpolating positions from a converged coarser solution. It
uses the public low-level solver, does not forge the high-level off-design
restart key, and does not change the production cold-start policy. Its eight
requested outcomes remain separate from the 108-job matched comparison.
An additional eight-outcome study raises that declared per-attempt budget to
1000, retaining the same tolerance, geometry and continuation procedure. It is
not an equal-effort comparison, a change to the default production policy, or
evidence that the 200/400-step failures were successful.

## Complete matched comparison

| Selection | v10 projected | v11 projected | v10 original annulus | v11 original annulus |
|---|---:|---:|---:|---:|
| All requested jobs converged | 22/54 | 25/54 | 27/54 | 27/54 |
| Experimental points converged | 12/33 | 14/33 | 16/33 | 16/33 |
| Admitted core points converged | 12/17 | 14/17 | 16/17 | 16/17 |
| Stage 35 | 4/8 | 6/8 | 7/8 | 7/8 |
| Stage 36 | 3/3 | 3/3 | 3/3 | 3/3 |
| Stage 37 | 2/3 | 2/3 | 3/3 | 3/3 |
| Stage 38 | 3/3 | 3/3 | 3/3 | 3/3 |
| Stage 52/53/55 | 0/16 | 0/16 | 0/16 | 0/16 |
| Common-flow Stage 8E family | 0/8 | 0/8 | 0/8 | 0/8 |
| Perturbation/refinement/repeat checks | 10/13 | 11/13 | 11/13 | 11/13 |

The projected Stage 35 design anchor (3978) and its repeat are recovered, along
with points 3989 and 3985. Point 3979 at 90% speed is lost; that regression is
retained in the table and analysis, not hidden by the aggregate gain. The
original-annulus success set is unchanged. Both original and projected anchors
now repeat with exactly identical metrics, stations, row and outcome diagnostics.

The 54 projected outcomes consist of 25 converged, 17 numerical failures, eight
unresolved capacity limits and four invalid states. Original outcomes consist
of 27 converged, 13 numerical failures, eight unresolved capacity limits, one
invalid state and five unsupported conditions. Original Stage 55's unresolved
internal annulus throat remains excluded. All outcomes stay in denominators.

## Experimental accuracy has not been repaired

The paired comparisons below use only points converged in both versions, so
coverage changes cannot masquerade as improved accuracy. Pressure and
temperature errors normalize by the measured rise; efficiency is in percentage
points. P90 is the 90th percentile of absolute errors, not a confidence bound.

| Shared cohort | Quantity | v10 P90 | v11 P90 |
|---|---|---:|---:|
| Original annulus, 16 points | Stage pressure-rise error | 25.874% | 26.201% |
| Original annulus, 16 points | Stage efficiency error | 4.783 pp | 4.850 pp |
| Original annulus, 16 points | Rotor temperature-rise error | 17.403% | 17.999% |
| Projected, 11 points | Stage pressure-rise error | 28.532% | 29.330% |
| Projected, 11 points | Stage efficiency error | 4.034 pp | 4.423 pp |
| Projected, 11 points | Rotor temperature-rise error | 19.792% | 20.225% |

Original-anchor core exit-angle RMS improves slightly from 1.9290 to 1.8767
degrees but still exceeds the 1.5-degree screen. Its normalized pressure-rise,
temperature-rise and meridional-velocity shape RMS values are 0.04184, 0.03125
and 0.02658. The comparison remains at the stator trailing edge with the same
measured samples and experimental mass-flux normalization.

All 96 measured-state closure records and six adapter sensitivity records are
identical to v10. Their row coefficients, reconstructed states and measurements
are unchanged. These conditional closure checks still supply measured exit
velocity and are not independent full-machine predictions.

Stage 35-to-36/37/38 comparisons still reverse the measured efficiency direction
in both representations. Original-annulus efficiency-delta errors are 2.541,
0.807 and 2.179 percentage points; pressure-ratio delta errors are 0.03873,
0.04604 and 0.08008. The machines operate at different measured peak flows,
so these are not controlled partial derivatives; they nevertheless fail to
establish design-ranking reliability. Numerical correctness cannot be selected
by whether a discretization accidentally fits those measurements better.

## Separate wall resolution

| Original-annulus point | Wall subintervals | Stage pressure ratio | Stage efficiency |
|---|---:|---:|---:|
| Stage 35, 100%, point 3978 | 8 | 1.823408067 | 0.822053424 |
| Same | 16 | 1.823502166 | 0.822048579 |
| Same | 32 | 1.823669559 | 0.822039897 |
| Stage 38, 90%, point 4133 | 8 | 1.735404816 | 0.857291818 |
| Same | 16 | 1.735631531 | 0.857273029 |
| Same | 32 | 1.736018190 | 0.857240179 |

All six outcomes converge. The successive pressure-ratio changes still increase
from 8-to-16 to 16-to-32. Small spreads (0.0002615 and 0.0006134) therefore do not
establish asymptotic convergence or qualify the auxiliary in-row interpolation
and collateral-force correction.

## Separate axial resolution and effort

The following results use the Stage 35 design-speed anchor. The coarse cases
start cold; subsequent grids use the last converged coarser positions. Both
budgets require the same 1e-7 outer residual and independent balance checks.

| Annulus | Duct subdivisions | 400 iterations/attempt | 1000 iterations/attempt | Converged stage PR | Converged efficiency |
|---|---:|---|---|---:|---:|
| Original | 1 | converged | converged | 1.823408067 | 0.822053424 |
| Original | 2 | converged | converged | 1.814742281 | 0.820827352 |
| Original | 4 | failed | failed | unavailable | unavailable |
| Original | 8 | failed | failed | unavailable | unavailable |
| Projected | 1 | converged | converged | 1.825042654 | 0.823005723 |
| Projected | 2 | converged | converged | 1.819089433 | 0.822517613 |
| Projected | 4 | failed | converged | 1.817160052 | 0.822332842 |
| Projected | 8 | failed | failed | unavailable | unavailable |

The shared successful 1/2-subdivision metrics are identical across the two
budgets. The projected four-subdivision case converges in 787 accelerated
iterations from the two-subdivision solution. This establishes a resolved root
under that explicit research policy; the matched production cold-start job at
200 iterations still fails and is never replaced by this result.

The original four-subdivision warm attempt has position/field residuals
1.74e-6 / 3.16e-6 after 1000 accelerated iterations. The projected eight-subdivision
warm attempt has 1.90e-5 / 2.13e-5. Both fail the unchanged tolerance. Their later
cold/homotopy attempts also fail current-iterate capacity brackets, so the final
classification is `unresolved_capacity_limit`; the retained attempt histories
show that slow numerical convergence and cold-start admissibility are distinct.
Neither is proof of physical choking.

Original PR changes by -0.008666 from one to two subdivisions. Projected PR
changes by -0.005953 then -0.001929 from one to two to four. The projected trend
is encouraging, but the missing eight-subdivision solution prevents a defensible
asymptotic/error-bound claim. Original geometry has only two resolved levels.
These sensitivities and the retained wall corners remain explicit limitations.

## Test evidence

The full suite completed with **237 passed, one skipped in 627.86 seconds**.
The lazy-import test skipped because the suite had imported the solver; it
passes separately in 1.46 seconds. Thus all **238 distinct tests** have passed
on the same production source. The full suite includes synthetic 4/8/16 duct
refinement under the original 400-iteration and 1e-7 requirements, conservation,
repeatability, off-design failure classification and the new geometric/modal
and rejection-trace checks. V5-v10 characterization values remain intact and
v11 has separate values.

A diagnostic duplicate of the synthetic refinement subset was started while
the buffered full-suite log had not advanced. It was stopped once the full
suite demonstrated progress beyond those tests; that partial diagnostic log
is not counted as a completed additional verification run.

## Remaining qualification requirements

Smooth-curve numerical accuracy does not qualify piecewise-linear wall corners,
the single-gap blade-row approximation or empirical compressor performance.
Preserve failed points, check absolute and radial-profile errors on shared
cohorts, and retain all design-ranking failures. Neither a recovered solution
nor a smaller discretization error automatically qualifies performance scores
for training a compressor-design model.

## Final evidence audit

Verification archive: `20261104T222738318204Z_slc_aungier_experimental_v11`.
It contains the final source/document/test snapshot, logs and
`verification.json`. All 811 protected historical files and 114 v10
baseline evidence JSON files retain their recorded hashes. All 108 matched
jobs preserve designs, measurements and task settings except simulator
version. Four wall-study outcomes and sixteen axial-study outcomes are
complete and separately identified. Source hashes match all final v11
campaigns and analyses. The frozen protocol and historical characterization
tables remain unchanged. `git diff --check` passes; no commit or push was
made. Physical qualification and scoring remain disabled.
