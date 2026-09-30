# Changelog

All notable changes are recorded here. The simulator and the score function
carry their own versions; a package release does not make results from
different simulator or score versions comparable.

## [Unreleased]

First release as a package of its own, extracted with its history from the
research repository (`sunimuhendis.environments.turbomachinery_throughflow`).
Simulator `nasa_turbo_design_experimental_v2` is unchanged: every reference
case produces the same result.

### Changed

- The package is `sm-throughflow`, imported as `sm_throughflow`, and builds on
  `sm-core`. It registers `turbomachinery_throughflow` in the
  `sm_core.environments` entry-point group.
- NASA `turbo-design` is a declared dependency instead of a separate
  requirements file.
- The asset command is `sm-throughflow-setup-assets`.
- The score function is versioned: `throughflow_score_disabled_v1`.
