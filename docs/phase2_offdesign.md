# Phase 2: off-design evidence and bounded continuation

Date: 2026-11-04. Simulator: `slc_aungier_experimental_v8`.
Physics profile remains `axial_compressor_aungier_v2`. Cold-start reference
performance is unchanged from v7. The version boundary covers restart paths,
capacity checks and map/anchor interpretation. The score remains disabled.

Frozen final-source evidence: [campaign manifest](../validation/campaigns/20261104T181357498201Z_slc_aungier_experimental_v8/manifest.json),
[synthetic paths](../validation/campaigns/20261104T181357498201Z_slc_aungier_experimental_v8/synthetic_map.json),
[capacity rejection](../validation/campaigns/20261104T181357498201Z_slc_aungier_experimental_v8/physical_capacity.json),
[iteration-budget failure](../validation/campaigns/20261104T181357498201Z_slc_aungier_experimental_v8/iteration_budget.json),
and [historical hole inventory](../validation/campaigns/20261104T181357498201Z_slc_aungier_experimental_v8/historical_holes.json).

## Classification

The outer sm-core statuses are unchanged. Structured evidence is carried in raw
output, and every requested operating point is attempted even after a failure.
Any failed requested point still invalidates the aggregate evaluation.

| Classification | Evidence and interpretation |
|---|---|
| `converged` | Full-model iterations and physical verification pass; empirical validity is still pending |
| `converged_with_model_limit` | Same convergence checks, but a converged throat-capacity or stall correlation indicator crosses its criterion; not a stable-map or surge claim |
| `physical_limit` | Requested flow exceeds an independent sonic capacity upper bound in the inlet or unworked inlet duct |
| `unresolved_capacity_limit` | A quasi-normal cannot carry the requested flow on an iterative state; whole-machine choking has not been established |
| `numerical_failure` | An iteration or root solve failed its numerical requirements |
| `unsupported_condition` | Geometry or gas/model scope is outside the declared implementation |
| `invalid_geometry`, `invalid_input`, `invalid_restart` | Admission or restart prerequisites fail; the specific reason is retained |
| `invalid_state` | Thermodynamic, balance or closure admissibility fails; this is not proof that the requested compressor is physically impossible |
| `unexpected_error` | An unclassified implementation/adapter failure, kept distinct from physical evidence |
| `path_sensitive` | Successful initialization paths disagree beyond the frozen comparison tolerance; no aggregate performance is selected |

The independent bound uses the perfect-gas sonic mass flux at prescribed uniform
inlet total pressure and temperature. It bounds flow through each represented
section before the first blade row, without downstream work or an iterative flow
state. Endwall runs use unblocked area conservatively; inclined geometry drops a
projection factor no greater than one. Nonuniform inlet totals and prescribed
swirl do not receive this bound. This necessary upper bound does not locate the
actual choke point. Source: [NASA Glenn mass-flow choking](https://www.grc.nasa.gov/www/k-12/airplane/mflchk.html).

The row throat margin is `o/s * rho*W* / (rho1*Wm1) - 1`, using Aungier's (6-53)
assumptions. It is reported on converged states separately from the diffusion-based
stall criterion. Both remain empirical model indicators; no system surge model
or experimentally validated blade-row choke boundary is introduced.

## Restart and map policy

`Throughflow.solve(start=...)` accepts finite, ordered stream-surface positions
with fixed endpoints and the current grid shape. The simulator adapter additionally
checks a fingerprint of geometry, task, speed and mixing settings. Only surface
positions are reused; flow fields and endwall state are recomputed. A failed restart
retries the deterministic cold policy and then the existing loss homotopy. Only a
converged loss-scale-one result can be accepted.

`trace_map` evaluates requested flows cold, then in ascending and descending
continuation order. Steps halve on failure and grow by 1.5 on success, subject to
maximum/minimum relative steps and a finite bridge budget. It explicitly attempts
each requested target even when bridging fails. Original ordering, intermediate
probes, failed points and later successes are preserved. The default root comparison
uses relative tolerance 1e-5 plus absolute tolerance 1e-7 on performance metrics;
iteration counts are excluded. These are numerical comparison settings, not
empirical uncertainty bounds. Agreement never proves uniqueness outside sampled paths.

Cold results have fixed priority, then ascending, then descending. Disagreement
suppresses aggregate metrics and retains all branches. Interior failed or ambiguous
points are bounded by their nearest sampled successful neighbours. A successful
warm start after a failed cold start is flagged as initialization-sensitive.

`find_upper_boundary` has a finite probe budget, look-ahead and bisection. It returns
the sampled bracket and its evidence. A numerical/unresolved boundary has no choke
anchor and cannot normalize measured flow. Peak/stall interpolation never crosses a
failed gap. Stall anchors remain criterion crossings, not surge predictions.

Effort counters include all outer iterations, station solves, row-model calls and
endwall solves across every failed and successful attempt. They do not claim to
count every internal scalar operation. Per-evaluation wall time is separate campaign
telemetry, is not deterministic, and never influences branches, scores or tolerances.

## Evidence and scope

The synthetic verification uses the one-stage reference at 77.6, 80.0 and 82.4 kg/s.
All cold/ascending/descending results converge and pass the same physical checks.
The largest path spread in pressure ratio is below 1.6e-10. Across the eight actual
evaluations (including one bridge and reused endpoints), the recorded effort is
149 outer iterations, 4,227 station solves and 3,631 row-model calls.

A requested 500 kg/s exceeds the independent 114.9785268 kg/s inlet-duct bound and
is rejected before iteration. A separate 16-subdivision case with a ten-iteration
Novak budget is a numerical failure, not choke: its cold and zero-loss attempts
both exhaust ten iterations, for twenty outer iterations in total.

All **39 historical interior holes** across 17 parameter sweeps were reconstructed
with their adjacent historical successes and rechecked against the current scope.
All those local brackets lie outside the current geometry domain. Nineteen are
mass-flow holes in four machine families; the remainder vary geometry. This bounds
the present coverage claim; it does **not** diagnose or repair the original failures.
Original full input records were not saved, so the reconstruction records its
historical baseline-reading selection and source hashes explicitly.

The historical exclusions include non-linear wall contours inside a single-gap
blade row. Keep that restriction explicit; do not simplify measured geometries
silently to make them pass. General map coverage and experimental choke/stall
accuracy remain unqualified. The Phase 2 machinery is implemented; industrial
acceptance still requires representative admitted cases, resolved/bounded gaps,
and the independent validation and generated-design gates in the plan.

Reproduce the evidence with `python validation/verify_phase2.py`; use
`--historical-only` for scope triage. Each invocation archives its source, input
selection and outputs under a new campaign. The direct experimental adapter in
`validation/run.py` deliberately bypasses DRC and labels that research path, but
shares convergence, balance and gas-scope checks with the environment.

## Test and packaging record

- Full Phase 2 regression: **193 passed, 1 skipped** in 730.65 s.
- Review then added scope-priority, correlation-range and partial-point metric
  checks, plus runner, analytic-boundary and warm-fallback coverage. After those
  corrections, **48 affected tests passed** on the final production source
  (off-design tests, all environment tests, and the inlet-constriction regression).
- The lazy-import test skipped by the combined run passed independently in a
  fresh process. Dependency consistency, compilation and diff checks passed.
- Wheel and sdist builds passed; a clean wheel installation reproduced reference
  PR=1.156719254239527. The simulator source fingerprint matches the frozen
  final-source campaign. All 811 historical data/result/report files remain
  byte-for-byte unchanged.

Coverage includes physical capacity versus iterative capacity, exhausted budgets,
scope exclusions before capacity claims, partial multi-point results, admissible
and mismatched restarts, deterministic cold fallback, adaptive bridge recovery,
branch disagreement, bounded searches, retained interior holes and prohibition
of choke normalization/stall interpolation across unresolved numerical gaps.
The analytic duct boundary brackets its closed-form choke capacity within 1e-4
relative flow. Neither these tests nor the local synthetic map establish an
experimental compressor operating envelope.
