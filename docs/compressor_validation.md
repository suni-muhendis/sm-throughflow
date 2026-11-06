# Compressor validation status

The current simulator is `slc_aungier_experimental_v16`. Its matched
regression campaign retains 75 of 108 converged jobs, including the
Stage 53 design-speed point and the Stage 35 90% speed point. The
cohort includes repeats, grid changes and research geometries. Both
Stage 35–38 aspect-ratio comparisons still give the wrong efficiency
direction. See the [v16 comparison](phase3_geometry_v16.md).

The [NASA back-pressure passage study](phase3_backpressure_passage_v16.md)
documents the separate research model's failure to match pressure recovery,
loss and blockage together. The [Phase 3 empirical audit](phase3_validation.md)
retains the v8 findings and the acceptance protocol. No empirical operating
envelope is qualified. The score returns zero for every design.

> **Historical sections.** The comparison and findings below were made with
> the NASA turbo-design simulators (`nasa_turbo_design_experimental_v3`/`v4`),
> which have since been removed from the package; the scripts they cite are in
> the git history. They are kept because they explain why the package has its
> own solver. The acceptance gate at the end applies to the current simulator,
> and the open test cases for it are in `validation/`.

The compressor environment can run a complete one- or two-stage axial design
through the public `make_env("turbomachinery_throughflow")` API with 11 radial
solution points (10 streamtubes). It is not yet an experimentally validated
compressor design model and every design scores zero.

In the historical v4 checkout, the comparison used this command:

```bash
python scripts/run_throughflow_compressor_benchmark.py
```

The reference case is Mattingly example 9.1 as transcribed in NASA
`turbo-design`, run on the pinned fork `suni-muhendis/turbo-design@v1.4.4-sm.2`
(simulator `nasa_turbo_design_experimental_v4`). The published example specifies one
stage, a total-pressure ratio of 1.3, the annulus, operating point, and exit
metal angles. The second stage below is a repeated-stage integration exercise,
not a published benchmark.

| Case | Achieved PR | Target PR | Polytropic efficiency | Massflow residual | Passes |
|---|---:|---:|---:|---:|---:|
| one-stage adapter regression | 1.3172 | 1.3000 | 1.0052 | 5.3e-10 | 4 |
| one-stage candidate physics | fails | 1.3000 | — | — | — |
| two-stage adapter regression | 1.6809 | 1.6900 | 1.0090 | 1.9e-9 | 5 |
| two-stage candidate physics | fails | 1.6900 | — | — | — |

The regression runs converge: no row's Vm or P0 profile changes by more than
1e-6 (relative) in the last pass. They are useful only for adapter
equivalence.

The candidate runs no longer solve, and the reasons are the substance of this
document:

1. **The candidate case is ill-posed.** Mattingly 9.1 gives exit angles but no
   inlet metal angles, and the case used 0 deg, so the rows met the flow at
   30-55 deg of incidence and the stators were drawn with camber of the wrong
   sign. Before `v1.4.4-sm.2` this was hidden because turbo-design computed a
   stator's deviation but released the flow at the metal angle. Once the
   deviation reaches the flow, the stators choke.
2. **A zero-incidence redesign exposes an energy error in turbo-design.** With
   inlet metal angles set to the flow and exit angles compensated for Carter
   deviation, the one-stage candidate solves with a polytropic efficiency of
   1.002 despite its losses. Even at zero loss the solver reports 1.005.
   Measured on NASA's own Mattingly 9.1 example, unmodified, on upstream
   23c2b0bf, upstream 1.4.4 and the fork alike, the stator raises the
   mass-averaged T0 by 0.62 K (2.6% of the stage's rise). At 11 streamlines
   the rotor exit T0 departs from the Euler work of the solver's own velocity
   triangles by up to 3.6 K, in a saw-tooth from one streamline to the next.
3. **The cause is the closure of the radial-equilibrium ODE.** turbo-design
   integrates P0, T0 and Vm together from mid-span, taking dT0/dr and dP0/dr
   from the previous pass's static profiles. The standard streamline-curvature
   method carries rothalpy and entropy along the stream surfaces and solves
   the normal-momentum equation for Vm only: L. H. Smith (1966), eqs. 52-60;
   Dixon and Hall, eq. 6.6a; Aungier (2003), eqs. 7-10, 7-11 and 7-40 to
   7-49. turbo-design's own paper assumes rothalpy is conserved in every row.

This environment therefore moves to its own streamline-curvature solver. The
turbo-design path stays as a cross-check, and its two candidate-compressor
tests are expected failures.

On NASA 23c2b0bf (simulator `…_v2`) the candidate predicted zero stator loss,
because the upstream loss divided the stator swirl change by rotor speed, and
the environment had to replace NASA's Carter class, which returned zero
deviation, with its own adapter. The fork fixes both (see its
`MODIFICATIONS.md`); on `…_v3` the one-stage stator carried a mean loss
coefficient of about 0.055.

## EEE high-pressure compressor audit

NASA CR-165558 describes a 10-stage EEE high-pressure compressor with a cruise
design pressure ratio of 22.6, corrected airflow of 53.5 kg/s, adiabatic
efficiency goal of 86.1%, and polytropic efficiency of 90.6%:
<https://ntrs.nasa.gov/citations/19850002690>.

NASA's current reconstructed EEE example is useful source material, but it is
not a ready validation case. The example itself says that the reconstructed
geometry may differ from the original hardware and that CFD matching remains
future work:
<https://github.com/nasa/turbo-design/tree/main/examples/EEE-HPC>.

At NASA 23c2b0bf, the example passes 54.4 kg/s to the solver even though
the report quantity is corrected flow. With the workbook mean inlet state
(59.48 kPa, 304.76 K), 53.5 kg/s corrected corresponds to approximately
30.54 kg/s physical flow using the standard corrected-flow definition. The
unmodified example stops at the IGV because the requested flow exceeds its
choked capacity. Re-running at 30.7 kg/s clears that check but the radial-
equilibrium integration fails at rotor 2. The reconstructed EEE case therefore
stays an audited future benchmark rather than a passing test fixture.

## Acceptance gate for physical validation

The plan for meeting it, with consistency of the error across designs as the
criterion, is in [validation_plan.md](validation_plan.md).

A compressor physics profile can be scored only after it meets all of these
conditions:

1. A published geometry and operating point run without fixed report-derived
   row losses or deviations.
2. Overall pressure ratio and efficiency errors are reported against measured
   or independently calculated values.
3. Spanwise quantities are compared at the same radial stations where data are
   available.
4. Incidence, profile, secondary, endwall, clearance, Reynolds, and compressible
   loss effects are either modelled or declared outside the correlation range.
5. Multi-stage and 10-streamtube convergence tolerances are enforced by the
   environment rather than inferred from a solver return code.

