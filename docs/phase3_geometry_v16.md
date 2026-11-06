# V16: analytic MCA construction; efficiency ordering remains unresolved

`slc_aungier_experimental_v16` removes a real geometry sensitivity defect.
It does **not** fix the reversed Stage 35–38 efficiency ordering or qualify
efficiency-based design labels. Scores remain disabled. This version is distinct
from the earlier, rejected research candidates whose filenames also contain
`v16`; those campaigns ran unmodified v15 with explicit research overrides.

## Defect and correction

The MCA surface builder located the maximum-thickness and arc-transition
constraints by selecting the nearest point in a 4,001-point meanline. It also
estimated endpoint directions by finite differences. The maximum-camber
location used by the deviation model was selected from 2,001 samples.
Consequently, a small change in a design parameter could leave the actual
blade unchanged, while larger changes jumped between sample points.

The v16 implementation in `correlations/blade_geometry.py`:

- evaluates position and tangent at the exact requested chord coordinate;
- puts the two surface arcs on the exact transition normal;
- places edge-circle centres using exact endpoint tangents;
- finds maximum camber from the horizontal tangent;
- integrates circular segments with a sinc/half-angle expression, avoiding
  cancellation at very small camber and retaining the exact straight limit.

This preserves the existing planar interpretation of the constant-turn
construction in [NASA TN D-7345](https://ntrs.nasa.gov/api/citations/19740009588/downloads/19740009588.pdf).
It is not a new conical-manufacturing reconstruction. No measured loss,
efficiency, PHISS table or per-stage coefficient enters the construction.

The first focused test exposed cancellation at 0.00001-degree camber. The
stable circular-segment displacement fixed it; the original tolerance was
retained. The failed test log is preserved with final evidence.

## Independent geometry response

`python -m validation.geometry_response_v16` loads only the frozen v15
geometry module from its source archive and verifies its Aungier dependency
is unchanged. It compares suction-surface ordinates at **fixed chord
coordinates**, avoiding a parameterization-motion artifact. The fixture is
a manufactured MCA section, not experimental validation.

| Perturbation in maximum-thickness position, chord fraction | v15 max ordinate derivative | v16 max ordinate derivative |
|---|---:|---:|
| 0.001 | 0.382330305 | 0.378462267 |
| 0.0001 | 0.477184249 | 0.378451950 |
| 0.00001 | 0 | 0.378451847 |
| 0.000001 | 0 | 0.378451846 |
| 0.0000001 | 0 | 0.378451849 |

The derivative of maximum-camber location with respect to transition location
also changes from an unresolved v15 value of about 0.002375 to a resolved
value of 0.2518524 at small steps. These are geometric derivatives, not claims
that aerodynamic design sensitivities are now experimentally correct.

[Frozen sensitivity study](../validation/campaigns/20261105T125512772642Z_slc_aungier_experimental_v16/sensitivity.json).

## Same experiment against v15

The [matched campaign](../validation/campaigns/20261105T124800167736Z_slc_aungier_experimental_v16/manifest.json)
uses all 108 frozen v15 design/task pairs, changing only simulator version.
It also repeats all 96 measured-state row closures and six adapter sensitivities.
The jobs include repeats, numerical grids and manufactured perturbations;
they are not 108 independent experiments.

- 75/108 jobs converge in both versions, with identical success IDs.
- Every job retains its classification: 20 unresolved capacity limits,
  seven numerical failures, five unsupported conditions and one invalid state.
- All 96 conditional rows evaluate; supplying measured states remains a
  diagnostic, not an independent coupled prediction.
- Stage 53 classifications and performance metrics remain bitwise identical.
- Stage 35 at 90%, both fourfold duct grids and both 21-surface grids converge.
- Both anchor repeats are bitwise identical, including station and row data.

At the same measured peak-flow readings in the original annulus:

| Stage | Measured eta (%) | v15 | v16 |
|---|---:|---:|---:|
| 35 | 84.500000 | 81.429081 | 81.428993 |
| 36 | 82.100000 | 81.986728 | 81.986560 |
| 37 | 84.000000 | 81.946445 | 81.946198 |
| 38 | 83.100000 | 82.610434 | 82.610931 |

The 35-to-36 and 37-to-38 changes are still +0.55757 and +0.66473 percentage
points instead of the measured -2.4 and -0.9 points. The 35-to-37 loading
direction is also wrong. The projected representation has the same three
wrong signs. The original-cohort P90 absolute eta error changes from
3.872239 to 3.872291 points; the projected-cohort value changes from
3.709419 to 3.709686 points. No experimental accuracy improvement is claimed.

[All outcomes, paired errors, preservation checks and failed family screen](../validation/campaigns/20261105T124800167736Z_slc_aungier_experimental_v16/analysis.json).

## Shock-model research and its limits

[Banjac et al. (2022), DOI 10.1115/1.4053852](https://doi.org/10.1115/1.4053852)
separates detached bow shocks, passage shocks and choked operating branches.
Its validation uses inviscid MISES calculations; it does not independently
validate shock-induced viscous separation. The paper also identifies axial
velocity-density ratio as important in throughflow application. Its simple
correction is not a verified extrapolation over these machines' full range.

`validation/bow_shock_reference.py` implements **only the unchoked supersonic
branch** as a research oracle using constructed surfaces. It checks shock
mass, momentum and energy balances, entropy, geometric residuals and bow-shock
limits. A bracket crossing a tangent pole is rejected rather than accepted
as a shock intersection. This is not the complete published model.

The [final diagnostic](../validation/campaigns/20261105T125349596467Z_slc_aungier_experimental_v16/manifest.json)
contains 44 rotor span evaluations, including eight extrapolated wall points.
Only 16 lie in that branch according to the borrowed choke-angle estimate;
28 are explicitly labeled unsupported choked counterfactuals. The normal API
rejects them. Their computed values must not be used as predictions. The
maximum accepted geometric residual is below 5.1e-14 chord. That verifies
equation solution, not experimental accuracy or the borrowed regime estimate.
The oracle is not installed in the production solver.

## Remaining physical work

The geometry quantization is now resolved, but it was not the cause of the
large family-ordering error. A defensible transonic correction still needs:

1. complete, independently checked choked/subsonic/supersonic branches and
   actual passage geometry, including source coordinate verification;
2. a consistent stream-sheet-contraction and post-shock diffusion treatment;
3. shock/boundary-layer interaction that accounts for both entropy and
   blockage without duplicating profile/endwall loss;
4. independent cascade measurements and held-out machines, followed by the
   same frozen comparison and unchanged Stage 53/grid/conservation gates.

No family-specific fit or borrowed CFD accuracy claim closes these items.
The solver remains unsuitable for labeling relative compressor efficiency merit.

Production source SHA256:
`96c0037b6c7ab70a5124b1bd8ef4a9cbbab452ed355743aea6afae98108ac43e`.

## Final frozen verification

The full suite passes **318 tests with one import-order skip** in 496.64 seconds.
The entry-point module passes all five checks in a fresh process, giving
**319 distinct verified tests**, including nine new analytic-MCA and
five research gas-dynamic/root checks. The suite includes repeated Stage 53,
Stage 35 at 90%, both eightfold grids and unchanged conservation tolerances.

The audit verifies 811 protected historical files, all v5-v15 golden
assignments, unchanged experimental inputs and exact campaign/current
production source identity. Only geometry and contract-version production
files changed. All 108 classifications and all Stage 53 metrics are preserved.

[Frozen verification, logs and input hashes](../validation/campaigns/20261105T125936001961Z_slc_aungier_experimental_v16/verification.json).
