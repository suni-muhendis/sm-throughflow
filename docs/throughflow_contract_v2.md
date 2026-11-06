# Throughflow contract v2 and simulator v16

Version 2 of the design and task contracts runs axial compressors on the
package's own streamline-curvature solver (`sm_throughflow.solver`) with
Aungier's blade-row, leakage and end-wall models. The simulator is
`slc_aungier_experimental_v16`, the active simulator of the environment.
Version 1 of the contracts ran on NASA turbo-design and was removed with that
simulator; its results are never pooled with these.

The score stays disabled (`throughflow_score_disabled_v1`): every design
scores zero until the physics passes the validation gate in
[compressor_validation.md](compressor_validation.md).

## Design (`throughflow_design_v2`), owned by the design

```json
{
  "schema_version": "throughflow_design_v2",
  "machine_type": "compressor",
  "flow_path": "axial",
  "passage": {"stations": [{"axial_m": 0.0, "hub_radius_m": 0.30, "shroud_radius_m": 0.50}, ...]},
  "rows": [ { ... one object per blade row, in axial order ... } ]
}
```

Each row:

| Field | Meaning |
|---|---|
| `row_id`, `stage_id` | Unique id; stage id (only inlet guide vanes, stators ahead of the first rotor, may omit it). Each stage has one rotor. |
| `row_type` | `rotor` or `stator`. |
| `leading_edge_axial_m`, `trailing_edge_axial_m` | Axial planes of the row's edges; rows may not touch, and all lie strictly inside the passage. |
| `blade_count` | Z. |
| `profile` | Thickness distribution: `naca65`, `c4`, `dca` (double circular arc) or `mca` (multiple circular arc). |
| `camberline` | `naca65` (a/c = 0.5), `circular_arc`, `parabolic_arc` or `multiple_circular_arc` (with, and only with, the `mca` profile); `max_camber_location` (a/c) applies to the parabolic arc only. |
| `edge_radius_to_chord` | Leading- and trailing-edge radius over chord; required for, and only for, `dca` and `mca`. |
| `transition_point`, `turning_rate_ratio`, `max_thickness_location` | Multiple circular arc only, eleven values each: the chordwise fraction where the meanline's two arcs meet (0.1 to 0.9), the ratio C1/C2 of the front arc's turning rate to the rear arc's (-0.5 to 3; 1 is a circular arc, 0 a straight front), and the chordwise fraction of maximum thickness (0.2 to 0.8). Crouse, NASA TN D-7345. |
| `metal_angle_in_deg`, `metal_angle_out_deg` | Eleven values hub to shroud (0, 0.1, ..., 1 of the span), degrees from the axial direction, **positive in the direction of rotation**: a rotor usually has negative angles, a stator positive inlet angles. Every section turns the flow the same way. |
| `chord_m`, `thickness_to_chord` | Eleven values: true chord and maximum thickness ratio. |
| `tip_clearance_m` | Rotors only, required. |
| `hub_clearance_m` or `shroud_seal` | Stators: exactly one, a cantilevered stator's hub gap or the labyrinth seal under a shroud band (`clearance_m`, `fin_count` 1 to 12, `fin_pitch_m`, `fin_thickness_m`). |

The inlet angle applies at the leading-edge plane, the exit angle at the
trailing-edge plane, chord and thickness between them; each stream surface
reads them at its own span fraction on those planes, and the solver projects
them onto the stream surface (Aungier 9-1 to 9-6). The simulator builds each
of the eleven sections from its profile and camberline (Aungier chapter 4)
and takes the throat opening, which sets the choke limit on incidence, from
the constructed cascade; for double- and multiple-circular-arc rows also the
expansion angle of the shock-loss model.

## Design rules (`drc.py`)

| Rule | Why |
|---|---|
| \|metal angle\| < 80 deg | Beyond this the cascade correlations and the throughflow angle relations break down. |
| camber <= 70 deg | The range of the cascade data behind the incidence, deviation and stall correlations. |
| 0.02 <= t_b/c <= 0.12 | The range of Johnsen and Bullock's thickness corrections (Aungier Figs. 6-3, 6-9). |
| 0.3 <= solidity <= 3 at every section | The range of the cascade data. |
| 0.5 <= chord cos(stagger) / (trailing edge - leading edge) <= 1.5 | The row's axial planes must match its blades. |
| clearance < 5% of blade height | Beyond the range of the clearance model. |
| seal clearance/fin pitch <= X2 - 1, fins fit under the row | The validity limit of Egli's model (6-94). |

## Task (`throughflow_task_v2`), owned by the task

| Field | Default | Meaning |
|---|---|---|
| `simulator_version` | `slc_aungier_experimental_v16` | The only value accepted by the current task contract. |
| `inlet` | | Absolute total pressure and temperature, absolute flow angle (deg, positive with rotation). |
| `operating_points` | | 1 to 12 named points, each a mass flow and a shaft speed. The first is the design point. |
| `gas` | dry air | Fixed cp = 1004.5 and R = 287.05 J/(kg K); other gases rejected by this profile. |
| `physics.physics_profile` | `axial_compressor_aungier_v2` | The frozen physics (below). |
| `physics.inlet_blockage` | 0.02 | End-wall blockage at the inlet (Aungier section 8.8). |
| `numerics` | 11 stream surfaces, `full` curvature, tolerance 1e-7, 400 iterations | Solver settings. |
| `numerics.duct_subdivisions` | 1 | 1 to 16 subdivisions per duct segment; blade rows stay single gaps. |
| `numerics.endwall_max_iterations` | 200 | 10 to 1000 residual-map evaluations per wall subinterval, including Jacobian probes; endwall residual tolerance remains 1e-8. |
| `numerics.endwall_subdivisions` | 8 | 1 to 32 wall integration subintervals per blade-row or duct gap; core-flow states remain at row edges. |
| `numerics.repositioning` | `anderson` | Coupled geometry/blockage acceleration, with deterministic Novak fallback; `novak` selects the original iteration. |
| `numerics.acceleration_depth` | 40 | 2-40 stored secant steps; task-owned. |
| `max_stages` | 20 | |

Profile `axial_compressor_aungier_v2` freezes: the row model of
[compressor_row_model.md](compressor_row_model.md) with K1 = 0.0073, the loss
limit 0.5 and spanwise smoothing, the arithmetic-mean shock loss, and the
end-wall boundary layers of [endwall_boundary_layer.md](endwall_boundary_layer.md).

## Simulation

Quasi-normals include passage endpoints, non-collinear duct wall vertices,
and every row edge. Collinear points are canonicalized before discretization.
Interior row wall vertices remain geometric controls: local annulus fraction is
interpolated between solved edge stations, and slope, curvature and arc length
include those controls. They are not internal blade-force or flow states. An
interior annulus minimum below both edge areas is explicitly unsupported; the
single-gap row cannot resolve its capacity. Duct refinement does not apply
blade work more than once. V11 computes curvature directly from local parametric
quadratics, including one-sided endpoint fits. It uses B*=4 for Novak's base
step, compatible with the high-frequency modes resolved by this stencil.
Novak's fallback still reduces B* toward one when the position error grows;
Anderson uses the fixed base map. All residual and balance tolerances remain
unchanged. Unconverged iterates do not establish a physical choke boundary.

## Results

Metrics of the design point (the other points prefixed with their name and a
dot): `pressure_ratio_total`, `temperature_ratio_total`,
`efficiency_polytropic`, `efficiency_isentropic` (from the mass-averaged total
enthalpy and entropy), `power_W`, `mass_flow_kg_s`, `shaft_speed_rpm`,
`stage_count`, `stream_surface_count`, `exit_blockage`, `max_blockage`,
`max_loss_coefficient`, `max_equivalent_diffusion`,
`max_relative_inlet_mach`, `min_stall_margin` (the smallest
W_RE / W_RE,stall - 1 over all rows and stream surfaces, Aungier 9-16 to
9-19; negative means a row is past his stall criterion) and
`solver_iterations`.

`raw_simulation_output.operating_points[*]` carries, per row, every quantity
of the row model on each stream surface (incidence, design and stall
incidences, deviation, every loss part, D_eq, wake blockage, solidity,
stagger, stall margin), per stage the total pressure and temperature ratios
and polytropic efficiency, the blockage on every quasi-normal and the exit
span profiles.

## Reference case

`scripts/run_throughflow.py --stages N` builds a repeating-stage subsonic
compressor with free-vortex blading (optionally with an inlet guide vane); the
tests retain separate v5 and v6 characterizations of its one-stage version.

## v6 reliability contract

The physics profile includes local Sutherland air viscosity in blade Reynolds
corrections and endwall layers. See [the scope specification](throughflow_domain.md)
for the provisional 200-400 K envelope and the distinction between admitted
and experimentally validated conditions.

A stator must belong to its preceding rotor; IGVs have no stage ID. DRC uses
the constructed MCA stagger and checks sampled blade surfaces for intersection.
Successful raw output includes the effective-input and source fingerprints,
row/station mapping, nested residuals, balance verification, local Reynolds
numbers and limiter flags. Failed simulation output retains structured evidence
under `failure`; this is compatible with the existing sm-core status schema.
A solver-capacity failure is not automatically a measured physical choke point.

## v7 iteration and geometry admission

V7 changes the numerical path and admission rules; the empirical physics profile
remains v2. Every nonconverged or failed accelerated attempt is recorded, and the
original Novak iteration is tried deterministically before rejecting the attempt.
Actual undamped residuals, sub-solve checks and final physical verification remain
mandatory. See [the v7 verification report](phase1_refinement.md).

Admission constructs 41 span sections from the eleven piecewise-linear design
inputs, including intermediate projected-chord and surface intersection checks.
Monotone or single-extremum span distributions are the provisional v7 scope;
multiple trend reversals are reported as unsupported. These are numerical
admission restrictions, not calibrated physical impossibility criteria.

## v8 off-design outcome evidence

The sm-core status schema remains unchanged. Failed evaluations retain a
`failure.classification` and `physical_limit_established` alongside the detailed
kind, location, residuals and attempts. A multi-point evaluation attempts all
points; any failure still makes the aggregate evaluation invalid. Partial results
remain in `raw_simulation_output.operating_points`; they do not earn a score.

Successful points report independent inlet-duct sonic capacity, converged
throat-capacity/stall correlation indicators, and total effort across restart,
cold, accelerated/original and homotopy attempts. Model indicators are not surge
predictions. The new `sm_throughflow.offdesign` API compares cold and both
continuation directions under a recorded caller-owned policy. Restart geometry
must match the design, task and speed. Divergent roots are retained and flagged,
never selected by performance. See [Phase 2](phase2_offdesign.md).

## V10 wall integration and coupled safeguards

`numerics.endwall_subdivisions` is task-owned, integer 1-32, default 8. It
subdivides the boundary-layer integration inside each blade-row or duct gap, using
interpolated edge states; it does not add core-flow states or apply blade work
again. `endwall_max_iterations` remains 10-1000 (default 200) and now bounds map
evaluations per wall subinterval, including numerical Jacobian evaluations.
Each interval reports substep index/count, residual, tolerance, method and effort.

The wall solve verifies all conserved-state fixed-point components as well as
theta11, H1 and force defect; an optimizer success flag alone is insufficient.
Accelerated coupled trials with failed sub-solves or excessive residual growth
are rolled back, including wall corrections, mixing state and row caches. Up to
eight smaller ordinary steps may be tried; each consumes the original outer
iteration budget. V11 retains rejection traces on returned attempts and failures
inside the coupled-map safeguard, including experimental output and total effort.
V12 also preserves the trace when construction of an acceleration step fails. Endwall
failures identify the subinterval index and count. No failure is
converted into a physical choke label by this policy.

## V12 iteration and fine-grid initialization

Anderson iteration uses a half-step elliptic position preconditioner and fits
stored raw residual differences; final convergence still uses undamped residuals.
Novak remains the fallback method. If a requested grid with more than one duct
subdivision fails numerically, checked full-model solutions on grids 1, 2, 4, ...
may initialize its retry. Each grid uses the original per-attempt budget. All
attempts report `duct_subdivisions` and `grid_role`; `effort` includes the original
failure, seed grids and final retry. Independent physical inlet-capacity failures
do not invoke this policy. See [v12 evidence](phase3_iteration_v12.md).
