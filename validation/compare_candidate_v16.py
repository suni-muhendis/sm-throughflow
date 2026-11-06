"""Frozen v15 experiment under a rejected research candidate, not a v16 release.

The pilot worsened family ordering. Complete the matched comparison to retain
all outcomes, including Stage 53 and grid regressions. No production changes,
new training labels, tuned coefficients or changed admission rules are made.
"""
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
from validation.campaign import create_campaign,write_json_new
from validation.probe_shock_coupled_v16 import BASELINE,run
from validation.phase3 import PROTOCOL_PATH
from validation.phase3_rows import run_rows
from validation.probe_shock_v16 import override,geometry
from validation.compare_geometry_v9 import summarize
from sm_throughflow.contracts import SIMULATOR_VERSION
from sm_throughflow.provenance import runtime_identity


def main():
    assert SIMULATOR_VERSION=='slc_aungier_experimental_v15'
    expected='fbc4d57167f594f98a92dd8765fb63913e4c7da35cfb2ccfc08a0f7a261eb719'
    assert runtime_identity()['source_sha256']==expected
    jobs=json.loads((BASELINE/'jobs.json').read_text(encoding='utf-8'))
    old={j['id']:json.loads((BASELINE/'results'/(j['id']+'.json')).read_text()) for j in jobs}
    hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in BASELINE.rglob('*.json')}
    out=create_campaign(purpose='v16_rejected_shock_candidate_matched_comparison',selection=dict(
        baseline=BASELINE.name,candidate_id='schobeiri_meanline_mca_nodewise',jobs=len(jobs),
        prototype=True,release_evidence=False,production_unchanged=True,
        limitation='MCA-only research generalization; nodewise shock without conservative sonic-cell integration; pilot failed family ordering'))
    write_json_new(out/'jobs.json',jobs);print(out,flush=True)
    results=[]
    with ProcessPoolExecutor(max_workers=3) as pool:
        for f in as_completed([pool.submit(run,j) for j in jobs]):
            result=f.result();write_json_new(out/'results'/(result['id']+'.json'),result);results.append(result)
            print(result['id'],result['classification'],round(result['elapsed_seconds'],1),flush=True)
    write_json_new(out/'comparison.json',summarize(sorted(results,key=lambda r:r['id']),old))
    # Full row cohort: use the same closure override but obtain each design's
    # geometry on row assembly, rather than retaining the previous machine.
    import validation.phase3_rows as rows
    original=rows.row_model
    def replacement(design,*args,**kwargs):
        model=original(design,*args,**kwargs)
        model._research_curves=geometry(design)
        return model
    from sm_throughflow.solver.aungier_row import AungierCompressorRow
    original_call=AungierCompressorRow.__call__
    def call(self,*args,**kwargs):
        with override(self._research_curves,True,None):
            return original_call(self,*args,**kwargs)
    rows.row_model=replacement;AungierCompressorRow.__call__=call
    try:
        data,sens=run_rows(json.loads(PROTOCOL_PATH.read_text()))
    finally:
        rows.row_model=original;AungierCompressorRow.__call__=original_call
    write_json_new(out/'rows.json',data);write_json_new(out/'row_sensitivity.json',sens)
    assert runtime_identity()['source_sha256']==expected
    from pathlib import Path
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    write_json_new(out/'integrity.json',dict(production_sha256=expected,baseline_json_unchanged=True,
        input_jobs_identical=jobs==json.loads((BASELINE/'jobs.json').read_text())))
    print('COMPLETE',out,flush=True)


if __name__=='__main__':main()
