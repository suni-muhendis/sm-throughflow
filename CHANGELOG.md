# Changelog

All notable changes are recorded here. The simulator and the score function
carry their own versions; a package release does not make results from
different simulator or score versions comparable.

## [Unreleased]

### Removed

- **Simulators `nasa_turbo_design_experimental_v2`ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦`v4`, the v1 design and task
  contracts, their physics profiles, loss-chart assets and reference scripts.**
  The package no longer depends on NASA `turbo-design` or Cantera; the
  environment runs only `slc_aungier_experimental_v5`. Turbines, which only
  the NASA path supported, return later on the package's own solver. None of
  the removed simulators was ever tagged or used by SM-Bench.

### Added

- **Back-pressure passage research.** Solve for a normal shock compatible
  with a fixed mass flow and outlet pressure. Compare pressure recovery,
  loss and attached displacement with NASA rotor evidence.

- **Rotor casing pressure benchmark.** Digitize the 12 NASA Stage 35–38
  pressure curves, match their rotor readings and screen the passage-shock
  candidate against the outermost measured loss.

- **Stage 35–38 loss attribution.** Separate rotor efficiency from the
  downstream pressure defect and bound the conditioned response to any
  common nonnegative direct-shock multiplier.

- **Trailing-edge wake junction research.** Preserve common-edge integral
  defects and compare a conditioned free-wake momentum march with NASA
  DCA cascade and controlled planar-wake measurements.

- **Local cascade displacement feedback.** Couple the attached layer and
  periodic pressure solution on prescribed surface intervals. Compare
  matched NASA DCA pressures and trailing-edge sensitivity before
  introducing a wake junction.

- **Periodic cascade surface-loading research.** Compute separate inviscid
  edge speeds, compare the two surface pressures with NASA DCA data, and
  record trailing-edge and near-stagnation sensitivity.

- **Stagnation and passage displacement research.** Initialize an attached
  layer from the local stagnation gradient. Couple laminar displacement
  to the subsonic core pressure of a symmetric reference passage and
  separate known inlet capacity from unresolved trial capacity.

- **Direct laminar blade-layer research.** Integrate momentum thickness,
  shape and dissipation with a prescribed smooth edge. Compare the
  calculation to NASA DCA profiles and expose sensitivity of the
  separation estimate to the supplied initial layer.

- **Shock loss budget and wake reduction research.** Screen shock loss
  against 36 measured Stage 35–38 sections. Add a conservative planar
  wake reduction and a low-speed NASA cascade traverse for checking the
  distinction between survey and mixed-out loss.

- **Post-v16 shock/interaction research; no production promotion.** Add
  choked normal/oblique passage-shock references and back-pressure queries,
  explicit domain failures, independent gas-dynamic/cache checks and a
  source-traced Rotor 37 shock/profile loss budget. Repeat the frozen
  experiment with a compressible-circulation hybrid: retain all 75 successes
  but reject its wrong family ordering and worse efficiency errors.
  See `docs/phase3_interaction_v16.md`; production remains v16.

- **Simulator v16: remove sampling quantization from MCA geometry.**
  Enforce the requested maximum-thickness and arc-transition locations with
  analytic meanline positions/tangents; compute maximum camber from its
  horizontal tangent and use a cancellation-resistant circular-segment formula.
  The frozen 108-job v15 comparison retains all classifications and Stage 53
  results. This fixes small geometric design responses, not the unresolved
  Stage 35–38 efficiency ordering. See `docs/phase3_geometry_v16.md`.
  A separate, incomplete detached-shock research oracle is not used by the
  production solver. Earlier `candidate_v16` artifacts remain rejected v15 probes.

- **Post-v15 research: reject insufficient conical/shock corrections.**
  Add independent conical-geometry and Schobeiri shock oracles, a frozen
  108-job comparison against v15, and a necessary family-response screen.
  The candidate preserves successful jobs but worsens efficiency ordering;
  it is not promoted. Production remains byte-identical v15. See
  `docs/phase3_candidate_v16.md`; the v16 filename is an investigation ID.

- **Simulator v15: invert the NASA Lewis equivalent-camber deviation rule.**
  Preserve absolute angular momentum when transporting exit flow to inlet
  radius and meridional speed. Recompute the reference outside the inlet cache,
  use it consistently in loss and exit triangles, and remove the duplicate MCA
  velocity correction. Retain Aungier's off-design incidence slope as an explicit
  hybrid assumption. Preserve v5-v14 goldens and rerun the same 108 jobs against
  v14. This consistency correction does not resolve Stage 35–38 efficiency
  ordering or qualify design-training labels; scores remain disabled.

- **Simulator v14: integrate passage-shock loss across sonic cuts.**
  Integrate pressure defect over dual inlet-mass cells, splitting at Mach 1;
  retain pointwise diagnostics and unchanged convergence tolerances. Locate
  the geometric shock foot on a continuous surface after projection onto the
  row cone. Recover the original Stage 53 design-speed point: 75/108 matched
  jobs converge versus 74/108 in v13, with no lost successes. The Stage 35–38
  efficiency ordering remains wrong; experimental qualification and design
  ranking remain disabled. Preserve v5–v13 references and historical evidence.

- **Simulator v13: actual-incidence passage-shock loss for DCA/MCA profiles.**
  Use the relative incoming flow direction and projected constructed foot tangent
  in the NACA Prandtl-Meyer expansion. Retain the tangent-incidence limit and
  expose suction incidence, signed flow turning and compression clipping.
  Preserve v5-v12 references and rerun all 108 frozen jobs against v12.
  This is an internal-physics correction, not an experimental accuracy upgrade:
  Stage 35–38 efficiency ranking remains wrong and scores remain disabled.

- **Simulator v12: duct wall substeps and conditioned fine-grid iteration.**
  Apply the task-owned wall integration count to ducts as well as blade gaps.
  Add an elliptic position preconditioner, fit raw Anderson residual differences,
  and retain step-construction failure traces. Retry failed fine-grid startup
  from checked full-model coarse solutions, preserving every grid attempt and
  its cost. Keep v5-v11 goldens and frozen experimental evidence; compare the
  same 108 jobs to v11 with independent analytic and resolution checks. Scores
  remain disabled; increased convergence coverage does not imply qualification.
- **Simulator v11: direct geometric curvature and compatible damping.** Replace
  composed first differences by local parametric quadratic derivatives,
  including consistent endpoint curvature. Verify circular paths, rigid motion,
  alternating-position modes and a manufactured near-planar flow. Use B*=4
  for the direct stencil; retain all residual and conservation tolerances.
  Preserve rejected-step traces in failed attempts and experimental outcomes,
  and identify the failed wall subinterval. Keep historical v5-v10 references
  and run a matched v10/v11 comparison with separate resolution studies.
- **Simulator v10: resolved wall march and safeguarded coupled steps.** Add
  task-owned boundary-layer subintervals (default eight per blade-row gap),
  normalized full-state residual checks and a bounded nonlinear fallback.
  Count numerical Jacobian probes against each interval budget. Evaluate the
  force-defect saturation without overflow. Roll back failed or excessive
  accelerated coupled steps before trying smaller ordinary steps; all trials
  consume the outer budget and remain in telemetry. Preserve v5-v9 reference
  values and rerun all 108 v9 jobs plus separate 16/32 wall-resolution checks.
  Correlation coefficients and experimental transcriptions remain unchanged.

- **Simulator v9: original wall controls and radial momentum numerics.** Separate
  blade-edge flow stations from interior annulus geometry, retaining wall slopes,
  curvature and arc length. Reject unresolved interior annulus throats. Integrate
  the same normal-momentum ODE in squared velocity and bracket hub speed in both
  directions; retain convergence tolerances and physical/numerical distinctions.
  Archive a matched rerun of all 54 v8 jobs, a second pass with original annuli,
  and measured-state closure checks. No correlation coefficients or experimental
  transcriptions change; the empirical gate and score remain closed. See
  `docs/phase3_geometry_convergence_v9.md`.

- **Phase 3 empirical audit of frozen v8.** Add preregistered measured-state
  row-closure comparisons, explicitly projected research geometries, 54 coupled
  and sensitivity jobs, density/spacing-aware radial-profile comparisons,
  clustered Mach/Re/loading error groups, family deltas and uncertainty-aware
  ranking diagnostics. Keep every failed outcome, missing observation and
  holdout-coverage gap visible. No physics coefficients or production source
  changed; the empirical gate and score remain closed. See
  `docs/phase3_validation.md` for the failed acceptance criteria and evidence.
- **Simulator v8: classified off-design outcomes and continuation.** Retain
  every requested operating point, including failures and later successes.
  Separate independent inlet-duct capacity bounds, unresolved iterative capacity,
  numerical failure, unsupported conditions, invalid states and converged model
  indicators. Add admissible geometry restarts with deterministic cold/homotopy
  fallback, bounded adaptive bidirectional map audits, path disagreement and
  interior-hole records, and effort counters across every attempt. Runtime is
  campaign telemetry and never affects a decision. Validation no longer uses a
  numerical boundary as a choke anchor or interpolates anchors across failed gaps.
  Historical v5-v7 results remain unchanged; the empirical gate and score stay shut.
- **Simulator v7: axial refinement and between-section admission.** Weighted
  Type-II Anderson acceleration advances stream-surface positions and blockage
  together, retaining actual residual and physical checks and a deterministic
  fallback to Novak's original iteration. The task owns the method and memory
  depth. v5/v6 characterization values and all prior campaigns remain unchanged.
  Geometry admission now checks 41 constructed span sections and declares
  repeated spanwise trend reversals unsupported in the provisional scope.
  The empirical profile remains v2 and the score remains disabled.
- **Simulator v6 / physics profile v2 reliability changes.** Preserve all real
  passage vertices, canonicalize redundant collinear points, refine ducts with
  explicit row indices, and reject unresolved wall contours within a blade row.
  Share constructed MCA section geometry with DRC, reject sampled blade
  intersections, and enforce consistent stage membership.
- **Local Reynolds correction and explicit air scope.** Blade-row viscosity now
  uses local static temperature through Sutherland's law, consistently with the
  endwall model. Report Re and limiter activations; reject custom gases and states
  outside the provisional constant-cp temperature envelope.
- **Trustworthy convergence and failure evidence.** Require endwall, row and
  quasi-normal convergence; strengthen coupled field convergence; check mass,
  Euler work, energy and entropy after solving. Reject negative smoothed loss.
  Expose a task-owned endwall iteration budget (default 200) so the three-stage
  reference converges without relaxing its 1e-8 inner tolerance.
  Preserve structured failures through the environment and retain all fallback
  attempts. Optional mixing uses integrated conservation checks.
- **Reproducible campaigns.** Archive the pre-change v5 working copy; keep v5
  goldens and historical result files unchanged. New campaigns carry source/data
  hashes, effective inputs and runtime provenance in separate exclusive paths.
  Pin validation dependencies; add reliability regression tests and a synthetic
  axial/radial resolution runner. See `docs/throughflow_domain.md` for the
  admitted scope and the validation gates that remain open.
- **Throughflow reliability and validation plan**
  (`docs/throughflow_reliability_plan.md`): prioritized audit findings,
  physical and numerical acceptance gates, generated-design checks, and
  staged expansion of the supported compressor domain.
- **Start-up homotopy in the throughflow solver.** When a point fails or does
  not converge from the cold start, it is solved again with the row losses
  ramped from 0 to 1, each step starting from the last one's stream surfaces
  (`docs/throughflow_solver.md`). Points that converge cold give identical
  numbers; on the validation cases 17 more measured points converge.
- **Carter's rule for multiple-circular-arc rows.** Their design deviation
  is now the NASA Lewis design code's Carter rule
  (`correlations.nasa_lewis`) instead of Lieblein's circular-arc rule; this
  moves the numbers of every MCA design (`docs/compressor_correlations.md`).
- **Spanwise mixing (Gallimore, 1986), off by default**:
  `sm_throughflow.solver.mixing` and `correlations.spanwise_mixing`, enabled
  only through the experimental `SlcAungierSimulator.mixing_model` switch.
- **Simulator `slc_aungier_experimental_v5`** with the v2 contracts
  (`throughflow_design_v2`, `throughflow_task_v2`) for axial compressors. It
  runs on the package's own streamline-curvature solver with Aungier's (2003)
  cascade correlations (design and off-design incidence, deviation and loss,
  Mach number and choke limits, shock loss), tip-clearance and shroud-seal
  leakage, wake and end-wall blockage, and his end-wall boundary-layer
  analysis. A task may list several operating points. The design rules keep
  designs inside the range of the cascade data. The score stays disabled. Blade throats, which set
  the choke limit on incidence, come from the constructed blade sections
  (NACA 65, C.4 and double circular arc on their camberlines). For
  double-circular-arc rows, the expansion angle of the shock-loss model also
  comes from the constructed sections, and on a parabolic-arc or NACA
  meanline the double-circular-arc thickness is laid along that meanline
  (before, the section was always built on a circular arc). Crouse's
  multiple-circular-arc section (`mca` profile, `multiple_circular_arc`
  camberline, with `transition_point`, `turning_rate_ratio` and
  `max_thickness_location`) represents the NASA Lewis transonic blading.

### Fixed

- **Multiple-circular-arc suction surface.** Its arcs met the edge circles
  from outside the section (the tangency assumed every circle on the arc's
  left), so near the leading edge the suction surface dipped below the
  meanline. The throat is unchanged; the shock model's expansion angle falls
  by 0.7 to 1.5 deg and now matches the printed PHISS where the front is
  cambered. Every MCA design's numbers move (`docs/validation_plan.md`).
- **Start-up homotopy steps adapt.** A loss step that fails is halved and
  retried (down to 1/64) instead of ending the fallback; with no failed step
  the sequence is the former 0, 0.25, 0.5, 0.75, 1, so no point that
  converged before changes. Some points inside an otherwise solved range now
  converge (`docs/validation_report.md`).

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
- `v1.4.4-sm.2` also releases a compressor stator's flow at its metal angle
  plus deviation (before, the deviation never reached the flow). The
  Mattingly candidate case, which has no inlet metal angles, now chokes; its
  two tests are expected failures. Investigating it showed that turbo-design's
  compressor solve does not conserve energy across a stator (see
  `docs/compressor_validation.md`), so the environment will move to its own
  streamline-curvature solver.
