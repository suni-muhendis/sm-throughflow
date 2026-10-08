# Throughflow contract v2 and simulator v5

Version 2 of the design and task contracts runs axial compressors on the
package's own streamline-curvature solver (`sm_throughflow.solver`) with
Aungier's blade-row, leakage and end-wall models. The simulator is
`slc_aungier_experimental_v5`, the only simulator of the environment.
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
| `profile` | Thickness distribution: `naca65`, `c4` or `dca` (double circular arc). |
| `camberline` | `naca65` (a/c = 0.5), `circular_arc` or `parabolic_arc`; `max_camber_location` (a/c) applies to the parabolic arc only. |
| `edge_radius_to_chord` | Leading- and trailing-edge radius over chord; required for, and only for, `dca`. |
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
the constructed cascade.

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
| `simulator_version` | `slc_aungier_experimental_v5` | The only value accepted. |
| `inlet` | | Absolute total pressure and temperature, absolute flow angle (deg, positive with rotation). |
| `operating_points` | | 1 to 12 named points, each a mass flow and a shaft speed. The first is the design point. |
| `gas` | air | Perfect gas: cp and R. |
| `physics.physics_profile` | `axial_compressor_aungier_v1` | The frozen physics (below). |
| `physics.inlet_blockage` | 0.02 | End-wall blockage at the inlet (Aungier section 8.8). |
| `numerics` | 11 stream surfaces, `full` curvature, tolerance 1e-7, 400 iterations | Solver settings. |
| `max_stages` | 20 | |

Profile `axial_compressor_aungier_v1` freezes: the row model of
[compressor_row_model.md](compressor_row_model.md) with K1 = 0.0073, the loss
limit 0.5 and spanwise smoothing, the arithmetic-mean shock loss, and the
end-wall boundary layers of [endwall_boundary_layer.md](endwall_boundary_layer.md).

## Simulation

Quasi-normals are radial lines at the passage inlet, at every row's leading
and trailing edge and at the passage outlet. Every operating point is solved
independently with Novak's damping at B* = 16, the top of the 8 to 16 range
Aungier gives (section 12.4); (7-59) still lowers B* if the stream surfaces
start to move more. On a three-stage case B* = 8, 16 and 32 give the same
pressure ratio to seven digits in 121, 65 and 35 iterations. A point that does
not converge, or a passage that chokes, fails the simulation.

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
tests pin simulator v5 to its one-stage version.
