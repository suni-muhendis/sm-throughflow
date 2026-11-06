# Phase 1 refinement and admission follow-up

Date: 2026-11-04. Simulator: `slc_aungier_experimental_v7`.
Physics profile: `axial_compressor_aungier_v2`, unchanged from v6.
This report extends [the v6 implementation record](phase01_implementation.md).
It demonstrates numerical verification, not experimental acceptance. The score
remains disabled and successful results retain `empirical_validation="pending"`.

## Refined-grid iteration

V6 failed to converge the four-subdivision synthetic duct grid within 400 and
1,000 outer iterations. Novak's local relaxation decreases with axial spacing
squared. Its adaptive B* reduction compounded this slowdown after transient
residual increases. Raising the iteration budget alone eventually found a root;
the tests below compare that root with the accelerated method.

V7 applies weighted Type-II Anderson acceleration to stream-surface positions
and endwall blockage together. The base update is still Novak's damped step;
B* stays fixed during acceleration. The least-squares residual is scaled by
local relaxation factors so closely spaced duct residuals retain influence.
The method follows [Walker and Ni (2011)](https://users.wpi.edu/~walker/Papers/Walker-Ni%2CSINUM%2CV49%2C1715-1735.pdf);
the bounded history and safeguards are implementation choices.

Up to 40 secant steps are retained. Extrapolated states must be finite, ordered,
within the blockage bounds and move less than 0.03 of span in one step. A rejected
extrapolation uses the base step and resets history. A failed accelerated solve
retries the original adaptive Novak method before the existing loss homotopy.
The task owns `repositioning` and `acceleration_depth`; the design cannot select
them. Every attempt reports its method and outcome. This changes the iteration
path, not the closures, required undamped residuals or independent balance checks.

## Frozen full-model results

[Resolution campaign](../validation/campaigns/20261104T172834809095Z_slc_aungier_experimental_v7/resolution.md):
one synthetic stage, eleven stream surfaces for axial refinement, one duct
subdivision for radial refinement. Outer tolerance is 1e-7, maximum 400 iterations;
the blade rows remain single gaps. Every row below passed admission, convergence
and independent physical verification in one accelerated attempt.

| Axis | Resolution | Pressure ratio | Isentropic efficiency | Outer iterations |
|---|---:|---:|---:|---:|
| Duct subdivisions | 1 | 1.15671925424 | 0.928366261 | 18 |
| Duct subdivisions | 2 | 1.15647755733 | 0.928284980 | 29 |
| Duct subdivisions | 4 | 1.15637349350 | 0.928178686 | 52 |
| Duct subdivisions | 8 | 1.15631536945 | 0.928144378 | 108 |
| Duct subdivisions | 16 | 1.15625220891 | 0.928136125 | 213 |
| Stream surfaces | 11 | 1.15671925424 | 0.928366261 | 18 |
| Stream surfaces | 21 | 1.15667178316 | 0.928442984 | 18 |
| Stream surfaces | 41 | 1.15668512540 | 0.928479271 | 18 |

The 8-to-16 change is about 0.0404% of the finest predicted pressure rise
(`PR - 1`) and 0.000825 efficiency percentage points. The last pressure-ratio
increment is slightly larger than the preceding increment, so the sequence does
not establish an asymptotic order or support a Richardson error bound. Radial
21-to-41 changes are about 0.0085% of pressure rise and 0.00363 efficiency points.
These are observed sensitivities, not universal grid-independence thresholds.

[Independent iteration-path and local-flow campaign](../validation/campaigns/20261104T172845121878Z_slc_aungier_experimental_v7/manifest.json):

| Case | Method | Iterations | Pressure ratio |
|---|---|---:|---:|
| Four subdivisions, reference flow | Original Novak | 1210 | 1.15637348253 |
| Four subdivisions, reference flow | Anderson | 52 | 1.15637349350 |
| Eight subdivisions, 97% reference flow | Anderson | 130 | 1.16773962128 |
| Eight subdivisions, 103% reference flow | Anderson | 91 | 1.14351946097 |

The refined-grid methods differ by 1.10e-8 in pressure ratio at the same tolerance.
Both pass the same balances. The local flow probes check that the improvement is
not confined to one exact flow value; they do not establish full off-design map
coverage or physical choke/stall boundaries. Preliminary algorithm experiments
are archived separately as explicitly marked prototypes using v6 source snapshots;
they must not be pooled with unmodified v6 or production v7 results.

## Between-section geometry admission

The contract's eleven piecewise-linear span input distributions are reconstructed
at 41 positions, including quarter intervals, using the shared section builder.
Projected chord and constructed surface/contact checks use those sections.
A regression case has valid projected chord at all eleven input nodes but an
invalid intermediate projection; v7 rejects it. Derived nonlinear geometry is
reconstructed from interpolated inputs for admission, not interpolated from the
derived values at the nodes. The row model retains its existing eleven-node
derived-parameter interpolation; this change does not establish continuous-span
equivalence or a CAD certificate.

V7 provisionally restricts each angle, chord, thickness and MCA input distribution
to monotone or single-extremum trends. More than one significant reversal is
explicitly unsupported (roundoff threshold: 1e-10 times max(1, field magnitude)).
This conservative project restriction is not an empirical law: it can exclude
physically valid blades. The 41-section/401-point surface checks remain discrete.
Generated-design qualification must test residual gaps, unusual parameter
combinations and improvements smaller than the numerical/model uncertainty.

## Regression evidence and remaining gates

- Full suite: **171 passed, 1 skipped** in 263.46 s. The skipped lazy-import check
  passed separately in a fresh process. A subsequently added forced-acceleration
  failure test also passed and confirms successful deterministic Novak fallback.
- Wheel and sdist builds passed. Installing the wheel in a clean temporary venv
  and solving the reference case gave PR=1.156719254239527, matching the local
  result. `pip check`, compilation and the diff whitespace check passed.
- Regression coverage includes 4/8/16 duct refinement at unchanged tolerance,
  agreement with the original coarse-grid root at tighter tolerance, rejection
  of inadmissible extrapolation, intermediate projection, and spanwise oscillation.
  Existing geometry, Reynolds, conservation, determinism and multi-stage checks
  are included in the full suite. V5 and v6 golden records remain separate.
- Every campaign archives source, dependency versions, exact inputs, outputs,
  hashes and the dirty patch. Historical experimental results are not rewritten.

Phase 0/1 implementation has advanced; its general resolution and cross-platform
gates remain open. The next planned work is structured off-design failure/map
classification, then frozen experimental validation and generated-design
qualification. Training-quality feedback requires those gates as well as numerical
verification; good convergence alone cannot validate loss, deviation or rankings.
