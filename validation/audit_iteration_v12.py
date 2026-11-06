"""Freeze the final v12 source, completed evidence, test logs and protection audit."""
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from validation.campaign import ROOT, create_campaign, write_json_new
from sm_throughflow.provenance import runtime_identity

CAMPAIGNS=dict(
    matched='20261104T225400132975Z_slc_aungier_experimental_v12',
    wall='20261104T225410435085Z_slc_aungier_experimental_v12',
    axial='20261104T225452065445Z_slc_aungier_experimental_v12',
    production='20261104T225503343516Z_slc_aungier_experimental_v12',
    comparison='20261104T225803330970Z_slc_aungier_experimental_v12',
    axial_comparison='20261104T225727068868Z_slc_aungier_experimental_v12')
SOURCE='b456b469028d7aeac6ff952c717ef92080539c4a28602ae501c74fae36ffff06'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert runtime_identity()['source_sha256']==SOURCE
    test_log=(ROOT/'tmp/v12_final_tests.log').read_text()
    assert re.search(r'250 passed, 1 skipped in [0-9.]+s',test_log)
    assert re.search(r'1 passed in [0-9.]+s',(ROOT/'tmp/v12_final_lazy_import.log').read_text())
    historical=json.loads((ROOT/'validation/campaigns/20261104_phase01_baseline/manifest.json').read_text())['files']
    protected={k:v for k,v in historical.items() if k.startswith((
        'validation/cases/','validation/results/','validation/reports/','validation/studies/results/'))}
    assert len(protected)==811 and all(sha(ROOT/k)==v for k,v in protected.items())
    main_path=ROOT/'validation/campaigns'/CAMPAIGNS['matched']
    m=json.loads((main_path/'manifest.json').read_text())
    baseline=m['selection']['baseline_evidence_sha256']
    assert len(baseline)==114 and all(sha(ROOT/k)==v for k,v in baseline.items())
    assert sha(ROOT/'validation/phase3_protocol.json')=='79e7b017db12bcd0acd75505f8d4755151bbe1d13b39afdb8f94beb6f721241a'
    evidence={}
    for role,name in CAMPAIGNS.items():
        path=ROOT/'validation/campaigns'/name
        manifest=json.loads((path/'manifest.json').read_text())
        assert manifest['runtime']['source_sha256']==SOURCE
        assert sha(path/'source.zip')==manifest['archive_sha256']
        if role in ('matched','wall','axial','production'):
            jobs={j['id'] for j in json.loads((path/'jobs.json').read_text())}
            results={p.stem for p in (path/'results').glob('*.json')}
            assert jobs==results and len(jobs)==dict(matched=108,wall=4,axial=8,production=6)[role]
        evidence.update({p.relative_to(ROOT).as_posix():sha(p) for p in path.rglob('*.json')})
    summary=json.loads((ROOT/'validation/campaigns'/CAMPAIGNS['comparison']/'summary.json').read_text())
    assert not summary['qualified']
    assert all(not summary[r]['lost'] and summary[r]['repeat_outcome_equal'] for r in ('projected','original'))
    assert summary['row_comparison']==dict(count=96,closure_values_identical=True,sensitivity_values_identical=True)
    name=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_slc_aungier_experimental_v12'
    output=ROOT/'validation/campaigns'/name
    report=ROOT/'docs/phase3_iteration_v12.md'
    addition='\n## Final frozen evidence and verification\n\n'
    addition+='Production source SHA256: `'+SOURCE+'`.\n\n'
    addition+='| Evidence | Campaign |\n|---|---|\n'
    for role,campaign in CAMPAIGNS.items():
        addition+='| '+role+' | ['+campaign+'](../validation/campaigns/'+campaign+'/manifest.json) |\n'
    addition+='\nFinal audit: ['+name+'](../validation/campaigns/'+name+'/verification.json).\n\n'
    addition+='The full suite passes 250 tests with one import-order skip; that skipped\n'
    addition+='lazy-import test passes in isolation, so all 251 distinct tests are verified.\n'
    addition+='Tests include conservation, deterministic independent-process results,\n'
    addition+='actual 3979 and production grid-8 regressions, nonuniform analytic checks,\n'
    addition+='failed seeds, exhausted budgets and step-construction telemetry. All 811\n'
    addition+='protected historical files and 114 v11 baseline JSON artifacts are unchanged.\n\n'
    addition+='Earlier exploratory v12 campaigns and the first failed test run are retained\n'
    addition+='but are not pooled with this final source. The first run exposed an invalid\n'
    addition+='error-constructor argument on exhausted outer budgets and sandbox temporary\n'
    addition+='directory failures. The former was fixed; the complete suite was rerun with\n'
    addition+='a repository-local temporary directory. All experimental and resolution\n'
    addition+='campaigns were rerun against the final source; their physical states and\n'
    addition+='metrics exactly reproduce the initial numerical implementation. Final logs\n'
    addition+='and superseded diagnostics are distinguished in the audit. No historical\n'
    addition+='result, physical coefficient, experimental target or acceptance gate was rewritten.\n'
    assert '## Final frozen evidence and verification' not in report.read_text()
    with report.open('a',encoding='utf-8') as stream:stream.write(addition)
    create_campaign(output,purpose='v12_final_verification_and_protection_audit',selection=dict(
        campaigns=CAMPAIGNS,distinct_tests_verified=251,qualified=False,release_evidence=False))
    logs=output/'logs';logs.mkdir()
    roles={}
    for path in sorted((ROOT/'tmp').glob('v12*')):
        if path.is_file():
            shutil.copyfile(path,logs/path.name)
            roles[path.name]='final' if path.name.startswith('v12_final_') else 'superseded_or_exploratory'
    # These root documents are outside the normal campaign source archive.
    for filename in ('README.md','CHANGELOG.md'):
        shutil.copyfile(ROOT/filename,output/filename)
    write_json_new(output/'input_evidence_sha256.json',evidence)
    write_json_new(output/'verification.json',dict(source_sha256=SOURCE,
        full_suite=dict(passed=250,skipped=1,log='logs/v12_final_tests.log'),
        isolated_lazy_import=dict(passed=1,log='logs/v12_final_lazy_import.log'),
        distinct_tests_verified=251,historical_files_unchanged=len(protected),
        baseline_v11_json_unchanged=len(baseline),qualified=False,log_roles=roles,
        protocol_unchanged=True,full_campaign_jobs=108,wall_jobs=4,axial_jobs=8,production_jobs=6))
    write_json_new(output/'artifact_sha256.json',{
        p.relative_to(output).as_posix():sha(p) for p in sorted(output.rglob('*')) if p.is_file()})
    print(output,flush=True)


if __name__=='__main__':main()
