# Changelog

All notable changes are recorded here. The simulator and the score function
carry their own versions; a package release does not make results from
different simulator or score versions comparable.

## [Unreleased]

First release as a package of its own, extracted with its history from the
research repository (`sunimuhendis.environments.turbomachinery_throughflow`).
The extraction alone changes no number; the move to the turbo-design fork
that follows it is a new simulator version.

### Changed

- The package is `sm-throughflow`, imported as `sm_throughflow`, and builds on
  `sm-core`. It registers `turbomachinery_throughflow` in the
  `sm_core.environments` entry-point group.
- NASA `turbo-design` is a declared dependency instead of a separate
  requirements file.
- The asset command is `sm-throughflow-setup-assets`.
- The score function is versioned: `throughflow_score_disabled_v1`.
- **Simulator `nasa_turbo_design_experimental_v3`** runs on the fork
  `suni-muhendis/turbo-design@v1.4.4-sm.1` instead of NASA 23c2b0bf. Its
  numbers differ from v2 and are never pooled with them: NASA 1.4.4 and the
  fork's radial-equilibrium, Lieblein and Carter fixes move the reference
  cases (OptTurb turbine power +5.3%, Mattingly 9.1 pressure ratio -0.10%).
  The repeated two-stage candidate compressor now plateaus at a massflow
  residual of 2.26e-6 and is rejected by the 1e-6 tolerance.
- The corrected Carter deviation and the mean-line Kacker-Okapuu adapters are
  removed; the fork fixes both upstream, and every reference case gives
  identical numbers without them.
- Loss-model chart data downloads from the fork tag (same SHA-256).
- **Simulator `nasa_turbo_design_experimental_v4`** on `v1.4.4-sm.2`: the
  compressor solve converges on the radial profiles, not on the massflow
  spread. `numerics.max_iterations` now reaches the solver, the new
  `numerics.convergence_tolerance` (default 1e-6) sets the stopping point, and
  a compressor that does not converge is a simulation error. Compressor
  results move by at most 7e-6; turbine results are unchanged. The repeated
  two-stage candidate compressor converges again. Results report
  `solver_solution_change`.
