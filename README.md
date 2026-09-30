# sm-throughflow

An experimental turbomachinery throughflow environment for machine-generated
engineering designs. It takes a multi-stage axial compressor or turbine design
as JSON, checks it, and solves it with NASA turbo-design, through the
[Suni Muhendis fork](https://github.com/suni-muhendis/turbo-design). It is one environment of
the Suni Muhendis benchmark and plugs into
[sm-core](https://github.com/suni-muhendis/sm-core).

```
design (JSON) → schema → design rules → simulation → score
```

**Status: experimental.** Every design scores zero
(`throughflow_score_disabled_v1`) until the physics profiles pass physical
validation; see [docs/compressor_validation.md](docs/compressor_validation.md).

- **Machines:** axial compressors and turbines, one or more stages.
- **Design:** passage stations and blade rows, with eleven hub-to-shroud values
  (`0.0, 0.1, …, 1.0`) for inlet metal, exit metal and stagger angle.
- **Task:** operating point, numerical resolution and physics profile (loss and
  deviation models). The model designs the machine; the task owns the referee.
- **Versions:** simulator `nasa_turbo_design_experimental_v3` on
  `suni-muhendis/turbo-design@v1.4.4-sm.1`; score `throughflow_score_disabled_v1`.

## Install

```bash
pip install "sm-throughflow @ git+https://github.com/suni-muhendis/sm-throughflow.git@<tag>"
sm-throughflow-setup-assets
```

This pulls in `sm-core` and `turbo-design` at pinned tags. The setup
command downloads the Kacker-Okapuu and Ainley-Mathieson chart data from the
same pinned revision and verifies their SHA-256 hashes; only those two loss
models need it. On Windows, installing `turbo-design` from git needs long
paths (`git config --global core.longpaths true`).

## Use

```python
from sm_core import make_env

env = make_env("turbomachinery_throughflow")
result = env.evaluate("task", task, "design", design)
result.status, result.metrics["pressure_ratio_total"]
```

`scripts/run_throughflow.py` and `scripts/run_throughflow_compressor.py` build
complete turbine and compressor cases. [docs/turbomachinery_throughflow.md](docs/turbomachinery_throughflow.md)
describes the contract and the physics profiles.

## History

This package was extracted, with its git history, from the private research
repository where it lived as
`sunimuhendis.environments.turbomachinery_throughflow`.

## License

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE). NASA
turbo-design is a dependency under the NASA Open Source Agreement 1.3 and is
not part of this package.
