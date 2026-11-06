"""Keep axial resolution, initialization and effort studies explicitly separate."""
import argparse
import hashlib
import json
from pathlib import Path

from validation.campaign import ROOT, create_campaign, write_json_new
from sm_throughflow.provenance import runtime_identity


def main(paths):
    identity=runtime_identity()
    evidence,studies={},[]
    for path in paths:
        manifest=json.loads((path/'manifest.json').read_text())
        if manifest['runtime']['source_sha256']!=identity['source_sha256']:
            raise ValueError('Use the matching archived source')
        if hashlib.sha256((path/'source.zip').read_bytes()).hexdigest()!=manifest['archive_sha256']:
            raise ValueError('Archive checksum mismatch')
        jobs={j['id']:j for j in json.loads((path/'jobs.json').read_text())}
        records={p.stem:json.loads(p.read_text()) for p in (path/'results').glob('*.json')}
        if len(jobs)!=8 or set(jobs)!=set(records):raise ValueError('All eight requested outcomes required')
        evidence.update({p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in path.rglob('*.json')})
        rows=[]
        for name,r in sorted(records.items()):
            d=r['diagnostics'];c=d.get('convergence',d)
            anchor=records[r['reference_id']+'__axial_1']
            successful=next((a for a in reversed(c.get('attempts',[])) if a['converged']),{})
            rows.append(dict(id=name,representation=r['representation'],subdivisions=r['value'],
                budget=jobs[name]['task']['numerics']['max_iterations'],classification=r['classification'],
                seed_id=r['seed_id'],requested_initialization=r['initialization'],
                successful_initialization=successful.get('initialization'),metrics=r['metrics'],
                delta_from_coarse={k:v-anchor['metrics'][k] for k,v in r['metrics'].items() if k in anchor['metrics']},
                accepted_iterations=c.get('iterations'),effort=c.get('effort'),
                attempts=c.get('attempts',[]),release_evidence=False))
        studies.append(dict(campaign=path.name,selection=manifest['selection'],rows=rows))
    output=create_campaign(purpose='v11_axial_resolution_and_effort_analysis',selection=dict(
        inputs=[p.name for p in paths],qualified=False,release_evidence=False))
    write_json_new(output/'input_evidence_sha256.json',evidence)
    write_json_new(output/'summary.json',dict(studies=studies,qualified=False,
        limitation='Low-level interpolated starts and different effort budgets; not a production cold-start or equal-effort comparison'))
    print(output,flush=True)
    for study in studies:
        for r in study['rows']:
            print(r['budget'],r['id'],r['classification'],r['metrics'].get('stage_pr'),r['metrics'].get('stage_eta'),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('campaigns',nargs='+',type=Path)
    main([p.resolve() for p in parser.parse_args().campaigns])
