"""Freeze v13 verification without rewriting old campaigns or hiding failed comparisons."""
from datetime import datetime, timezone
import hashlib
import json
import re
import shutil

from validation.campaign import ROOT, create_campaign, write_json_new
from validation.verify_family_source_v13 import verify
from sm_throughflow.provenance import runtime_identity

MATCHED='20261104T232522087684Z_slc_aungier_experimental_v13'
ANALYSIS='20261104T233526128041Z_slc_aungier_experimental_v13'
BASELINE='20261104T225400132975Z_slc_aungier_experimental_v12'
SOURCE='4863be0b501b6c84e11a5f096a9937617447daf8031044b001ccfa2d9f62ccc5'
PROBES=['20261104T230545829386Z_slc_aungier_experimental_v12',
        '20261104T230916451235Z_slc_aungier_experimental_v12',
        '20261104T231844330158Z_slc_aungier_experimental_v12']


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert runtime_identity()['source_sha256']==SOURCE
    log=(ROOT/'tmp/v13_final_tests.log').read_text()
    assert re.search(r'256 passed, 1 skipped in [0-9.]+s',log)
    assert re.search(r'1 passed in [0-9.]+s',(ROOT/'tmp/v13_final_lazy_import.log').read_text())
    campaign=ROOT/'validation/campaigns'/MATCHED
    source_comparison=verify(campaign)
    jobs={j['id'] for j in json.loads((campaign/'jobs.json').read_text())}
    assert len(jobs)==108 and jobs=={p.stem for p in (campaign/'results').glob('*.json')}
    assert len(json.loads((campaign/'rows.json').read_text()))==96
    assert len(json.loads((campaign/'row_sensitivity.json').read_text()))==6
    historical=json.loads((ROOT/'validation/campaigns/20261104_phase01_baseline/manifest.json').read_text())['files']
    protected={k:v for k,v in historical.items() if k.startswith((
        'validation/cases/','validation/results/','validation/reports/','validation/studies/results/'))}
    assert len(protected)==811 and all(sha(ROOT/k)==v for k,v in protected.items())
    baseline=json.loads((campaign/'manifest.json').read_text())['selection']['baseline_evidence_sha256']
    assert len(baseline)==114 and all(sha(ROOT/k)==v for k,v in baseline.items())
    assert sha(ROOT/'validation/phase3_protocol.json')=='79e7b017db12bcd0acd75505f8d4755151bbe1d13b39afdb8f94beb6f721241a'
    analysis=ROOT/'validation/campaigns'/ANALYSIS
    summary=json.loads((analysis/'summary.json').read_text())
    assert not summary['qualified'] and not summary['all_four_family_directions_agree']
    assert summary['original']['counts']['converged']==34 and summary['projected']['counts']['converged']==40
    assert summary['original']['lost']==['original__nasa_stage53_100_2993']
    assert not summary['projected']['lost']
    assert all(summary[r]['repeat_converged'] and summary[r]['repeat_bitwise_equal'] for r in ('original','projected'))
    evidence={}
    for name in [BASELINE,MATCHED,ANALYSIS,*PROBES]:
        path=ROOT/'validation/campaigns'/name
        m=json.loads((path/'manifest.json').read_text())
        assert sha(path/'source.zip')==m['archive_sha256']
        evidence.update({p.relative_to(ROOT).as_posix():sha(p) for p in path.rglob('*.json')})
    evidence[(analysis/'family_efficiency.png').relative_to(ROOT).as_posix()]=sha(analysis/'family_efficiency.png')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_slc_aungier_experimental_v13'
    output=ROOT/'validation/campaigns'/stamp
    report=ROOT/'docs/phase3_family_v13.md'
    addition='\n## Frozen evidence and verification\n\n'
    addition+='| Evidence | Campaign |\n|---|---|\n'
    for role,name in [('v12 baseline',BASELINE),('108 matched jobs + 96 row closures + 6 sensitivities',MATCHED),
                      ('Final analysis',ANALYSIS),('Final audit',stamp),*[(f'Diagnostic probe {i+1}',n) for i,n in enumerate(PROBES)]]:
        addition+=f'| {role} | [{name}](../validation/campaigns/{name}/manifest.json) |\n'
    addition+='\n![Matched family efficiencies](../validation/campaigns/'+ANALYSIS+'/family_efficiency.png)\n\n'
    addition+='The complete suite passes **256 tests with one import-order skip**. The\n'
    addition+='skipped lazy-import test passes in isolation: **257 distinct tests verified**.\n'
    addition+='This includes the previously recovered Stage 35 90% point and both original\n'
    addition+='and projected eightfold-grid regressions at unchanged tolerances. Six new\n'
    addition+='tests cover fixed-Mach incidence response in both frames, tangent-entry\n'
    addition+='equivalence, conical projection, the compression flag, subsonic zero shock,\n'
    addition+='independent analytic circle geometry and malformed input. Historical\n'
    addition+='v5-v12 goldens, all 811 protected historical files, 114 v12 baseline JSON\n'
    addition+='artifacts and the frozen protocol checksum are unchanged.\n\n'
    addition+='The numerical campaign records production SHA256 `'+source_comparison['campaign_source_sha256']+'`.\n'
    addition+='Final source SHA256 is `'+SOURCE+'`. The only intervening package\n'
    addition+='change corrects the PHISS definition in a docstring. An exact allowlisted\n'
    addition+='text diff and a docstring-stripped AST comparison verify identical executable\n'
    addition+='source; every other package file is byte-identical. Results retain their\n'
    addition+='original source identity and were not relabeled. The complete final test\n'
    addition+='suite runs against the final source. See `source_comparison.json` in the audit.\n\n'
    addition+='The initial v13 campaign `20261104T232255932514Z_slc_aungier_experimental_v13`\n'
    addition+='had a stale schema literal and is superseded, not physical evidence. The\n'
    addition+='initial full tests also exposed an inaccessible default temporary directory;\n'
    addition+='the final complete run uses a repository-local pytest directory. All initial\n'
    addition+='and final logs remain distinguished in the audit. The intermediate analysis\n'
    addition+='`20261104T233331876943Z_slc_aungier_experimental_v13` is superseded by the\n'
    addition+='final analysis above. No commit or publication is part of this iteration.\n'
    assert '## Frozen evidence and verification' not in report.read_text(encoding='utf-8')
    with report.open('a',encoding='utf-8',newline='\n') as f:f.write(addition)
    create_campaign(output,purpose='v13_final_family_verification',selection=dict(
        matched=MATCHED,analysis=ANALYSIS,baseline=BASELINE,qualified=False,distinct_tests_verified=257))
    logs=output/'logs';logs.mkdir()
    roles={}
    for p in sorted((ROOT/'tmp').glob('v13*.log')):
        shutil.copyfile(p,logs/p.name)
        roles[p.name]='final' if p.name.startswith('v13_final_') else 'diagnostic_or_superseded'
    for name in ('README.md','CHANGELOG.md'):shutil.copyfile(ROOT/name,output/name)
    write_json_new(output/'input_evidence_sha256.json',evidence)
    write_json_new(output/'source_comparison.json',source_comparison)
    write_json_new(output/'verification.json',dict(source_sha256=SOURCE,full_suite=dict(passed=256,skipped=1),
        isolated_import_passed=1,distinct_tests_verified=257,historical_files_unchanged=811,
        baseline_v12_json_unchanged=114,protocol_unchanged=True,matched_jobs=108,row_closures=96,row_sensitivities=6,
        total_converged=74,baseline_converged=75,lost=summary['original']['lost'],
        family_efficiency_gate_passed=False,qualified=False,log_roles=roles))
    write_json_new(output/'artifact_sha256.json',{p.relative_to(output).as_posix():sha(p)
        for p in sorted(output.rglob('*')) if p.is_file()})
    print(output,flush=True)


if __name__=='__main__':main()
