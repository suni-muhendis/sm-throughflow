# AGENTS.md

Guidance for AI coding agents (Claude Code, Codex, and others) working in this
repository.

## What this is

`sm-throughflow` (import `sm_throughflow`) is the experimental turbomachinery
throughflow environment of the Suni Muhendis benchmark. It implements the
`sm-core` contract (schema, design-rule check, simulator, score) and registers
itself as `turbomachinery_throughflow` in the `sm_core.environments`
entry-point group.

It solves axial compressors with its own streamline-curvature solver
(`sm_throughflow.solver`, Aungier 2003 ch. 7) and Aungier's cascade, leakage,
end-wall and blade-throat models (`sm_throughflow.correlations`). The
simulator is `slc_aungier_experimental_v16`; the contracts are
`throughflow_design_v2` / `throughflow_task_v2`
(`docs/throughflow_contract_v2.md`). Turbines are not supported yet; they will
use the same solver core.

Earlier simulators (up to `nasa_turbo_design_experimental_v4`, on a fork of
NASA `turbo-design`) and their v1 contracts were removed; they remain in the
git history. The reason the NASA solver was dropped is in
`docs/throughflow_solver.md` and `docs/compressor_validation.md`.

The repository is **private** until the maintainers decide to publish the
environment. It is not yet part of SM-Bench.

## Commands

- Setup: `python3.12 -m venv .venv`, activate it,
  `python -m pip install -c constraints-validation.txt -e ".[dev]"`.
- Tests: `python -m pytest tests -q`.
- Demo: `python scripts/run_throughflow.py --stages 3`.
- Wheel check: `python -m build` then `python scripts/check_wheel.py dist`.
- Validation data checks: `python validation/tools/check_lewis_geometry.py`
  and `python validation/tools/compare_passes.py` (see `validation/README.md`).

## Rules

- **Versions are real.** `ThroughflowTaskV2.simulator_version` accepts only
  `SlcAungierSimulator.VERSION`. Any change that can move a number (a solver
  or correlation change) needs a new simulator version and new reference
  values; results from different versions are never pooled.
  `tests/test_throughflow_env.py` holds separate v5 through v16 goldens. The v5
  working-copy baseline is archived under `validation/campaigns/`; do not
  overwrite it or pool historical versions with v16 results.
- **Correlations are transcribed from their sources and tested against them.**
  Every function in `correlations/` cites its equation; the docs record each
  source, each misprint found and each choice the source leaves open.
- **The score is disabled.** `ExperimentalThroughflowScore` returns zero for
  every design until the physics passes the acceptance gate in
  `docs/compressor_validation.md`.
- **Determinism is a hard requirement.** Identical input gives identical
  output; tests assert it.
- **Validation data are verbatim.** Files under `validation/cases/` are
  transcriptions of report pages and follow `validation/TRANSCRIPTION_GUIDE.md`;
  never "fix" a printed value there. Interpretation belongs in code.
- Prefer "score" over "reward" in new code and documentation.
- Consumers pin tags, never branches. Record user-visible changes in
  `CHANGELOG.md`.

## Layout

- `src/sm_throughflow/contracts.py`: design and task contracts (Pydantic,
  strict, extra fields forbidden) and the frozen physics profiles;
  `drc.py` the design rules; `simulator.py` the simulator; `env.py`
  `TurbomachineryThroughflowEnv`; `score.py` the disabled score.
- `solver/`: the streamline-curvature solver (`throughflow.py`,
  `quasi_normal.py`, `geometry.py`, `gas.py`), Aungier's row model
  (`aungier_row.py`) and end-wall boundary layers (`endwall.py`).
- `correlations/`: solver-independent cascade correlations and blade
  geometry (numpy/scipy only).
- `scripts/run_throughflow.py`: the reference repeating-stage compressor the
  tests use. `scripts/check_wheel.py`: wheel smoke test.
- `docs/`: solver, correlations, row model, end-wall model, contract, roadmap
  and validation status.
- `validation/`: transcribed geometry of open test cases and the tools that
  check it.

## Ownership boundary

The design supplies passage geometry and blade geometry: blade count, edge
planes, profile family, clearances or shroud seals and eleven-point angle,
chord and thickness distributions. The task owns the operating points,
numerical resolution, gas, physics profile and any calibrated values.
`prepare_simulation_inputs` validates both and hands them to the simulator
together, so a design can never choose the referee that scores it.
