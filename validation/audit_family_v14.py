"""Freeze v14 tests and matched evidence, preserving every historical result."""
import argparse
import ast
from datetime import datetime,timezone
import hashlib
import json
import re
import shutil
import zipfile

from validation.campaign import ROOT,create_campaign,write_json_new
from validation.verify_family_source_v14 import verify

BASELINE='20261104T232522087684Z_slc_aungier_experimental_v13'
V13_AUDIT='20261104T234011745189Z_slc_aungier_experimental_v13'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def references(source):
    out={}
    for node in ast.parse(source).body:
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id.startswith('GOLDEN'):
                    match=re.search(r'_V(\d+)$',target.id)
                    if match and int(match[1])<=13:out[target.id]=ast.dump(node.value)
    return out

def main():
    parser=argparse.ArgumentParser();parser.add_argument('matched');parser.add_argument('analysis');args=parser.parse_args()
    campaign=ROOT/'validation/campaigns'/args.matched
    analysis=ROOT/'validation/campaigns'/args.analysis
    identity=verify(campaign)
    log=(ROOT/'tmp/v14_full_tests.log').read_text(encoding='utf-8')
    counts=re.search(r'(\d+) passed, (\d+) skipped in ([\d.]+)s',log)
    assert counts and 'FAILED ' not in log
    passed,skipped=int(counts[1]),int(counts[2]);assert skipped==1
    entry=(ROOT/'tmp/v14_entry_point.log').read_text(encoding='utf-8')
    assert '5 passed' in entry and 'skipped' not in entry
    assert '7 passed' in (ROOT/'tmp/v14_mattingly.log').read_text(encoding='utf-8')
    manifest=json.loads((campaign/'manifest.json').read_text())
    baseline=manifest['selection']['baseline_evidence_sha256']
    assert len(baseline)==114 and all(sha(ROOT/k)==v for k,v in baseline.items())
    historical=json.loads((ROOT/'validation/campaigns/20261104_phase01_baseline/manifest.json').read_text())['files']
    protected={k:v for k,v in historical.items() if k.startswith(('validation/cases/','validation/results/','validation/reports/','validation/studies/results/'))}
    assert len(protected)==811 and all(sha(ROOT/k)==v for k,v in protected.items())
    assert sha(ROOT/'validation/phase3_protocol.json')=='79e7b017db12bcd0acd75505f8d4755151bbe1d13b39afdb8f94beb6f721241a'
    with zipfile.ZipFile(ROOT/'validation/campaigns'/V13_AUDIT/'source.zip') as archive:
        for name in ('tests/test_throughflow_env.py','tests/test_solver_mattingly.py'):
            assert references(archive.read(name).decode('utf-8'))==references((ROOT/name).read_text(encoding='utf-8'))
    jobs=json.loads((campaign/'jobs.json').read_text())
    old_jobs={j['id']:j for j in json.loads((ROOT/'validation/campaigns'/BASELINE/'jobs.json').read_text())}
    assert len(jobs)==108 and {j['id'] for j in jobs}=={p.stem for p in (campaign/'results').glob('*.json')}
    for j in jobs:
        prior=old_jobs[j['id']];task=dict(prior['task'],simulator_version=j['task']['simulator_version'])
        assert j['design']==prior['design'] and j['task']==task
    assert len(json.loads((campaign/'rows.json').read_text()))==96
    assert len(json.loads((campaign/'row_sensitivity.json').read_text()))==6
    summary=json.loads((analysis/'summary.json').read_text())
    assert not summary['qualified'] and not summary['training_design_ranking_qualified']
    assert all(summary[r]['repeat_bitwise_equal'] for r in ('original','projected'))
    inputs={};research=[]
    folders=[ROOT/'validation/campaigns'/BASELINE,*sorted((ROOT/'validation/campaigns').glob('20261105*'))]
    for path in folders:
        if not (path/'manifest.json').exists():continue
        m=json.loads((path/'manifest.json').read_text());assert sha(path/'source.zip')==m['archive_sha256']
        inputs.update({p.relative_to(ROOT).as_posix():sha(p) for p in path.rglob('*.json')})
        research.append(dict(campaign=path.name,purpose=m['purpose'],has_result=(path/'result.json').exists(),
                             incomplete=path.name=='20261105T082458305188Z_slc_aungier_experimental_v13'))
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_slc_aungier_experimental_v14'
    report=ROOT/'docs/phase3_family_v14.md'
    assert '## Final frozen audit' not in report.read_text(encoding='utf-8')
    with report.open('a',encoding='utf-8') as stream:
        stream.write(f'\n## Final frozen audit\n\nThe full suite passes **{passed} tests with one import-order skip**. The\n'
            f'entry-point module passes all five tests in isolation, including that skip,\n'
            f'for **{passed+1} distinct tests verified**. The seven Mattingly checks were\n'
            'also rerun after adding the explicit v14 reference alias.\n\n'
            'The audit verifies 811 protected historical files, 114 v13 baseline JSON\n'
            'artifacts, all prior golden assignments and the frozen protocol unchanged.\n'
            'All 108 design/task pairs match v13 except the simulator version.\n'
            'The numerical campaign and final production files are byte-identical.\n\n'
            f'Production SHA256: `{identity["current_source_sha256"]}`.\n\n'
            f'[Frozen audit](../validation/campaigns/{stamp}/manifest.json) includes\n'
            'test logs, input hashes, source archive and verification results.\n'
            'The interrupted damped counterfactual and superseded initial test runs\n'
            'remain explicitly distinguished; they are not completed evidence.\n')
    output=create_campaign(ROOT/'validation/campaigns'/stamp,purpose='v14_final_family_verification',selection=dict(
        baseline=BASELINE,matched=args.matched,analysis=args.analysis,qualified=False,distinct_tests_verified=passed+1))
    logs=output/'logs';logs.mkdir()
    for p in sorted((ROOT/'tmp').glob('v14*.log')):shutil.copyfile(p,logs/p.name)
    for name in ('README.md','CHANGELOG.md'):shutil.copyfile(ROOT/name,output/name)
    write_json_new(output/'source_comparison.json',identity)
    write_json_new(output/'input_evidence_sha256.json',inputs)
    write_json_new(output/'research_inventory.json',research)
    write_json_new(output/'verification.json',dict(full_suite=dict(passed=passed,skipped=skipped,seconds=float(counts[3])),
        distinct_tests_verified=passed+1,isolated_entry_point_passed=5,mattingly_recheck_passed=7,
        historical_files_unchanged=811,baseline_v13_json_unchanged=114,historical_goldens_unchanged=True,
        protocol_unchanged=True,matched_jobs=108,row_closures=96,row_sensitivities=6,
        source=identity,comparison=summary,qualified=False))
    write_json_new(output/'artifact_sha256.json',{p.relative_to(output).as_posix():sha(p) for p in output.rglob('*') if p.is_file()})
    print(output,flush=True)

if __name__=='__main__':main()
