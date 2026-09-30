# Axial compressor physics roadmap

Goal: solve multi-stage axial compressors at 11 streamlines (10 streamtubes)
with the most complete physics a throughflow method supports: incidence,
deviation, and every loss mechanism an empirical correlation set can model.
Beyond that set lies CFD, which is out of scope.

The target correlation set is Aungier's axial-compressor model, which
assembles the classical NASA cascade data into one consistent off-design
method. Turbines follow the same structure later.

## Where the physics lives

Correlations are our own code and live in this package, not in the
`turbo-design` fork. The fork takes solver fixes only.

```
sm_throughflow/correlations/   pure functions, numpy only, no turbodesign import
    inputs:  cascade geometry (profile family, camber, t/c, x_tmax/c, stagger,
             solidity, clearance) and flow state (inlet/exit angles, Mach, Re)
    outputs: reference incidence and deviation, incidence range, loss
             coefficients by mechanism
sm_throughflow/backend/        thin adapters to turbo-design's loss and
                               deviation interfaces (per-streamline arrays)
```

Keeping the correlations free of any solver API lets a future cascade solver
reuse them unchanged. Every correlation carries its source and is tested
against published chart values or worked examples before it is wired in.

## What exists today (simulator `nasa_turbo_design_experimental_v3`)

- Loss: the Lieblein diffusion-factor `DiffusionLoss` only. The fork's
  `AxialCompressorAungier`, `AxialCompressorEntropy` and
  `AxialCompressorWrightMiller` are mean-line placeholders with invented
  coefficients; `NASA74A` and `NASA23B20` return zero. None is used.
- Deviation: Carter's rule.
- No incidence model, shock loss, endwall or tip-clearance loss, spanwise
  blockage, or spanwise mixing.
- The solver applies `Yp` and deviation per streamline; blockage is one scalar
  per row; the compressor massflow loop stops after at most ten passes.
- The design contract has no profile family, thickness or thickness location.

## Phases

Each phase that can move a number ships as a new physics profile and, where
the backend changes, a new simulator version, with characterization goldens.

### 1. Foundation
- `correlations/` and `backend/` packages; adapter contract; test conventions
  (every function pinned to published values).
- Solver robustness at 10 streamtubes for multi-stage cases: expose the
  iteration limit (today `Numerics.max_iterations` is not passed to the
  backend), and investigate the two-stage residual plateau (2.26e-6).

### 2. Design contract v2 (`throughflow_design_v2`)
- Per blade row, eleven span values of: profile family (NACA 65, DCA, MCA),
  maximum thickness to chord, maximum-thickness location, in addition to the
  existing metal angles and stagger. Camber follows from the metal angles.
- v1 designs keep working under the v1 profiles.

### 3. Design-point cascade physics
- Minimum-loss (reference) incidence and reference deviation from the NASA
  SP-36 cascade correlations, with thickness and profile-family corrections.
- Profile loss at minimum-loss incidence from the equivalent diffusion ratio
  (Lieblein), with Reynolds-number and inlet-Mach corrections.

### 4. Off-design cascade physics
- Positive and negative stall incidence limits (Aungier) and the incidence
  loss across that range.
- Deviation variation with incidence (the SP-36 slope) and with Mach number.

### 5. Transonic rows
- Shock loss for supersonic relative inlet Mach (Miller-Lewis-Hartmann or
  Koch-Smith).

### 6. Three-dimensional effects
- Endwall and secondary loss (Howell / Aungier) and tip-clearance loss
  (Storer-Cumpsty), distributed toward the endwall streamlines.
- Endwall boundary-layer blockage, per streamline. Needs spanwise blockage in
  the backend (fork change).
- Spanwise mixing between rows (Adkins-Smith or Gallimore-Cumpsty). Without it
  loss accumulates unrealistically at hub and tip through a multi-stage
  machine. Needs a mixing step in the solver loop (fork change).

### 7. Validation (the gate for scoring)
- Single stage with spanwise data: NASA Rotor 37 and Stage 35.
- Multi-stage: NASA five-stage core compressor 74A, then the EEE
  high-pressure compressor (10 stages, NASA CR-165558).
- Errors reported against the acceptance gate in
  [compressor_validation.md](compressor_validation.md).

## Sources (to confirm against the originals before each implementation)

- R. H. Aungier, *Axial-Flow Compressors: A Strategy for Aerodynamic Design
  and Analysis*, ASME Press, 2003.
- I. A. Johnsen and R. O. Bullock (eds.), *Aerodynamic Design of Axial-Flow
  Compressors*, NASA SP-36, 1965 (Lieblein's cascade chapters).
- S. Lieblein, "Loss and stall analysis of compressor cascades", J. Basic
  Eng., 1959.
- C. C. Koch and L. H. Smith, "Loss sources and magnitudes in axial-flow
  compressors", J. Eng. Power, 1976.
- G. R. Miller, G. W. Lewis and M. J. Hartmann, "Shock losses in transonic
  compressor blade rows", J. Eng. Power, 1961.
- A. R. Howell, "Fluid dynamics of axial compressors", Proc. IMechE, 1945.
- J. A. Storer and N. A. Cumpsty, "An approximate analysis and prediction
  method for tip clearance loss in axial compressors", J. Turbomach., 1994.
- G. C. Adkins and L. H. Smith, "Spanwise mixing in axial-flow
  turbomachines", J. Eng. Power, 1982; S. J. Gallimore and N. A. Cumpsty,
  "Spanwise mixing in multistage axial flow compressors", J. Turbomach., 1986.
- L. Reid and R. D. Moore, NASA Rotor 37 and Stage 35 test reports, 1978.
