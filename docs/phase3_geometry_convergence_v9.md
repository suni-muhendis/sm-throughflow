# Phase 3 follow-up: geometry and convergence, simulator v9

Date: 2026-11-04. This is a numerical and geometry repair with a matched
experimental rerun. It is not calibration or qualification of an industrial
operating envelope. The score remains disabled.

## Changes and their physical meaning

The v8 audit rejected every original experimental annulus because interior
wall vertices could not coexist with a single-gap blade-row model. V9 separates
flow stations from geometric controls. Every non-collinear wall control remains
in the annulus. Flow is solved at row edges and duct stations; between them,
local annulus fraction is interpolated along each stream surface. Original wall
controls then enter arc length, slope and curvature. Blade-section construction
also uses the original mid-chord annulus radii. Row work and loss are applied
once, between the same two edge states.

This is still a blade-edge throughflow approximation. There are no internal
blade-force or flow states, no prediction of in-row separation, and no new 3-D
lean/sweep representation. The adapter's scalar edge planes and blade-family
assumptions remain. "Original" in the campaign means original **annulus inputs**,
not an exact reconstruction of the whole experimental machine. An interior
annulus throat smaller than both edge areas is explicitly unsupported, including
quadratic area extrema between polyline vertices. This prevents acceptance from
silently skipping a constriction that the single-gap flow model cannot resolve.

The distinction between blade-edge duct-flow methods and methods with internal
blade-force stations is also described in the [Ansys throughflow theory](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/wb_bm/bm_vista_tf_theory.html).
V9 does not claim the latter capability.

Two numerical defects were isolated using actual failing Stage 35 iterates:

1. The hub-speed search only moved downward when the first radial profile was
   inadmissible. A strong radial energy gradient can instead require a higher
   hub speed to keep the outer span flowing forward. V9 searches in both
   directions, bounded by positive hub static enthalpy, and approaches a lower
   admissibility boundary by bisection before declaring no resolved bracket.
2. Iterating the `f3/Wm` term in the radial momentum ODE was unstable at low
   velocity. With `u = Wm^2`, the same continuous equation becomes
   `u' = 2 f1 u + 2 f2 sqrt(u) + 2 f3`. V9 applies the integrating factor and
   trapezoidal quadrature to this equation. This changes the discrete operator,
   so v9 has its own characterization values. It does not alter a loss or
   deviation coefficient, clip velocity, or relax convergence tolerances.

The captured oscillating profile had residual 0.01262 after 200 v8-form inner
iterations. The squared formulation reaches residual below 1e-12 in nine
iterations at 20.82 kg/s. This is a local equation test; the complete half-gap
machine still has an endwall failure, which remains a failed outcome.

## Matched experiment and provenance

- Frozen v8 coupled evidence: `20261104T184527810503Z_slc_aungier_experimental_v8`.
- Frozen v8 row evidence: `20261104T184542071838Z_slc_aungier_experimental_v8`.
- V9 coupled/row rerun: `20261104T200124147703Z_slc_aungier_experimental_v9`.
- Production source SHA-256:
  `fdbb4502acb25d23d99bac1bf1c4129f95083e3796c83ae6824c251de3226363`.

All paths above are under `validation/campaigns/`. Run
`.venv/Scripts/python -m validation.compare_geometry_v9 --workers 3`.
It reads all 54 archived v8 jobs rather than reselecting successful points:
33 experimental comparisons, eight common-flow clearance-family cases and
13 perturbation/refinement/repeat checks. It runs each once with the identical
projected input and once with original annulus controls, for 108 outcomes.
Blade perturbations, operating points, inlet blockage, 200 outer iterations per
attempt and 1e-7 outer tolerance are unchanged. The same 96 measured-state
closures and six adapter sensitivities are rerun separately.

Comparison of v8 projected to v9 projected isolates the numerical/version
change; comparison of v9 projected to v9 original measures the geometry effect.
Cases excluded by other DRC rules remain research diagnostics. Failed points
stay in coverage denominators. Accuracy comparisons use an explicitly shared
converged cohort and also show all-requested statistics with missing outcomes.
Measured-state closure comparisons exclude only changed admission metadata.
They still supply measured exit Vm and are not independent Vm predictions.

The pre-change capture `20261104T194452331854Z_slc_aungier_experimental_v8`
contains the exact first failed station input. Exploratory v9 campaigns
`20261104T195322182545Z` (interrupted, incomplete, before squared velocity),
`20261104T195558129039Z` (oscillating-profile capture) and
`20261104T195926496051Z` (eight-point probe) are retained as development evidence;
they must not be pooled with the complete comparison.

Analysis and plot: `20261104T201253955726Z_slc_aungier_experimental_v9`.
Reproduce with `.venv/Scripts/python -m validation.report_geometry_v9 <campaign>`.
The analyzer requires matching production source, intact baseline checksums and
all 108 outcomes; it does not reinterpret v8 profiles using v9 geometry.

## Results: progress is local, overall experimental coverage is not improved

| Selection | v8 projected | v9 identical projected input | v9 original annulus |
|---|---:|---:|---:|
| All requested jobs converged | 20/54 | 22/54 | 22/54 |
| Experimental operating points converged | 12/33 | 11/33 | 11/33 |
| Admitted core experimental points converged | 12/17 | 11/17 | 11/17 |
| Stage 35 | 4/8 | 4/8 | 7/8 |
| Stage 36 | 3/3 | 3/3 | 3/3 |
| Stage 37 | 2/3 | 1/3 | 0/3 |
| Stage 38 | 3/3 | 3/3 | 1/3 |
| Stage 52/53/55 | 0/16 | 0/16 | 0/16 |
| Common-flow Stage 8E family | 0/8 | 0/8 | 0/8 |
| Sensitivity/refinement/repeat jobs | 8/13 | 11/13 | 11/13 |

Original-annulus admission improves from 0/20 registered geometries to 4/20
(Stages 35-38). Other provisional spanwise restrictions remain in force. Stage
55 and Stage 6-1 have an unsupported internal annulus throat; they are not
declared physically impossible. All five requested original Stage 55 operating
points are reported as unsupported rather than as a solver convergence result.

Against the same projected inputs, v9 newly solves clearance x1.5, stagger
+0.5 degrees and 21 stream surfaces, but loses Stage 37 reading 4182 at 100%
speed. That reading was already expensive in v8 (1,285 outer iterations over
ten attempts); v9 does not recover it at the frozen task settings. Original
annuli additionally recover Stage 35 readings 3989, 3985 and 4004, while losing
Stage 37 reading 4201 and Stage 38 readings 4133 and 4120 relative to the v8
projected baseline. These losses are retained, not excluded from the comparison.

The half-gap Stage 35 case now reaches the downstream equations but fails on a
non-finite stator shroud endwall residual. Four duct subdivisions still fail
outer/endwall convergence. No result in either category is relabelled as a
physical choke or accepted with a larger tolerance. For the original annulus,
11 to 21 radial surfaces changes anchor PR by +0.0008664 and efficiency by
+0.01990 percentage points; missing axial convergence prevents a general
resolution-independence claim.

### Accuracy and design response

Stage 35, 100% speed, reading 3978, measured mass flow 20.82 kg/s:

| Quantity | Experiment | v8 projected | v9 projected | v9 original |
|---|---:|---:|---:|---:|
| Stage total pressure ratio | 1.842 | 1.814835 | 1.814790 | 1.816078 |
| Report-basis stage efficiency (%) | 84.500 | 82.0102 | 82.0103 | 82.1690 |
| Core exit-angle RMS error (degrees) | -- | 2.5926 | 2.5923 | 1.9353 |
| Core normalized Vm-shape RMS error | -- | 0.10448 | 0.10451 | 0.02134 |

Original geometry materially improves this anchor's velocity profile, but the
exit-angle error remains above the preregistered 1.5-degree screen. P0/T0 shape
RMS errors slightly increase (v9 projected 0.03964/0.03161; original
0.04059/0.03261). It is not a uniform accuracy improvement.

On the same 11 experimental points solved by v8 and v9 projected, mean pressure
**rise** relative error changes from +12.0369% to +12.0184%, and efficiency bias
from +0.7241 to +0.7224 percentage points. On the eight points shared by v8
projected and v9 original, pressure-rise bias changes from +13.5955% to
+13.4332%, while efficiency bias changes from +1.0510 to +1.0899 points.
These are descriptive, dependent-sample statistics, not a validated error bound.

At the original-annulus anchor, clearance x0.5 changes PR by +0.002188 and
efficiency by +0.09922 points; clearance x1.5 changes PR by -0.002187 and
efficiency by -0.09944 points. This gives the expected local direction. The
projected x1.5 case instead shows a tiny +0.00710-point efficiency change,
illustrating why small design rankings are geometry-sensitive. The experimental
Stage 8E clearance family still has no converged predictions, so the local
trend is not experimentally validated. The nominal Stage 36-minus-35 ranking
at their measured design-speed peaks remains reversed: measured efficiency
delta -2.4 points versus model +0.2441 points with original annuli. The machines
and operating flows differ; this is not a controlled partial derivative.

All 96 measured-state closure outputs and all six adapter sensitivities are
bitwise equal to v8 after excluding admission metadata. Thus the measured-state
loss/deviation failures from the previous audit remain. Both anchor repeat
checks have all six overall metrics bitwise equal.

![Matched numerical coverage and common-point efficiency errors](../validation/campaigns/20261104T201253955726Z_slc_aungier_experimental_v9/comparison.png)

## Verification method

Regression tests replay the captured real-machine inputs, check mass and
rothalpy, compare different positive starting velocities and require bitwise
repeatability. An independent radial-enthalpy-gradient solution verifies the
squared-momentum transformation to roundoff. A quadratic-swirl analytic case
checks second-order radial accuracy. Uniform/free-vortex, lossless stage,
conical-flow, refinement, off-design and invalid-inner-solve tests remain in
the full suite. Original wall controls, equivalent collinear representations,
row-edge mapping and rejection of hidden internal throats have explicit tests.

The previous forced-vortex error was dominated by radial integration. V9
integrates that linear squared-velocity forcing exactly; the test now checks
the remaining 401-point inlet-interpolation error below 2e-7. Second-order
convergence is tested with nontrivial quadratic swirl instead of expecting an
already exact operator to show an artificial error ratio.

Full-suite run: 219 passed, one skipped and two pre-v9 Mattingly characterization
values failed (367.10 s). Their old values were retained, and separate v9 values
were added without changing tolerances. The final affected-suite run then passed
all 27 tests (7.24 s). Across these runs, all 221 non-skipped tests are verified
on the final production source. No production code changed after the full run.
All 811 protected historical measurement/result/report files match their baseline
checksums; v8 campaigns and the frozen protocol were not rewritten.

## Remaining model limits

Improved geometry representation and solution coverage do not resolve the
previous measured-state deviation/loss errors, radial-profile mismatch,
uncertain small design rankings or missing independent holdout validation.
Reversed flow, highly loaded endwalls, tightly spaced axial stations and
unresolved iterative capacity limits need further work. A failed inner solve
is not a physical stall/choke label. Successful points remain ineligible for
performance scoring until the empirical and generated-design gates pass.
