# sm-throughflow

An experimental turbomachinery throughflow environment for machine-generated
engineering designs. It takes a multi-stage axial compressor design as JSON,
checks it, and solves it with its own streamline-curvature solver and
Aungier's empirical blade-row, leakage, end-wall and blade-throat models. It
is one environment of the Suni Muhendis benchmark and plugs into
[sm-core](https://github.com/suni-muhendis/sm-core).

```
design (JSON) → schema → design rules → simulation → score
```

**Status: experimental.** Every design scores zero
(`throughflow_score_disabled_v1`) until the physics passes validation; see
[docs/compressor_validation.md](docs/compressor_validation.md).

- **Machines:** axial compressors, one or more stages, with or without inlet
  guide vanes. Turbines will follow on the same solver.
- **Design:** passage stations and blade rows: edge planes, blade count,
  profile family (NACA 65, C.4, double circular arc), camberline, clearance or
  shroud seal, and eleven hub-to-shroud values (`0.0, 0.1, …, 1.0`) of metal
  angles, chord and thickness.
- **Task:** inlet conditions, operating points, gas, numerics and the physics
  profile. The model designs the machine; the task owns the referee.
- **Versions:** simulator `slc_aungier_experimental_v5`, contracts
  `throughflow_design_v2` / `throughflow_task_v2`
  ([docs/throughflow_contract_v2.md](docs/throughflow_contract_v2.md)), score
  `throughflow_score_disabled_v1`.

## Install

```bash
pip install "sm-throughflow @ git+https://github.com/suni-muhendis/sm-throughflow.git@<tag>"
```

This pulls in `sm-core` at its pinned tag, numpy and scipy.

## Use

```python
from sm_core import make_env

env = make_env("turbomachinery_throughflow")
result = env.evaluate("task", task, "design", design)
result.status, result.metrics["pressure_ratio_total"]
```

`scripts/run_throughflow.py` builds a complete repeating-stage compressor case.

## Documentation

- [docs/throughflow_solver.md](docs/throughflow_solver.md): the solver and its verification.
- [docs/compressor_correlations.md](docs/compressor_correlations.md): Aungier's correlations, their sources and the misprints found.
- [docs/compressor_row_model.md](docs/compressor_row_model.md), [docs/endwall_boundary_layer.md](docs/endwall_boundary_layer.md): how they are assembled.
- [docs/throughflow_contract_v2.md](docs/throughflow_contract_v2.md): design, task and results.
- [validation/README.md](validation/README.md): transcribed test cases for validation.

## History

This package was extracted, with its git history, from the private research
repository where it lived as
`sunimuhendis.environments.turbomachinery_throughflow`. Its first simulators
ran on a fork of NASA turbo-design; they were removed once the package's own
solver replaced them, and remain in the git history.

## License

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
