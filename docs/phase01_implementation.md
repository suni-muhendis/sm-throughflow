# Phase 0/1 implementation and verification

Date: 2026-11-04. Simulator: `slc_aungier_experimental_v6`.
Physics profile: `axial_compressor_aungier_v2`. Score: still disabled.

The geometry-transfer, Reynolds-coupling and convergence defects are addressed.
The full Phase 1 acceptance gate remains open: general grid independence and
spanwise geometry qualification have not been demonstrated. Experimental
accuracy and design-response validation remain later gates.

## Implemented changes

- Preserve genuine hub/shroud contour vertices and explicitly map row edges to
  solver stations. Task-owned duct refinement cannot duplicate blade work.
  Redundant collinear vertices are removed before discretization. Reject a
  nonlinear wall segment within a single-gap blade row rather than ignoring it.
- Share constructed section parameters, including MCA stagger, across admission
  and simulation. Check sampled surfaces for intersections/closed cascades.
  Reject crossed stage labels and assign stators to their preceding rotor.
- Use Sutherland air viscosity at each row's local inlet static temperature.
  Report chord Reynolds number and the active correction. Tests vary density,
  temperature and physical scale at otherwise similar operating conditions.
- Declare the air model, provisional temperature restriction and unsupported
  mechanisms in [the scope specification](throughflow_domain.md). Record
  unvalidated Mach/Re ranges explicitly instead of implying unrestricted validity.
- Enforce every inner convergence limit and strengthen the outer field residuals.
  Retain failure identity/residuals and every cold/homotopy attempt. The local
  environment adapter preserves diagnostics that sm-core v0.8.0 otherwise drops;
  no other repository was changed.
- Check mass, stream-tube fractions, Euler work, integrated energy, duct angular
  momentum, positive states and entropy independently of the nonlinear stopping
  criterion. With mixing, use global balances and allow local entropy redistribution.
- Reject negative smoothed loss; retain Aungier's source equation and avoid an
  undocumented floor. Expose final loss, blockage and meridional-Mach limit flags.
- Make the endwall iteration budget task-owned, default 200, keeping the inner
  tolerance at 1e-8. The previous 50-pass budget fails during startup of the
  three-stage synthetic reference; 200 passes allow a converged, verified solution.
- Freeze runtime/input identities and numerical dependencies. Reject evaluating
  stale imported code after source files change. New campaigns use exclusive
  output paths, archive exact source bytes and data hashes, and retain failures.

## Evidence and historical preservation

[Pre-change v5 snapshot](../validation/campaigns/20261104_phase01_baseline/manifest.json)
contains the original dirty working copy, existing untracked studies, historical
results, dependencies and complete one-/three-stage inputs and outputs.
The source archive is approximately 1.4 MB. SHA-256 comparison confirmed that
**811 historical data/result/report files remain unchanged**. Old v5 goldens are
retained beside distinct v6 values; they were not rewritten to make tests pass.

[Final reference campaign](../validation/campaigns/20261104T164259053924Z_slc_aungier_experimental_v6/manifest.json)
records the final one- and three-stage default configurations and full outputs.
The one-stage pressure ratio changes from 1.15595286884961 to 1.15671925374717;
this is an intentional versioned change with the local Reynolds correction active.
The final three-stage pressure ratio is 1.58307916423127, with all required
inner/outer convergence and physical balance checks passing.

[Resolution campaign](../validation/campaigns/20261104T163106420091Z_slc_aungier_experimental_v6/resolution.md)
contains five successes and an explicit failure. Its archive and every result's
source identity were checked against the manifest. This campaign preceded the
change of the endwall iteration budget from 50 to 200; its exact source/settings
are archived and are not silently relabelled as a final-default campaign.

| Independent refinement | Total pressure ratio | Isentropic efficiency | Outcome |
|---|---:|---:|---|
| Duct subdivisions 1, surfaces 11 | 1.15671925374717 | 0.92836626048211 | Verified success |
| Duct subdivisions 2, surfaces 11 | 1.15647754341915 | 0.92828497823417 | Verified success |
| Duct subdivisions 4, surfaces 11 | unavailable | unavailable | Outer limit: 400 iterations, residual 1.82457e-4 versus 1e-7 |
| Surfaces 21, duct subdivisions 1 | 1.15667178289897 | 0.92844298370500 | Verified success |
| Surfaces 41, duct subdivisions 1 | 1.15668512522989 | 0.92847927099157 | Verified success |

The 21-to-41 radial change is about 0.0085% of the predicted pressure rise and
0.00363 efficiency percentage points. This is small for this synthetic case;
the pressure-ratio sequence is not monotone and no general grid-error bound is
claimed. Axial grid independence is **not established**. The earlier 1000-iteration
exploratory failure is retained separately with a review note; that interim run
is not used as final reproducibility evidence because edits continued during it.

The independent analytic conical-source tests still exercise the SLC equations
and second-order radial accuracy. Synthetic compressor studies do not replace
experimental performance/profile validation.

## Additional failures now caught

- The severe inlet constriction has independent ideal sonic capacity below
  10 kg/s and can no longer return success at the requested 80 kg/s.
- Forced exhaustion of row, quasi-normal, endwall and outer iteration limits
  produces structured failure instead of a usable number.
- A corrupted converged energy or duct angular-momentum field is rejected.
- Optional Gallimore mixing at 11 surfaces has angular-momentum flux residual
  8.9346e-6 against a 2e-6 limit and is rejected. At 41 surfaces it is 7.1619e-7
  and passes; energy residual is 3.0383e-8. Local entropy decreases by as much
  as 0.07381 J/(kg K) while integrated production remains nonnegative, which
  illustrates why a per-stream entropy check would be incorrect with mixing.
- A similar operating point with inlet T0=450 K is explicitly outside the
  provisional air envelope; custom gas constants and explicit old versions
  cannot silently select a different evaluator.

## Final test and package checks

- Full suite: **164 passed, 1 skipped** in 418.62 seconds on Windows/Python
  3.12.10 with the pinned numerical stack. The skip is the order-dependent
  lazy-import check; running that test alone passed (1 passed in 0.94 seconds).
- `python -m pip check`: no broken requirements. `git diff --check`: clean.
- Final wheel and source distribution built successfully. Installing the wheel
  into a clean temporary environment with `constraints-validation.txt` and
  running `scripts/check_wheel.py` passed, reproducing PR 1.1567192537471698.
- [Final source and test evidence](../validation/campaigns/20261104T164727274880Z_slc_aungier_experimental_v6/verification.json)
  records the final checks; its manifest and archive identify the final sources.
  Source bytes were verified against the archive. Linux CI has not been run here.

The expanded tests include deliberately slow failure and refinement cases; their
runtime is not a representative per-design throughput benchmark. That benchmark
remains part of the later robustness/performance work.

## Remaining gates

The [updated reliability plan](throughflow_reliability_plan.md) leaves open:

1. Reliable convergence under finer axial discretization and a numerical
   uncertainty bound suitable for comparing design improvements.
2. Quantified limits for spanwise oscillation and geometry between the eleven
   admitted sections, beyond sampled section intersection checks.
3. A completed Linux/Windows comparison on the pinned numerical stack.
4. Physical versus numerical map-boundary classification, continuation and
   coverage, then experimental and generated-design acceptance (Phases 2-4).

These changes prevent several misleading successes and make failures traceable.
They do not yet qualify the tool as an industrial compressor evaluator or as
accepted performance feedback for training. The score remains zero.
