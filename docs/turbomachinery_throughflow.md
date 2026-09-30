# Turbomachinery throughflow environment

This environment is an experimental adapter to NASA `turbo-design`, run on
the Suni Muhendis fork (see Backend below). It accepts
multi-stage axial compressor and turbine designs, uses ten streamtubes, and
requires eleven hub-to-shroud values at `0.0, 0.1, ..., 1.0` for inlet metal
angle, exit metal angle, and the physical profiles' stagger angle.

## Reproducible setup

NASA code remains an external dependency under the NASA Open Source Agreement;
it is not copied into the sm-throughflow wheel.

```bash
python -m pip install -e ".[dev]"
sm-throughflow-setup-assets
```

The package pins the reviewed NASA revision as a dependency. The setup command
downloads the Kacker-Okapuu and Ainley-Mathieson chart data from that same
revision and verifies their SHA-256 hashes. Simulation never accepts an
unverified pickle and does not silently download mutable data from NASA `main`.

A consumer installs the package at an immutable tag and runs the same packaged
setup command:

```bash
python -m pip install "sm-throughflow @ git+https://github.com/suni-muhendis/sm-throughflow.git@<tag>"
sm-throughflow-setup-assets
```

## Ownership boundary

The model supplies passage geometry and blade geometry: blade count, axial
chord, rotor tip clearance, trailing-edge thickness, and eleven-point inlet,
exit, and stagger-angle distributions. The benchmark task owns operating
conditions, numerical resolution, loss model, deviation model, and any
calibrated fixed loss or deviation values. This prevents a model from choosing
the referee that scores its own design.

`axial_compressor_candidate_v1` applies the preliminary Lieblein diffusion
loss and Carter deviation. Local pitch and solidity are derived from radius,
blade count, axial chord, and the supplied stagger at every span station.

`axial_turbine_candidate_v1` currently uses TD2 as an interim correlation.
Kacker-Okapuu and Ainley-Mathieson remain shadow candidates: Kacker-Okapuu now
runs on spanwise rows, but its stator secondary-loss calculation is not yet
validated. Turbine deviation remains zero unless a task supplies a calibrated
fixed eleven-point distribution.

Both candidate profiles return a score of zero. They can be scored only after
independent compressor and turbine validation cases establish error limits for
performance, spanwise flow, off-design behavior, and numerical resolution.

The current compressor evidence, executable comparison, NASA EEE audit, and
scoring gate are documented in
[compressor_validation.md](compressor_validation.md).

## Backend

The simulator runs on `suni-muhendis/turbo-design@v1.4.4-sm.1`, a fork of NASA
`turbo-design` 1.4.4 with seven fixes listed in its `MODIFICATIONS.md`. Four
leave results unchanged; three change them: radial equilibrium uses the static
pressure, the diffusion loss uses the Lieblein diffusion factor, and Carter
deviation returns degrees from the row's metal angles. The fixes replace two
adapters this environment needed on NASA 23c2b0bf (a corrected Carter
deviation and a mean-line geometry wrapper for Kacker-Okapuu); removing them
leaves every reference case unchanged. Results from simulator `…_v2` (NASA
23c2b0bf) and `…_v3` (the fork) are never pooled: moving from 1.4.3 to 1.4.4
alone changes turbine power by about 5%.

## Result diagnostics

Each blade row reports total pressure and temperature, absolute and relative
Mach number, loss coefficient, solidity, applied deviation, absolute and
relative exit flow angles, metal angles, tip-clearance fraction, and
trailing-edge-to-pitch ratio. `fidelity_notes` identifies physics that remains
approximate or unavailable.
