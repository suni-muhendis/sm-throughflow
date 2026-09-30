# AGENTS.md

Guidance for AI coding agents (Claude Code, Codex, and others) working in this
repository.

## What this is

`sm-throughflow` (import `sm_throughflow`) is the experimental turbomachinery
throughflow environment of the Suni Muhendis benchmark. It implements the
`sm-core` contract (schema, design-rule check, simulator, score) on NASA
`turbo-design` and registers itself as `turbomachinery_throughflow` in the
`sm_core.environments` entry-point group.

The repository is **private** until the maintainers decide to publish the
environment. It is not yet part of SM-Bench.

## Commands

- Setup: `python3.12 -m venv .venv`, activate it,
  `python -m pip install -e ".[dev]"`, then `sm-throughflow-setup-assets`
  (only the Kacker-Okapuu and Ainley-Mathieson loss models need it). On
  Windows, installing `turbo-design` from git needs long paths:
  `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.longpaths GIT_CONFIG_VALUE_0=true pip install …`.
- Tests: `python -m pytest tests -q`.
- Demos: `python scripts/run_throughflow.py --stages 2`,
  `python scripts/run_throughflow_compressor.py --stages 2 --streamtubes 10`,
  `python scripts/run_throughflow_compressor_benchmark.py`,
  `python scripts/run_throughflow_resolution_study.py`.
- Wheel check: `python -m build` then `python scripts/check_wheel.py dist`.

## Rules

- **Versions are real.** The simulator is `NasaTurboDesignSimulator.VERSION`
  and it is also the only value `ThroughflowTaskV1.simulator_version` accepts.
  Any change that can move a number (including a new `turbo-design` pin) needs
  a new simulator version and new reference values; results from different
  versions are never pooled.
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

- `src/sm_throughflow/contracts.py`: design, task and result contracts
  (Pydantic, strict, extra fields forbidden).
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

The design supplies passage geometry and blade geometry: blade count, axial
chord, rotor tip clearance, trailing-edge thickness and eleven-point inlet,
exit and stagger-angle distributions. The task owns the operating point,
numerical resolution, physics profile, loss and deviation models and any
calibrated values. `prepare_simulation_inputs` validates both and hands them to
the simulator together, so a design can never choose the referee that scores it.
