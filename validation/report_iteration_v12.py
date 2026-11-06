"""Compare complete frozen axial studies and explicit production startup work."""
import json
import hashlib
from validation.campaign import ROOT, create_campaign, write_json_new
from sm_throughflow.provenance import runtime_identity

V11_SOURCE='81cba25a32cdff525c48bb8ca110d7f7a50b85b11aad6df4e2d5111b04ec5dd2'
PATHS=dict(v11_400='20261104T220809961902Z_slc_aungier_experimental_v11',
           v11_1000='20261104T221411788920Z_slc_aungier_experimental_v11',
           v12_400='20261104T225452065445Z_slc_aungier_experimental_v12',
           v12_production='20261104T225503343516Z_slc_aungier_experimental_v12')


def main():
    evidence,studies={},{}
    for key,name in PATHS.items():
        path=ROOT/'validation/campaigns'/name
        manifest=json.loads((path/'manifest.json').read_text())
        expected=V11_SOURCE if key.startswith('v11') else runtime_identity()['source_sha256']
        assert manifest['runtime']['source_sha256']==expected
        assert hashlib.sha256((path/'source.zip').read_bytes()).hexdigest()==manifest['archive_sha256']
        jobs={j['id']:j for j in json.loads((path/'jobs.json').read_text())}
        results={p.stem:json.loads(p.read_text()) for p in (path/'results').glob('*.json')}
        assert set(jobs)==set(results) and len(jobs)==(6 if key.endswith('production') else 8)
        evidence.update({p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in path.rglob('*.json')})
        rows=[]
        for identifier,r in sorted(results.items()):
            c=r['diagnostics'].get('convergence',r['diagnostics'])
            attempts=c.get('attempts',[])
            successful=next((a for a in reversed(attempts) if a['converged']),{})
            rows.append(dict(id=identifier,representation=r['representation'],converged=r['converged'],
                classification=r['classification'],budget=jobs[identifier]['task']['numerics']['max_iterations'],
                duct_subdivisions=jobs[identifier]['task']['numerics']['duct_subdivisions'],
                wall_subdivisions=jobs[identifier]['task']['numerics']['endwall_subdivisions'],
                metrics=r['metrics'],accepted_iterations=successful.get('iterations'),
                position_residual=successful.get('position_residual'),field_residual=successful.get('field_residual'),
                seed_id=r.get('seed_id'),effort=c.get('effort'),attempts=attempts))
        studies[key]=dict(campaign=name,source_sha256=expected,rows=rows)
    equality={}
    for rep in ('original','projected'):
        a=next(r for r in studies['v12_400']['rows'] if r['representation']==rep and r['duct_subdivisions']==8)
        b=next(r for r in studies['v12_production']['rows'] if r['representation']==rep and r['duct_subdivisions']==8)
        equality[rep]=a['metrics']==b['metrics']
        assert equality[rep] and a['converged'] and b['converged']
        for key,total in b['effort'].items():
            assert total==sum(attempt.get('effort',{}).get(key,0) for attempt in b['attempts'])
    output=create_campaign(purpose='v12_axial_and_production_startup_analysis',selection=dict(
        inputs=PATHS,qualified=False,release_evidence=False))
    write_json_new(output/'input_evidence_sha256.json',evidence)
    write_json_new(output/'summary.json',dict(studies=studies,production_research_metrics_bitwise_equal=equality,
        qualified=False,limitation='Wall discretization and iteration differ by version; 200/400/1000 budgets and startup policies are reported separately.'))
    print(output,flush=True)
    for key,study in studies.items():
        for r in study['rows']:
            print(key,r['id'],r['classification'],r['accepted_iterations'],r['effort'],flush=True)


if __name__=='__main__':main()
