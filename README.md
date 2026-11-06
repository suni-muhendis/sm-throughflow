# sm-throughflow

Experimental streamline-curvature solver for axial compressors. Evaluate a
prescribed blade and annulus design at specified shaft speeds and mass flows.
The solver uses Aungier-based blade-row, endwall, leakage and throat
correlations and integrates with [sm-core](https://github.com/suni-muhendis/sm-core).

**Research software.** The current solver is
`slc_aungier_experimental_v16`. It is suitable for solver development,
conservation checks and research comparisons. An experimentally qualified
operating envelope is still open. The score is disabled and returns zero
for every design.

## Quick start

Use Python 3.12 and Git. From the repository root, create a virtual
environment.

```sh
python -m venv .venv
```

Activate it with `source .venv/bin/activate` on Linux or macOS, or
`.\.venv\Scripts\Activate.ps1` in Windows PowerShell. Install the checkout
with the validation dependency constraints and run the synthetic example.

```sh
python -m pip install -c constraints-validation.txt -e ".[dev]"
python scripts/run_throughflow.py --stages 1
python -m pytest tests -q
```

The example prints the solver status and performance metrics. Use
`--stages 3` for a repeating-stage example or `--json` to export the
complete input. The examples are synthetic solver checks. The
installation resolves `sm-core` from its pinned Git tag.

### Python API

From the checkout, the same example can be evaluated through the
environment entry point.

```python
from scripts.run_throughflow import build_case
from sm_core import make_env

design, task = build_case(stages=1)
env = make_env("turbomachinery_throughflow")
result = env.evaluate("example-task", task, "one-stage", design)

if result.status == "success":
    print(result.metrics["pressure_ratio_total"])
else:
    print(result.status, result.error_message)
```

## What it models

- **Machine** — A single-shaft, axisymmetric axial compressor with one or
  more rotor–stator stages and optional inlet guide vanes. The design
  specifies a piecewise-linear hub and shroud, blade-row positions,
  clearances or seals, and eleven hub-to-shroud sections. Available
  thickness families include NACA 65, C.4, DCA and MCA.
- **Operating point** — The task supplies actual shaft speed and mass
  flow, uniform inlet total conditions and swirl, and numerical settings.
  The default gas is calorically perfect dry air with air-specific
  transport. The production path evaluates specified points rather than
  solving a compressor map from a prescribed outlet pressure.
- **Results** — The environment reports pressure ratio, efficiency, power,
  blockage and model-limit indicators, with spanwise fields and convergence
  and conservation diagnostics in the raw result. A successful evaluation
  establishes numerical convergence and the implemented balance checks.

The JSON schemas are `throughflow_design_v2` and `throughflow_task_v2`.
The environment name is `turbomachinery_throughflow`. See the
[input and result contract](docs/throughflow_contract_v2.md).

## Current limitations

| Area | What the evidence supports |
| --- | --- |
| Experimental accuracy | No qualified Mach, Reynolds, speed, loading or stage-count envelope. Schema bounds describe implementation scope. |
| Design ranking | At the NASA Stage 35–38 design-speed anchors, v16 predicts the wrong direction for both low- to high-aspect-ratio efficiency comparisons. Performance values are unsuitable as trusted design-ranking labels. |
| Off-design | Prescribed-point analysis with separate numerical failures, unresolved capacity limits and model-scope outcomes. Limit indicators are model estimates. Measured stall, surge and the complete stable operating range remain unqualified. |
| Transonic flow | The production closure approximates shock loss and wake blockage. It lacks resolved shock-induced separation and reattachment. The separate pressure-matched passage research fails the joint NASA pressure, loss and blockage comparison. |
| Geometry and physics | Axisymmetric, section-based geometry and empirical closures. Arbitrary 3D lean and sweep, part-span dampers, bleed, cooling, variable-vane schedules, turbines and unsteady stall/surge dynamics are outside scope. |

The [frozen v16 comparison](docs/phase3_geometry_v16.md) retained 75
converged jobs out of 108, including numerical refinements and repeats.
This is a mixed regression cohort with measured, projected and numerical
cases. See the [scope and failure semantics](docs/throughflow_domain.md)
and the [physical acceptance criteria](docs/compressor_validation.md).

## Documentation and validation

| Topic | Guide |
| --- | --- |
| Solver and correlations | [Streamline-curvature solver](docs/throughflow_solver.md) · [Correlation sources](docs/compressor_correlations.md) · [Blade rows](docs/compressor_row_model.md) · [Endwall layers](docs/endwall_boundary_layer.md) |
| Validation inputs and commands | [Validation cases and workflows](validation/README.md) · [Off-design checks](docs/phase2_offdesign.md) |
| Current transonic evidence | [Rotor and stator loss attribution](docs/phase3_stage_loss_attribution_v16.md) · [NASA casing pressure](docs/phase3_rotor_casing_pressure_v16.md) · [Back-pressure passage experiment](docs/phase3_backpressure_passage_v16.md) |
| Version history | [Changelog](CHANGELOG.md) |

Validation case folders include source-report and page references. Raw
campaign snapshots and scratch outputs are local artifacts. Historical
reports may refer to their local campaign directories.

## License

Source code is available under the [Apache License 2.0](LICENSE). See
[NOTICE](NOTICE) for attribution and third-party dependencies. Validation
data provenance is recorded alongside the individual cases.
