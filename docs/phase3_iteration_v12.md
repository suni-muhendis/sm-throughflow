# Phase 3: duct wall integration and conditioned iteration (v12)

The simulator is `slc_aungier_experimental_v12`. This is a numerical recovery
study, not empirical qualification. Model coefficients, experimental targets,
acceptance gates, the `1e-7` outer tolerance and `1e-8` wall tolerance are unchanged.
Scores remain disabled. V11 source and all its results are retained.

## Numerical changes and independent checks

V11 integrated blade-wall gaps in eight subintervals but each duct-wall gap in
one. The first failed interval of projected Stage 35 reading 3979 was captured
verbatim, including both edge states and the incoming conserved wall state.
Its single-step residual floor is 0.0221768511, against a required `1e-8`.
V12 applies the task-owned wall subdivision count to both types of gap. The
captured duct interval now converges at 8/16/32 substeps with unchanged residual
tests; the thickness differences decrease. This changes the wall discretization,
not a loss, deviation or viscosity coefficient. Linear edge interpolation, the
EOS density and conserved `r*Ctheta` interpolation remain unchanged. Blade work
is still applied only once per row. This does not establish asymptotic accuracy
of the collateral blade-force correction or wall fields inside blade rows.

For nearly planar subsonic flow, streamline curvature gives an approximate
position residual `R = -(I + Ky^-1 Km)e`, where `Ky` is the positive transverse
second-difference operator and `Km` includes the axial second difference and
`(1-Mm^2)`. Diagonal damping shrinks useful low-frequency corrections as axial
spacing decreases. V12 instead applies `P = (Ky + Km)^-1 Ky` to the dimensional
position residual and takes a half step before Anderson extrapolation. The
half step is a fixed numerical relaxation, not case tuning. Both operators use
nonuniform three-point differences. Wall displacements are zero; at axial
endpoints the preconditioner leaves the supplied residual unchanged. These are
conditions on the update, not new flow boundary conditions. The existing
meridional Mach cap of 0.95 is used only in the preconditioner coefficient.

This is an approximate inverse of curvature coupling, not the full nonlinear
Jacobian. Its rationale follows the standard distinction between the original
equations and an iteration preconditioner described in [Templates for the
Solution of Linear Systems](https://www.netlib.org/templates/templates.html).
Tests independently check known low/high-frequency discrete modes and a
continuous polynomial solution on stretched grids, with second-order refinement.
Acceptance still uses the **unpreconditioned** position, field, blockage and
mixing residuals. No smoothing changes the solved geometry or physical equations.

Anderson least squares now uses stored differences of the **raw** residuals;
dividing differences of preconditioned steps by the current diagonal weights
would be incorrect. Existing bounded extrapolation, rollback, eight smaller
trial steps and Novak fallback remain. Failures during construction of an
iteration step now retain the attempt's rejection trace as well.

If the requested fine grid fails, the production adapter may solve grids
1, 2, 4, ... below the requested duct subdivision count, then retry that count.
It interpolates only checked, fully converged stream positions. Temperature
scope and conservation checks run before accepting each seed. Full physics,
wall resolution and the task's per-attempt iteration budget remain the same at
every grid. The final solution must satisfy the requested grid's equations.
Every failed original attempt, coarse-grid attempt and final retry carries its
grid count and role, with total work summed across all levels. A proven inlet
sonic capacity violation does not trigger this fallback. Numerical/current-iterate
capacity failures are never relabeled as proven choke.

The separate research refinement sequence still uses explicit interpolated
starts and a 400-iteration per-attempt budget, matching the v11 study. It is
reported separately from production startup under the frozen 200-iteration jobs.

## Matched experimental outcomes

All 108 frozen jobs were rerun; targets, flow readings, geometry perturbations
and admission interpretations were preserved. Counts include all requested
failures, not only a favorable subset. "Projected" is the historical projected
annulus adapter; "original" preserves the published annulus contours.

| Selection | V11 | V12 |
|---|---:|---:|
| All projected jobs | 25/54 | 40/54 |
| All original-annulus jobs | 27/54 | 35/54 |
| Projected experimental readings | 14/33 | 28/33 |
| Original-annulus experimental readings | 16/33 | 23/33 |
| Stage 35, projected | 6/8 | 8/8 |
| Stage 35, original annulus | 7/8 | 8/8 |
| Previously successful jobs lost | — | 0 |

The Stage 35-38 core reading set now converges at 17/17 in both representations.
Stages 52 and 53 reach 3/6 and 3/5 respectively in both. Stage 55 reaches 5/5
only with projected geometry; all five original-annulus jobs remain outside
model scope. The Stage 8E clearance family still has zero successes in both
representations. These differences must not be removed by choosing the more
favorable geometry interpretation for training.

Reading 3979 at 90% speed converges in 16 outer iterations with default eight
wall substeps. Its stage pressure ratio is 1.6271169160 and efficiency is
0.8639110590. Against its measurements the pressure-**rise** error is +9.2538%
and efficiency error is -0.1089 percentage points. With one wall substep the
case still fails numerically; at 16/32 substeps the pressure ratios are
1.6271794720/1.6272935350. The whole-machine differences do not shrink at a
clear asymptotic rate, despite the independent local duct ODE accuracy check.

All 96 measured-state row closures and six row-adapter sensitivity results are
bitwise identical to v11. Repeated anchor outputs (metrics, states, row outputs,
diagnostics and classification) are bitwise identical within v12 as well.

## Axial resolution and effort

These are successful final-attempt iteration counts in the separate 400-budget
coarse-to-fine study. A dash means no converged solution within that protocol.

| Duct subdivisions | Projected v11 | Projected v12 | Original v11 | Original v12 |
|---:|---:|---:|---:|---:|
| 1 | 109 | 17 | 108 | 21 |
| 2 | 188 | 27 | 196 | 37 |
| 4 | — | 43 | — | 55 |
| 8 | — | 54 | — | 64 |

V11's separate 1000-budget study recovered projected grid 4 after 787 iterations,
but still failed original grid 4 and both grid 8 cases. V12 needs no relaxation
of the acceptance residuals or increase of the per-attempt budget.

| Duct subdivisions | Projected PR | Projected efficiency | Original PR | Original efficiency |
|---:|---:|---:|---:|---:|
| 1 | 1.8249700984 | 0.8229998653 | 1.8233474997 | 0.8220481158 |
| 2 | 1.8190687384 | 0.8225156236 | 1.8147447981 | 0.8208277597 |
| 4 | 1.8172520239 | 0.8223427413 | 1.8113608419 | 0.8201495682 |
| 8 | 1.8167301272 | 0.8222846405 | 1.8102057392 | 0.8198829374 |

From grid 4 to 8, pressure ratio changes by about 0.029% projected and 0.064%
original; efficiency changes by 0.0058 and 0.0267 percentage points. This is
evidence for these two anchor calculations, not a universal mesh-independent
operating envelope or a proof for polyline corner curvature.

Production startup with a 200-iteration **per-attempt** budget also reaches both
grid 8 solutions, with metrics bitwise identical to the research sequence.
Counting all failed initial attempts and coarse grids, it consumes **145 outer
evaluations projected and 181 original**, not merely the final 54/64 iterations.
All conserved balances and every returned wall residual pass their original
checks. Requested-grid failures and seed-grid work are retained in the records.

## Accuracy and remaining qualification limits

Only shared successful experimental readings are used below, avoiding selection
bias from newly recovered cases. These are P90 absolute errors, not improvements
in overall empirical coverage masquerading as accuracy improvements.

| Representation/cohort | Quantity | V11 | V12 |
|---|---|---:|---:|
| Projected, 14 readings | Stage pressure-rise error | 27.4439% | 27.4418% |
| Projected, 14 readings | Efficiency error | 5.00195 pp | 5.00237 pp |
| Projected, 14 readings | Rotor temperature-rise error | 18.9596% | 18.9555% |
| Original, 16 readings | Stage pressure-rise error | 26.2010% | 26.1998% |
| Original, 16 readings | Efficiency error | 4.84996 pp | 4.85009 pp |
| Original, 16 readings | Rotor temperature-rise error | 17.9985% | 17.9942% |

The Stage 35-to-36/37/38 efficiency directions remain reversed relative to
experiment. Absolute error, radial-profile, family-response and independent
holdout gates remain unmet. Wall/in-row interpolation and collateral closure
still need spatial qualification. Numerical failures, original Stage 55 scope
violations and clearance-family failures remain explicit. The work establishes
recoverable numerical solutions for the requested cases; it does not authorize
performance scores, a trusted Mach/Reynolds range or compressor design ranking.

## Final frozen evidence and verification

Production source SHA256: `b456b469028d7aeac6ff952c717ef92080539c4a28602ae501c74fae36ffff06`.

| Evidence | Campaign |
|---|---|
| matched | [20261104T225400132975Z_slc_aungier_experimental_v12](../validation/campaigns/20261104T225400132975Z_slc_aungier_experimental_v12/manifest.json) |
| wall | [20261104T225410435085Z_slc_aungier_experimental_v12](../validation/campaigns/20261104T225410435085Z_slc_aungier_experimental_v12/manifest.json) |
| axial | [20261104T225452065445Z_slc_aungier_experimental_v12](../validation/campaigns/20261104T225452065445Z_slc_aungier_experimental_v12/manifest.json) |
| production | [20261104T225503343516Z_slc_aungier_experimental_v12](../validation/campaigns/20261104T225503343516Z_slc_aungier_experimental_v12/manifest.json) |
| comparison | [20261104T225803330970Z_slc_aungier_experimental_v12](../validation/campaigns/20261104T225803330970Z_slc_aungier_experimental_v12/manifest.json) |
| axial_comparison | [20261104T225727068868Z_slc_aungier_experimental_v12](../validation/campaigns/20261104T225727068868Z_slc_aungier_experimental_v12/manifest.json) |

Final audit: [20261104T230116743078Z_slc_aungier_experimental_v12](../validation/campaigns/20261104T230116743078Z_slc_aungier_experimental_v12/verification.json).

The full suite passes 250 tests with one import-order skip; that skipped
lazy-import test passes in isolation, so all 251 distinct tests are verified.
Tests include conservation, deterministic independent-process results,
actual 3979 and production grid-8 regressions, nonuniform analytic checks,
failed seeds, exhausted budgets and step-construction telemetry. All 811
protected historical files and 114 v11 baseline JSON artifacts are unchanged.

Earlier exploratory v12 campaigns and the first failed test run are retained
but are not pooled with this final source. The first run exposed an invalid
error-constructor argument on exhausted outer budgets and sandbox temporary
directory failures. The former was fixed; the complete suite was rerun with
a repository-local temporary directory. All experimental and resolution
campaigns were rerun against the final source; their physical states and
metrics exactly reproduce the initial numerical implementation. Final logs
and superseded diagnostics are distinguished in the audit. No historical
result, physical coefficient, experimental target or acceptance gate was rewritten.
