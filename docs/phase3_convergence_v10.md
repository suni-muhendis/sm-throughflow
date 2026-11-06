# Phase 3 follow-up: wall integration and coupled convergence, v10

Date: 2026-11-04. This changes numerical integration and the coupled solution
policy, not fitted loss/deviation coefficients. It does not qualify a physical
operating envelope or enable scoring.

## Failure mechanism and repairs

The v9 failures were captured before changing production source. A single large
trapezoidal wall step can have no positive solution under strong deceleration.
For a locally growing momentum thickness, `M' = k M`, the trapezoid amplification
factor is `(1+k h/2)/(1-k h/2)`; it is negative for `k h/2 > 1` even though the
continuous solution stays positive. The adverse-velocity contribution estimated
with the limiting H1 gives 1.183 for the captured Stage 38 stator hub interval
and 4.058 for the Stage 35 half-gap stator shroud interval. More fixed-point
iterations, or a nonlinear optimizer on that same coarse interval, cannot fix
this discretization defect.

V10 therefore adds **task-owned wall integration subintervals**: eight per
blade-row gap by default, configurable from one to 32. Duct intervals stay on
their flow grid. These are auxiliary boundary-layer integration points; they
do not introduce core-flow states, duplicate row work, or solve internal blade
forces. Edge fields interpolate between the solved stations, with density
consistent with the ideal-gas EOS and r*Ctheta used for swirl interpolation.
The wall arc length comes from the retained annulus controls; auxiliary radius
and slope still use endpoint interpolation. This remains an explicit model
approximation, not a resolved in-row flow solution.

Wall convergence now checks all three conserved-state fixed-point components,
the collateral force correction, theta11, H1 and total force defect. Slow or
growing Picard iteration falls back to a bounded residual solve. The
[SciPy least-squares solver](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html)
supplies trial steps; its termination flag is never sufficient for acceptance.
The independently measured residual must satisfy the unchanged 1e-8 threshold.
Every map evaluation, including finite-difference Jacobian probes, counts
against `endwall_max_iterations` for that subinterval. The default is 200 per
subinterval, so subdividing increases the possible total inner work budget.
Force-defect saturation uses an algebraically equivalent reciprocal expression
at large positive arguments, avoiding overflow without clipping thickness.

The outer loop now evaluates accelerated trials transactionally. A failed
sub-solve or excessive coupled residual growth restores wall corrections,
mixing state, row convergence state and caches before trying a smaller ordinary
step. At most eight reductions are attempted from a complete checkpoint. Every
rejected evaluation consumes the existing outer iteration budget and remains in
the returned solver's repositioning telemetry. The experimental campaign
serializer retains attempt summaries and aggregate effort, but does not export
that detailed rejection trace; an attempt that throws also loses its local
trace. Preserving these traces across all failure paths is a remaining
observability task. Inner failure and unresolved current-iterate capacity are
still not physical choke/stall proofs.

## Frozen comparison and source

- V9 baseline: `20261104T200124147703Z_slc_aungier_experimental_v9`.
- Complete v10 rerun: `20261104T203655068245Z_slc_aungier_experimental_v10`.
- Separate 16/32 wall-resolution study:
  `20261104T203736428503Z_slc_aungier_experimental_v10`.
- Complete comparison analysis:
  `20261104T205243013117Z_slc_aungier_experimental_v10`.
- Production SHA-256:
  `1813d4b197e9ef09e63b303fa72591c768fa64f345175258f15792db26bb611b`.

Paths are under `validation/campaigns/`. The complete rerun keeps all 108 v9
jobs, with identical designs, operating points and measurements, and the same
200 outer iterations per attempt at 1e-7 tolerance. The changed wall resolution
and per-subinterval budget are explicit; this is not an equal-total-inner-work
comparison. Both projected and original annulus inputs are retained. Numerical
failures, excluded research geometries and model limits remain in denominators.
The same 96 measured-state closure records and six adapter sensitivities are
rerun separately. No measurement transcription is edited.

Commands:

```powershell
.venv/Scripts/python -m validation.compare_convergence_v10 --workers 3
.venv/Scripts/python -m validation.refine_endwall_v10
.venv/Scripts/python -m validation.report_convergence_v10 <coupled-campaign> <refinement-campaign>
```

Correct initial wall-gap captures are in
`20261104T202105726767Z_slc_aungier_experimental_v9`; the earlier
`20261104T202020314879Z` capture recorded the final failing iterate instead of
the initial predictor and is superseded. Exploratory v10 campaign
`20261104T202816498115Z` was interrupted after five points while the coupled
safeguard was being developed; it is incomplete and is not pooled with final
evidence. `20261104T203428582567Z` is the three-point guarded-iteration probe.

## Matched results

| Selection | v9 projected | v10 projected | v9 original annulus | v10 original annulus |
|---|---:|---:|---:|---:|
| All requested jobs converged | 22/54 | 22/54 | 22/54 | 27/54 |
| Experimental operating points converged | 11/33 | 12/33 | 11/33 | 16/33 |
| Admitted core experimental points converged | 11/17 | 12/17 | 11/17 | 16/17 |
| Stage 35 | 4/8 | 4/8 | 7/8 | 7/8 |
| Stage 36 | 3/3 | 3/3 | 3/3 | 3/3 |
| Stage 37 | 1/3 | 2/3 | 0/3 | 3/3 |
| Stage 38 | 3/3 | 3/3 | 1/3 | 3/3 |
| Stage 52/53/55 | 0/16 | 0/16 | 0/16 | 0/16 |
| Common-flow Stage 8E family | 0/8 | 0/8 | 0/8 | 0/8 |
| Perturbation/refinement/repeat checks | 11/13 | 10/13 | 11/13 | 11/13 |

Original-annulus inputs recover all three Stage 37 points and the 90% and 100%
Stage 38 points, with no lost v9 success. This is improved numerical coverage,
not a validated 16-point operating envelope. Original annulus inputs still use
the adapter's blade and scalar edge-plane approximations.

There is a regression on projected geometry: Stage 35 point 3978 and its exact
repeat now fail. The projected 4004 point and Stage 37 point 4182 are recovered,
so the aggregate 22/54 conceals a changed success set. The failed anchor prevents
projected family deltas and anchor-based design rankings from being evaluated.
The original anchor and repeat have identical metrics, stations, row diagnostics
and outcome diagnostics. The projected anchor and repeat reproduce the same
failure; failure repeatability is not a successful performance validation.

V10's original-annulus 54 outcomes contain 27 converged, 15 numerical failures,
four unresolved capacity limits, three invalid states and five unsupported
conditions. Projected inputs contain 22 converged, 22 numerical failures, six
unresolved capacity limits and four invalid states. The original Stage 55
internal-annulus-throat exclusions remain explicit. None of these failed or
excluded points is removed from the reported denominator.

## Accuracy and design-response evidence

To avoid improving an error statistic simply by changing the success set, the
following comparison uses only points converged in both versions. P90 means the
90th percentile of absolute error; pressure and temperature errors normalize by
the measured pressure/temperature **rise**, while efficiency is in percentage
points. These are descriptive statistics, not uncertainty bounds.

| Shared cohort | Quantity | v9 P90 | v10 P90 |
|---|---|---:|---:|
| Original annulus, 11 points | Stage pressure-rise error | 28.198% | 28.255% |
| Original annulus, 11 points | Stage efficiency error | 5.178 pp | 5.168 pp |
| Original annulus, 11 points | Rotor temperature-rise error | 19.521% | 19.566% |
| Projected, 10 points | Stage pressure-rise error | 29.270% | 29.328% |
| Projected, 10 points | Stage efficiency error | 4.067 pp | 4.071 pp |
| Projected, 10 points | Rotor temperature-rise error | 20.557% | 20.603% |

The numerical repair does not materially improve the existing experimental
accuracy. All 96 measured-state closure records and all six adapter sensitivity
records are identical to v9, consistent with unchanged row correlations.
Measured exit velocity is still supplied to those closure checks; they are not
independent full-machine predictions.

The original Stage 35 anchor's core exit-angle RMS changes from 1.9353 to
1.9290 degrees, still above the existing 1.5-degree screen. Its normalized
pressure-rise / temperature-rise / meridional-velocity shape RMS values change
from 0.04059 / 0.03261 / 0.02134 to 0.04045 / 0.03249 / 0.02136. Profiles retain
the same stator-trailing-edge comparison, available measured samples and common
experimental mass-flux normalization as the v9 analysis
(`20261104T201253955726Z_slc_aungier_experimental_v9`). There is no material
radial-profile correction from this numerical change.

The now-computable original-annulus Stage 35-to-36/37/38 family comparisons all
predict an efficiency increase where the measured peak-flow efficiency falls.
Stage 36's pressure direction is also reversed. Stage 37/38 pressure directions
agree but their delta errors are 0.0483 and 0.0879 in pressure ratio. These are
different machines at different measured peak flows, not controlled partial
derivatives, but they do not support design-ranking qualification.

Original-anchor clearance, chord, stagger and increased-gap perturbations solve.
Their finite differences remain diagnostics: sampled uncertainty has not been
fully resolved, and none is admitted as a validated design improvement. The
half-gap case remains an unresolved current-iterate capacity limit on original
geometry and a numerical failure on projected geometry. Four duct subdivisions
still fail for both representations. Twenty-one radial surfaces converge on
the original anchor with pressure-ratio change +0.000849 and efficiency change
+0.01963 percentage points; this does not replace an axial refinement sequence.

## Separate wall-resolution check

These are complete machine solutions on identical original-annulus inputs with
8, 16 and 32 auxiliary wall subintervals. All six outcomes converge; four new
runs supplement the two eight-subinterval outcomes from the full campaign.

| Point | Subintervals | Stage pressure ratio | Stage efficiency |
|---|---:|---:|---:|
| Stage 35, 100%, point 3978 | 8 | 1.816986460 | 0.821653567 |
| Same | 16 | 1.817112446 | 0.821648267 |
| Same | 32 | 1.817338992 | 0.821638610 |
| Stage 38, 90%, point 4133 | 8 | 1.732605697 | 0.854871447 |
| Same | 16 | 1.732973387 | 0.854871925 |
| Same | 32 | 1.733579656 | 0.854870813 |

The pressure-ratio spreads are 0.000353 and 0.000974, respectively. The successive
pressure changes grow from 8-to-16 to 16-to-32, so these results do **not** show an
asymptotic convergence sequence or establish a discretization error bound. The
interpolated edge field and subinterval collateral correction remain model-form
limitations to investigate. Small observed variation alone is not sufficient.

## Numerical verification

The full test suite passes: **227 passed, one skipped**, 363.58 seconds.
The skipped entry-point lazy-import test passes separately in 1.23 seconds; it
was skipped only because the combined run had already imported the solver.
Thus all **228 distinct tests** have been exercised successfully across the
full run and that isolated check, using the same final production source.
V5-v9 characterization values remain intact; v10 has separate values.
New tests replay actual failed wall gaps, verify the positive analytic
`exp(3m)` solution and second-order trapezoidal accuracy, exercise force-defect
saturation, and reject exhausted wall budgets. An injected failed coupled trial
poisons the wall correction cache; the rollback test proves that the poison is
discarded, the same root is recovered, and rejected work is counted.

The captured Stage 38 wall interval fails as one step and solves at 8, 16 and
32 steps without changing tolerance. The resulting theta11 spread is below 1%,
but not monotone because the profile closures are piecewise limited. The
captured Stage 35 half-gap layer can also be marched, yet becomes very thick:
this local integration result is deliberately not a machine capacity or
admissibility proof. Whole-machine verification and scope checks remain
necessary.

## Remaining limits

Recovered solutions are not experimental validation. The auxiliary in-row edge
interpolation and subinterval collateral correction need further resolution and
physical qualification. Small differences between 8/16/32 results do not by
themselves establish asymptotic convergence. Axial core-flow refinement and
the half-gap case remain separate checks; a solved wall equation alone cannot
make their complete machine solutions trustworthy. Existing measured-state
loss/deviation errors, uncertain design ranking and missing independent holdout
validation keep the empirical gate and score closed.

## Final evidence audit

Verification archive: `20261104T205722081159Z_slc_aungier_experimental_v10`.
It contains the final source/document snapshot, test logs, run logs and
`verification.json`. All 811 protected historical data/result files and
114 v9 baseline evidence JSON files match their recorded checksums. All
108 jobs preserve the v9 designs, measurements and task settings except
the declared simulator version and wall subdivision setting. The frozen
experimental protocol is unchanged. Production source matches the full
campaign, wall-resolution study and analysis. The 96 row closures and
six sensitivities are unchanged; the source diff is limited to the four
declared contract/simulator/endwall/outer-solver files. `git diff --check`
passes. No commit or push was made. The physical acceptance gate remains
open and the score remains disabled.
