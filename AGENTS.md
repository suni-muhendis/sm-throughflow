# AGENTS.md

Guidance for AI coding agents (Claude Code, Codex, and others) working in this
repository.

## What this is

`sm-throughflow` (import `sm_throughflow`) is the experimental turbomachinery
throughflow environment of the Suni Muhendis benchmark. It implements the
`sm-core` contract (schema, design-rule check, simulator, score) and registers
itself as `turbomachinery_throughflow` in the `sm_core.environments`
entry-point group. Two simulators live side by side:

- `slc_aungier_experimental_v5` (v2 contracts, axial compressors): the
  package's own streamline-curvature solver (`sm_throughflow.solver`) with
  Aungier's (2003) cascade, leakage and end-wall models
  (`sm_throughflow.correlations`). See `docs/throughflow_contract_v2.md`.
- `nasa_turbo_design_experimental_v4` (v1 contracts, compressors and
  turbines): the Suni Muhendis fork of NASA `turbo-design`.

The environment hands each task to the simulator its `simulator_version`
names, so every result is stamped with the simulator that produced it.

The repository is **private** until the maintainers decide to publish the
environment. It is not yet part of SM-Bench.

## Commands

- Setup: `python3.12 -m venv .venv`, activate it,
  `python -m pip install -e ".[dev]"`, then `sm-throughflow-setup-assets`
  (only the Kacker-Okapuu and Ainley-Mathieson loss models need it). On
  Windows, installing `turbo-design` from git needs long paths:
  `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.longpaths GIT_CONFIG_VALUE_0=true pip install …`.
- Tests: `python -m pytest tests -q`.
- Demos: `python scripts/run_throughflow_v2.py --stages 3` (simulator v5),
  `python scripts/run_throughflow.py --stages 2`,
  `python scripts/run_throughflow_compressor.py --stages 2 --streamtubes 10`,
  `python scripts/run_throughflow_compressor_benchmark.py`,
  `python scripts/run_throughflow_resolution_study.py`.
- Wheel check: `python -m build` then `python scripts/check_wheel.py dist`.

## Rules

- **Versions are real.** `ThroughflowTaskV2.simulator_version` accepts only
  `SlcAungierSimulator.VERSION` and `ThroughflowTaskV1.simulator_version` only
  `NasaTurboDesignSimulator.VERSION`. Any change that can move a number (a
  solver or correlation change, a new `turbo-design` pin) needs a new
  simulator version and new reference values; results from different versions
  are never pooled. `tests/test_throughflow_v2.py` holds the v5 goldens.
- **Correlations are transcribed from their sources and tested against them.**
  Every function in `correlations/` cites its equation; the docs record each
  source, each misprint found and each choice the source leaves open.
- **The score is disabled.** `ExperimentalThroughflowScore` returns zero for
  every design until a physics profile passes the acceptance gate in
  `docs/compressor_validation.md`.
- **Determinism is a hard requirement.** Identical input gives identical
  output; tests assert it for multi-stage cases.
- **Third-party solvers are pinned, never vendored.** `turbo-design` is a
  dependency pinned to an exact revision; its source and chart data never
  enter this repository or the wheel.
- Prefer "score" over "reward" in new code and documentation.
- Consumers pin tags, never branches. Record user-visible changes in
  `CHANGELOG.md`.

## Layout

- `src/sm_throughflow/contracts.py`: v1 design, task and result contracts
  (Pydantic, strict, extra fields forbidden); `contracts_v2.py` the v2 ones,
  `drc_v2.py` their design rules and `simulator_v5.py` their simulator.
- `solver/`: the streamline-curvature solver (`throughflow.py`,
  `quasi_normal.py`, `geometry.py`), Aungier's row model (`aungier_row.py`)
  and end-wall boundary layers (`endwall.py`).
- `correlations/`: solver-independent cascade correlations (numpy only).
- `profiles.py`: versioned physics profiles; each fixes the loss and deviation
  models a task may select and the backend revision it was built against.
- `env.py`: `TurbomachineryThroughflowEnv`, schema, DRC and the task-owned
  simulation inputs. `simulator.py`: the adapter to `turbo-design`.
- `physics.py`: small adapters around the backend. `assets.py`: pinned,
  hash-verified chart data. `score.py`: the disabled score.
- `scripts/`: reference cases (OptTurb turbine, Mattingly 9.1 compressor) and
  studies; the tests build their cases from them.
- `docs/`: the environment contract and the compressor validation status.

## Ownership boundary

The design supplies passage geometry and blade geometry (v2: blade count,
edge planes, profile family, clearances or shroud seals and eleven-point
angle, chord and thickness distributions). The task owns the operating
points, numerical resolution, gas, physics profile, loss and deviation models
and any calibrated values. `prepare_simulation_inputs` validates both and hands them to
the simulator together, so a design can never choose the referee that scores it.
