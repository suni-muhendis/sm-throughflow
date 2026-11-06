# Experimental throughflow scope, simulator v16

Status: implementation scope and numerical verification, **not an experimentally
validated industrial operating envelope**. The score remains disabled. A successful
solution means that the implemented equations converged and passed the checks
below; it does not establish the accuracy of the empirical closures.

The active simulator is `slc_aungier_experimental_v16` and its frozen profile is
`axial_compressor_aungier_v2`. Both contract schemas are version 2. The
task contract accepts the active simulator and profile identifiers.

## Limits and their basis

| Quantity or feature | Admitted implementation | Basis and remaining evidence |
|---|---|---|
| Machine | Axisymmetric axial compressor, one shaft speed, optional IGVs | Model assumption; no turbines, counter-rotation, reverse flow or system surge dynamics |
| Stage membership | Unique rotor per stage; downstream stators belong to the most recent rotor; IGVs have no stage ID | Structural consistency, not aerodynamic validation |
| Stage count | Task default at most 20, configurable to 40; at most 80 rows | Resource/schema limit, **not** a validated 20- or 40-stage capability |
| Passage | Positive piecewise-linear hub/shroud separation; duct vertices become flow stations; interior row vertices remain geometric controls | Physical geometry plus discretization rule |
| Wall contour inside a row | Original polyline controls constrain interpolated annulus-fraction paths; interior area below both edge areas is unsupported | Single-gap blade-row approximation: no internal flow state, blade force distribution or internal annulus-throat capacity solution |
| Axial resolution | `duct_subdivisions` 1-16 per non-row interval | Numerical control; grid sensitivity still has to be checked for the particular design |
| Endwall integration | Task-owned `endwall_subdivisions` 1-32, default 8 per blade-row or duct gap; interpolated wall-edge states only | Numerical resolution, not internal core-flow/blade-force resolution; check 8/16/32 sensitivity |
| Endwall iteration budget | `endwall_max_iterations` 10-1000, default 200 map evaluations per subinterval including Jacobian probes; tolerance stays 1e-8 | Exhaustion is numerical failure; no optimizer termination flag substitutes for the physical-state residual checks |
| Radial resolution | 5-41 stream surfaces; 11 design sections | Numerical limit; input profiles interpolate linearly without overshoot |
| Blade families | NACA 65, C.4, DCA, MCA and the documented camberlines | Implemented Aungier/NASA geometry; not a modern arbitrary-section model |
| Section validity | Finite constructed surfaces; no sampled surface self-intersection or adjacent-blade contact at 41 sections (the eleven design nodes plus quarter intervals) | Discrete 401-point geometry check including edge circles; not a continuous-span certificate or a 3-D CAD check |
| Metal angle, camber | Absolute metal angle <80 deg, camber <=70 deg | Existing correlation/angle-relation admission rules |
| Thickness, solidity | t/c 0.02-0.12, solidity 0.3-3 | Existing cascade-data admission ranges; do not imply whole-compressor validation |
| Axial chord projection | chord cos(stagger)/row width 0.5-1.5 | Geometry consistency tolerance; constructed MCA stagger is shared with simulation |
| Clearance and seals | Clearance <5% span; Egli seal condition and axial fit | Existing correlation/model restrictions; not validated clearance sensitivity for every family |
| Gas | cp=1004.5, R=287.05 J/(kg K), dry-air Sutherland viscosity | Calorically perfect air; custom cp/R are rejected because the transport model is air-specific |
| Temperature | Static T >=200 K and absolute total T0 <=400 K everywhere in a successful solution | **Provisional project restriction**, not a measured or NASA-certified accuracy bound; excludes hotter applications until gas-model error is qualified or variable properties are implemented |
| Inlet | Uniform P0, T0 and swirl angle, task-owned inlet blockage 0-0.2 | Current public contract; arbitrary radial inlet profiles only exist in the low-level solver |
| Speed, mass flow | Positive prescribed actual rpm and kg/s | No experimentally established universal speed range; corrected quantities and back-pressure solution are future work |
| Relative Mach and chord Reynolds | Reported at every row; finite positive Re required by the physical state and transport model | **Validated ranges remain unspecified**. Aungier's Re correction changes branch at 2.5e5; this is not a validated-domain boundary |
| Mixing | Off in the frozen profile; optional Gallimore research switch recorded explicitly | Experimental; global conservation checks apply when enabled; coarse radial mixing solutions can fail them |

Constant cp is an approximation; molecular excitation changes heat capacities
with temperature. Sutherland viscosity is temperature dependent even when cp is
held fixed. Background: [NASA calorically imperfect gas](https://www.grc.nasa.gov/www/BGH/realspec.html)
and [NASA viscosity](https://www.grc.nasa.gov/www/k-12/airplane/viscosity.html).
Neither reference supplies the project's 200-400 K acceptance boundary.

No validated Mach/Reynolds, speed, loading or stage-count region has yet been
earned for v16. Consequently every successful point carries
`empirical_validation="pending"`, `score_eligible=false` and an empty validated
Mach/Reynolds range. This is an explicit gap, not an implicit unrestricted claim.

The [Phase 3 empirical audit](phase3_validation.md) tested measured-state row
closures across relative Mach 0.444-1.501 and Re 4.72e5-1.67e6. These are observed
test ranges, not a validated rectangular domain: no sufficiently supported
joint core cell passed both deviation and loss screens. In that frozen v8 audit, original annuli were excluded by row-contour admission.
V9 retains their interior wall controls; see the [matched geometry and convergence
comparison](phase3_geometry_convergence_v9.md). Other admission restrictions and
the failed empirical closure/coverage/profile/design-response gates remain.

V7 provisionally admits only monotone or single-extremum span distributions of
metal angles, chord, thickness and MCA parameters. More than one trend reversal
is explicitly unsupported; differences below 1e-10 times max(1, field magnitude)
are ignored as roundoff. This is a conservative scope restriction, not an
experimentally calibrated criterion or a claim of physical impossibility.
Derived geometry is reconstructed at 41 span positions, rather than interpolating
nonlinear derived quantities. Continuous-span certification and broader geometry
qualification still belong to generated-design validation.

Part-span dampers, bleed, cooling, variable vane schedules, arbitrary controlled
diffusion sections, 3-D lean/sweep effects and time-dependent rotating stall/surge
are outside the represented scope. Historical experimental cases containing an
omitted mechanism are research diagnostics, not release evidence for that feature.

## What success now checks

- Every required row, quasi-normal, endwall and outer solve must converge.
  Outer convergence covers stream-surface position, Wm, swirl, enthalpy,
  pressure, entropy, endwall coupling and the optional mixing coefficient.
- Residuals, tolerances, iteration counts and cold/homotopy attempts are retained.
  A homotopy result is usable only after the full loss scale reaches one.
- Wm, pressure, density, static/total temperature and sound speed must be finite
  and positive; stream surfaces must be ordered. Row angles must be forward,
  losses nonnegative, and wake blockage in [0,1).
- Station mass error must be <=1e-9 relative. Maximum absolute stream-tube mass
  fraction error must be <=max(10*outer_tolerance, 1e-8).
- Without mixing, local Euler/duct/stator enthalpy residual divided by inlet
  total enthalpy must be <=1e-10. Integrated energy/work error uses
  max(20*outer_tolerance, 1e-8); it includes the remaining stream-tube placement
  error and also applies with mixing.
- In ducts, angular momentum is checked per stream surface without mixing
  (relative tolerance 1e-10), and as a mass-weighted flux with or without mixing
  (max(20*outer_tolerance, 1e-8)). Blade rows may exchange torque.
- Without mixing, streamwise entropy decrease below -1e-8 J/(kg K) is rejected.
  With mixing, only integrated entropy production is constrained, at
  -max(20*outer_tolerance*cp, 1e-8) J/(kg K). Local entropy may decrease during
  radial redistribution.

These tolerances test numerical consistency of the implemented equations.
They do not quantify model error or prescribe a resolvable design improvement.
Coupled Anderson repositioning is the default in v7, with up to 40 secant steps
and deterministic Novak fallback. The original undamped residuals must still
pass. The independent conical source-flow tests demonstrate second-order radial
accuracy for that analytic case; full-model resolution evidence is kept in
separate synthetic campaigns, including failures.

## Limits, diagnostics and failure semantics

The existing loss cap (0.5), endwall blockage clip (0-0.5) and meridional-Mach
denominator safeguard (Mm^2 capped at 0.9) remain explicit model/numerical
operations. Final-state activations are reported by row or station. They have
not been experimentally qualified as acceptable design-feedback conditions.
Correlation branches are not automatically classified as physical boundaries.

Aungier's loss smoothing remains unmodified: its endpoint extrapolation can
produce a negative value. The solver rejects such a closure with
`invalid_physical_state`; it does not silently floor it to zero. A positive,
conservative replacement would require its own evidence and version boundary.

Failure evidence is retained in `raw_simulation_output.failure`, including
component, row/station, iterations and residual where available.
`quasi_normal_capacity` describes the solver's representable capacity boundary;
it is not proof of whole-machine choking. `numerical_failure` is not established
physical infeasibility. `outside_model_scope` identifies the temperature envelope.
V8 evaluates every requested point, retains partial outcomes, and separates
physical upper-bound evidence from unresolved iterative capacity and numerical
failures. The aggregate evaluation still fails if any requested point fails;
partial metrics never earn a score. See [Phase 2](phase2_offdesign.md) for path
audits, model-limit indicators and the remaining map coverage gate.

## Reproducibility

Use Python 3.12.10 and `pip install -c constraints-validation.txt -e ".[dev]"`.
The numerical stack and test dependencies are pinned; sm-core remains pinned to
its released v0.8.0 tag. Exact determinism is tested within this environment and
across fresh processes. Portable regression comparisons use relative tolerance
1e-7; a new Linux/Windows CI run is still needed to establish cross-platform
agreement for this change.

Changing package sources after import invalidates evaluation; start a fresh
process so on-disk fingerprints cannot describe stale imported code.
Every evaluated simulation records normalized inputs, effective physics options
(including the mixing switch), source-file hashes and runtime dependency versions.
Campaigns additionally archive the working sources, source-data hashes, git
commit/dirty patch, selection and outputs. New runs use exclusive files under
`validation/campaigns/`. Older result directories and the pre-change v5 snapshot
remain unchanged. Full-model synthetic verification is reproducible with
`python validation/verify_phase01.py`.

The [v7 refinement report](phase1_refinement.md) records successful 1/2/4/8/16
duct refinement, comparisons with Novak and the remaining limits of numerical
uncertainty estimates. Passing these checks does not open the score.

V10 adds wall-layer subintervals and safeguarded coupled rollback. The
[matched v10 comparison](phase3_convergence_v10.md) separates numerical coverage,
wall-resolution sensitivity and experimental accuracy. No empirical gate is
automatically opened by a recovered numerical solution.

V11 uses direct three-point curvature and B*=4 base damping, with independent
geometric and modal stability tests. Original polyline corners are retained;
their classical point curvature is undefined and their resolved values can
depend on axial spacing. The [v11 report](phase3_curvature_v11.md) keeps this
limitation separate from smooth-curve accuracy and from numerical convergence.

V12 applies wall substeps to ducts and preconditions the coupled position update.
Failed production fine-grid starts can use checked coarse-grid continuation,
with every attempt and its cost reported. The recovered Stage 35 4/8 grids and
reading 3979 are documented in [the v12 report](phase3_iteration_v12.md). Wall
substep sensitivity, original corners, empirical error and design ranking still
need qualification; convergence recovery alone does not establish a trusted
Mach/Reynolds operating envelope.

V15 inverts the NASA Lewis equivalent-camber rule for MCA rows; its scalar
closure is unique for positive meridional speeds/radii and 0<=m/sqrt(sigma)<1,
with metal/setting angles inside (-90,90) degrees. This mathematical domain is
not an experimentally qualified operating envelope. The retained Aungier
incidence slope is a hybrid off-design extension. See the [v15 report](phase3_family_v15.md)
for the unresolved family response and training-label limitations.

V16 evaluates the MCA meanline at the requested geometric locations and
removes sampling quantization from small geometry changes. The frozen
comparison still finds the wrong efficiency direction for both NASA Stage
35–38 aspect-ratio pairs. Separate passage experiments identify failures in
transonic pressure recovery, loss and blockage. See the
[v16 geometry comparison](phase3_geometry_v16.md) and the
[NASA back-pressure passage study](phase3_backpressure_passage_v16.md).
