# Compressor validation status

The compressor environment can run a complete one- or two-stage axial design
through the public `make_env("turbomachinery_throughflow")` API with 11 radial
solution points (10 streamtubes). It is not yet an experimentally validated
compressor design model and every design scores zero.

Run the reproducible comparison from the repository root:

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
| one-stage candidate physics | 1.4294 | 1.3000 | 0.9550 | 2.7e-10 | 10 |
| two-stage adapter regression | 1.6809 | 1.6900 | 1.0090 | 1.9e-9 | 5 |
| two-stage candidate physics | 2.0314 | 1.6900 | 0.9437 | 7.2e-10 | 10 |

Every run converges: no row's Vm or P0 profile changes by more than 1e-6
(relative) in the last pass.

The regression path is useful only for adapter equivalence. Its efficiency
above one is physically impossible and demonstrates why zero loss cannot be a
validation model. The candidate path applies the preliminary Lieblein
diffusion loss and Carter deviation. It converges, but its pressure-ratio
errors are 9.95% for one stage and 20.2% for the repeated two-stage case.
Incidence loss is absent. These facts block scoring.

On `…_v3` (fork `v1.4.4-sm.1`) the two-stage candidate stopped at a massflow
residual of 2.26e-6 and was rejected: the solver's row solves were only
accurate to about 1e-6, and its loop stopped on that noise. `v1.4.4-sm.2`
fixes both.

On NASA 23c2b0bf (simulator `…_v2`) the candidate predicted zero stator loss,
because the upstream loss divided the stator swirl change by rotor speed, and
the environment had to replace NASA's Carter class, which returned zero
deviation, with its own adapter. The fork fixes both (see its
`MODIFICATIONS.md`); the stator now carries a mean loss coefficient of about
0.055 in the one-stage case.

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

