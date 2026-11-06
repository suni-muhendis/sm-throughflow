# Validation cases

Geometry of open axial-compressor test cases, transcribed verbatim from their
primary reports (NASA, NACA, GE, P&W) for validating the throughflow simulator.
Nothing here is converted or corrected: each number is as printed, with its
source page, and every doubtful reading is marked with a trailing `?`.

- `TRANSCRIPTION_GUIDE.md`: the rules every transcription followed.
- `cases/<case>/`: one folder per case with the CSV tables, `source.json`
  (report, NTRS id, PDF page and title of every table), `scalars.json`
  (values quoted from the text) and `notes.md` (conventions, gaps, print
  errors found in the reports, and how uncertain cells were resolved).
- `pass_b/<case>/`: independent blind re-readings of the tables without strong
  internal checks (NACA, GE LSRC, UTRC, LSAC, P&W exit-stage geometry).
- `tools/check_lewis_geometry.py`: consistency checks on the NASA Lewis-format
  geometry tables (camber, blade count from solidity, ordering, smoothness,
  text layer). `tools/compare_passes.py`: cell-by-cell comparison of the two
  readings.
- `reports/`: the outputs of those two tools.

Result of the checks: all 47 Lewis-format geometry tables give an integer
blade count to within 0.03 on every row and satisfy KIC - KOC = camber; the
blind re-readings agree with the first reading in every numeric cell except 11
(2 P&W cells already marked doubtful, 9 UTRC dot-matrix cells resolved or
marked in `cases/utrc_isolated_rotor/notes.md`).

The source PDFs are public NASA/NACA reports and are not stored here; each
`source.json` gives the NTRS id.

## Running without overwriting history

The repository provides source-traced case data and validation scripts.
New runs write local artifacts under `validation/campaigns/`. This directory,
the legacy study output directory `validation/studies/results/` and the root
`tmp/` directory are excluded from Git. Historical report
links to campaign directories require those local archives. Comparisons
that verify a frozen simulator version also require that version's source
and runtime.

`python validation/run.py nasa_stage35` creates a fresh campaign containing its
manifest, source archive, patch, results, case outcomes and report. Omit the case
to run all registered cases. `--output validation/campaigns/<new-name>` chooses a
new directory; existing paths are rejected. Do not combine results from different simulator versions.

`python validation/studies/run_all.py admission numerics` does the same for
selected internal studies, recording individual environment inputs and results.
Run `python validation/studies/analyze.py <campaign-directory>` only when that
campaign does not yet have a report; reports are also exclusively created.

`python validation/verify_phase01.py` runs the smaller synthetic resolution study.
The baseline in `campaigns/20261104_phase01_baseline/` captures the complete dirty
working copy before the reliability changes, including existing untracked studies
and historical results. New campaigns are not experimental acceptance by default;
consult their purpose and diagnostics.

`python validation/verify_phase2.py` audits cold and bidirectional continuation,
independent capacity and iteration-budget outcomes, and reconstructs all 39
historical interior holes with their neighbouring successes for current-scope
triage. `--historical-only` omits the synthetic runs. See
[the Phase 2 report](../docs/phase2_offdesign.md).

`validation/run.py` retains every measured-point outcome and path audit. Its upper
flow search returns a classified bracket. An unresolved or numerical boundary
is not used as a choke anchor or for matched-flow normalization. The direct
experimental adapter still bypasses DRC intentionally and labels that fact; it
now uses the same convergence, balance and gas-scope checks as the environment.

## Phase 3 empirical audit

The frozen selection and screens are in `phase3_protocol.json`; the outcome and
limits are in [the Phase 3 report](../docs/phase3_validation.md). These commands
use the repository's own environment and create new campaigns:

```powershell
.venv/Scripts/python -m validation.phase3 --workers 3
.venv/Scripts/python -m validation.phase3_rows
.venv/Scripts/python -m validation.phase3_report <coupled-campaign> <row-campaign>
```

The analysis command requires matplotlib for its standalone diagnostic plots.
The solver dependencies are unchanged. The protocol rejects a production source
hash different from the frozen v8 model; do not silently rerun it on a new model
and mix the results. Analysis checks matching protocols and complete requested
job coverage. Exact source snapshots, inputs and outputs remain in the campaigns.

`phase3_rows.py` conditions the closure on measured inlet and exit meridional
states; it is not an independent Vm prediction. `phase3.py` explicitly transforms
in-row wall contours for research, records displacement/area effects and DRC,
and marks those inputs ineligible for release evidence. Neither path changes
the transcriptions or production admission rules. Holdout metadata inventory
is not holdout validation.

## v9 matched geometry and convergence comparison

Run `.venv/Scripts/python -m validation.compare_geometry_v9 --workers 3`.
This reads the archived 54 v8 jobs without changing point selection, task
budgets or measurements. It runs the identical projected inputs on v9 and a
second set retaining original wall controls, preserving each blade perturbation.
Every outcome is recorded, including out-of-scope research cases and failures.
The same 96 measured-state row closures and six adapter sensitivities are rerun
and compared separately from admission metadata. `--ids <id> ...` is an explicitly
exploratory subset, not the complete comparison. Each invocation creates a new
campaign; old results and `phase3_protocol.json` remain immutable.

See [the v9 report](../docs/phase3_geometry_convergence_v9.md) for the comparison
and unresolved limitations. The old v8 CLI must use its archived source, since
its frozen source-hash requirement remains enforced.

## V10 wall integration and coupled safeguards

Run `.venv/Scripts/python -m validation.compare_convergence_v10 --workers 3`
for all 108 archived v9 jobs and the same 96 measured-state closures. Designs,
measurements and outer budgets are fixed; the declared numerical change is
eight boundary-layer subintervals per blade-row gap plus guarded coupled steps.
`endwall_max_iterations` counts map evaluations per subinterval, including
Jacobian probes. This is not an equal-total-inner-work-budget comparison.

Run `.venv/Scripts/python -m validation.refine_endwall_v10` separately for
16/32-subinterval sensitivity at two original-annulus points. Analyze the complete
runs with `.venv/Scripts/python -m validation.report_convergence_v10 <coupled> <refinement>`.
Every command creates a new campaign. Archived v9/v8 evidence and protocols stay
unchanged; their replay commands require their archived production source.
See [the v10 report](../docs/phase3_convergence_v10.md).

### V11 curvature and stability follow-up

Run `.venv/Scripts/python -m validation.compare_convergence_v11 --workers 3`
for all 108 v10 jobs with unchanged inputs apart from the version. The production
geometry stencil and base damping change; the 200-iteration per-attempt budget
and tolerances do not. Rejected evaluations remain in the recorded effort and
are now exported with the attempted steps.

Run `.venv/Scripts/python -m validation.refine_endwall_v11` for four separate
16/32-subinterval jobs. Analyze with
`.venv/Scripts/python -m validation.report_convergence_v11 <coupled> <wall-refinement>`.
The separate `.venv/Scripts/python -m validation.refine_curvature_v11` study uses
1/2/4/8 duct subdivisions, 400 iterations per attempt and interpolated converged
coarser-grid positions via the low-level solver. It does not change the
production cold-start policy or pool those results with the matched campaign.
`validation.refine_curvature_v11_effort` repeats that separate study at 1000
iterations per attempt, retaining all failures and the original tolerance.
Use `validation.report_axial_v11 <400-step-campaign> <1000-step-campaign>` to
compare resolution and effort without pooling the distinct budgets.

The `probe_curvature_v11` and `probe_refinement_v11` scripts are explicitly
marked research overrides on archived v10 source, not normal v10 evaluations.
See [the v11 report](../docs/phase3_curvature_v11.md).

### V12 duct integration and conditioned iteration

Run `.venv/Scripts/python -m validation.compare_convergence_v12 --workers 3`
for the same 108 frozen v11 jobs and unchanged measured-state row checks.
V12 uses duct wall substeps, an elliptic position update and an accounted
production coarse-grid fallback. Every grid keeps the 200-iteration per-attempt
budget; total effort includes failed starts, seed grids and requested-grid retry.

Run `validation.refine_endwall_v12` for the same four wall-refinement jobs and
`validation.refine_curvature_v12` for the eight 400-budget research continuation
jobs. That low-level research runner bypasses high-level production startup;
its metadata flag `production_cold_start_policy_unchanged` means the **study**
does not override production policy, not that v12 has v11's startup policy.
Run `validation.check_iteration_v12` for explicit production grid-8 checks and
the recovered 3979 point at wall resolutions 1/8/16/32. Analyze complete matched
and wall campaigns with `validation.report_convergence_v12 <coupled> <wall>`.

`report_iteration_v12` and `audit_iteration_v12` reproduce this investigation's
specific frozen evidence comparisons, rather than choosing the newest directory.
Exploratory prototype/capture commands require archived v11 source; they are not
standard released-simulator evidence. See [the v12 report](../docs/phase3_iteration_v12.md)
for source hashes, separate budgets, remaining physical limits and final tests.

## V13 matched family-response investigation

Run `python -m validation.compare_family_v13 --workers 3` under the v13 source,
then `python -m validation.report_family_v13 <campaign-directory-name>`.
The runner repeats all 108 frozen v12 jobs, 96 measured-state row closures and
six adapter sensitivities without altering the old evidence. The report
retains numerical failures, all original/projected outcomes, the three frozen
legacy family comparisons, and four additional aspect-ratio/loading pairs.
See [the v13 report](../docs/phase3_family_v13.md) for the unresolved efficiency
response and the single lost Stage 53 solution. The counterfactual probe
requires its archived v12 source and is not production or acceptance evidence.

## v15 equivalent-camber comparison

Run `python -m validation.compare_family_v15 --workers 3` under the v15 source,
then `python -m validation.report_family_v15 <campaign-directory-name>`.
The 108 design/task pairs match frozen v14 except the simulator version; the
96 row closures and six sensitivities use the unchanged protocol and tables.
`probe_equivalent_camber_v15` requires the archived v14 source and records
research overrides separately; it must not be run as v15 production evidence.
See [the v15 report](../docs/phase3_family_v15.md) for source derivation and the
unresolved efficiency ordering. No experimental qualification is implied.

## Post-v15 candidate investigation

[The candidate report](../docs/phase3_candidate_v16.md) records rejected
conical-geometry and flow-dependent shock hypotheses. `compare_candidate_v16.py`
repeats the frozen v15 jobs with an explicit research override. These are not
normal v15 labels or a v16 simulator release, despite the production version
in their runtime provenance. Use the manifest purpose and research identifier.
`screen_candidate_v16.py` retains reversed family directions and lost/failed
predictions; passing this development screen never grants qualification.

## v16 analytic MCA geometry

Run `python -m validation.compare_geometry_v16 --workers 3` for the exact
108-job v15 cohort, 96 row closures and six sensitivities, with only the
simulator version changed. Run `python -m validation.geometry_response_v16`
to reproduce the old geometric sensitivity defect using archived v15 source.
See [the v16 geometry report](../docs/phase3_geometry_v16.md). Stage 35–38
efficiency ordering remains unresolved; this is not label qualification.

`probe_bow_shock` exercises the unchoked supersonic branch of a separate
research oracle. It deliberately records unsupported choked counterfactuals
for diagnosis; the default oracle rejects them. It omits the other operating
branches, AVDR and viscous interaction and must not replace the production
closure. Earlier `candidate_v16` files refer to rejected pre-v16 research.
