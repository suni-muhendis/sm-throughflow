"""Freeze rejected-candidate evidence and prove production/history preservation."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import re
import shutil
import zipfile
from validation.campaign import ROOT,create_campaign,write_json_new
from validation.probe_shock_coupled_v16 import BASELINE
from validation.verify_family_source_v14 import verify


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('matched');p.add_argument('analysis');args=p.parse_args()
    matched,analysis=[ROOT/'validation/campaigns'/n for n in (args.matched,args.analysis)]
    identity=verify(matched);assert verify(BASELINE)==identity
    assert identity['current_source_sha256']=='fbc4d57167f594f98a92dd8765fb63913e4c7da35cfb2ccfc08a0f7a261eb719'
    summary=json.loads((analysis/'comparison.json').read_text())
    assert not summary['screen']['necessary_development_checks_passed']
    assert summary['screen']['lost_converged_ids']==[]
    log=(ROOT/'tmp/v16_tests_final.log').read_text(encoding='utf-8')
    count=re.search(r'(\d+) passed in ([\d.]+)s',log)
    assert count and int(count[1])==40 and 'FAILED ' not in log
    historical=json.loads((ROOT/'validation/campaigns/20261104_phase01_baseline/manifest.json').read_text())['files']
    protected={k:v for k,v in historical.items() if k.startswith(
        ('validation/cases/','validation/results/','validation/reports/','validation/studies/results/'))}
    assert len(protected)==811 and all(sha(ROOT/k)==v for k,v in protected.items())
    assert sha(ROOT/'validation/phase3_protocol.json')=='79e7b017db12bcd0acd75505f8d4755151bbe1d13b39afdb8f94beb6f721241a'
    with zipfile.ZipFile(BASELINE/'source.zip') as archive:
        unchanged=[n for n in archive.namelist() if n.startswith(('src/','tests/','validation/cases/'))]
        assert all(archive.read(n)==(ROOT/n).read_bytes() for n in unchanged)
    assert json.loads((BASELINE/'jobs.json').read_text())==json.loads((matched/'jobs.json').read_text())
    assert len(list((matched/'results').glob('*.json')))==108
    for name,count_expected in [('rows.json',96),('row_sensitivity.json',6)]:
        assert len(json.loads((matched/name).read_text()))==count_expected
    prior=ROOT/'validation/campaigns/20261105T111830553561Z_slc_aungier_experimental_v15'
    metric_changes=[]
    for path in (matched/'results').glob('*.json'):
        a=json.loads(path.read_text());b=json.loads((prior/'results'/path.name).read_text())
        assert all(a[k]==b[k] for k in ('converged','classification'))
        assert set(a['metrics'])==set(b['metrics'])
        for k,value in a['metrics'].items():
            if value!=b['metrics'][k]:
                metric_changes.append(dict(id=path.stem,metric=k,absolute_change=abs(value-b['metrics'][k])))
    max_change=max((r['absolute_change'] for r in metric_changes),default=0.)
    inputs={}
    names=[BASELINE.name,args.matched,args.analysis,
        '20261105T105832187471Z_slc_aungier_experimental_v15',
        '20261105T110934330514Z_slc_aungier_experimental_v15',
        '20261105T111232905801Z_slc_aungier_experimental_v15',prior.name,
        '20261105T112208326711Z_slc_aungier_experimental_v15']
    for name in names:
        folder=ROOT/'validation/campaigns'/name;m=json.loads((folder/'manifest.json').read_text())
        assert sha(folder/'source.zip')==m['archive_sha256']
        with zipfile.ZipFile(folder/'source.zip') as archive:
            assert set(archive.namelist())==set(m['files'])
            assert all(hashlib.sha256(archive.read(n)).hexdigest()==h for n,h in m['files'].items())
        inputs.update({p.relative_to(ROOT).as_posix():sha(p) for p in folder.rglob('*') if p.is_file()})
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_slc_aungier_experimental_v15'
    report=ROOT/'docs/phase3_candidate_v16.md';body=report.read_text(encoding='utf-8')
    assert '## Final evidence' not in body
    body+=f'''\n## Final evidence\n\nThe final targeted suite passes **40 tests** in {float(count[2]):.2f} seconds.\nThis is a focused regression run, not a rerun of the entire 290-test v15 suite.\nThe failed first oracle test and successful reruns are archived separately.\n\n- [Final 108-job candidate campaign](../validation/campaigns/{args.matched}/manifest.json).\n- [Full paired analysis, failures and row results](../validation/campaigns/{args.analysis}/comparison.json).\n- [Final frozen audit and test logs](../validation/campaigns/{stamp}/verification.json).\n\n![Measured versus v15 and rejected candidate efficiencies](../validation/campaigns/{args.analysis}/family_efficiency.png)\n\nThe audit checks 811 protected historical files, the frozen protocol, all\npre-existing v15 tests (including historical goldens), source archives and\nidentical experiment inputs. The final diagnostic/sonic-endpoint correction\nleaves all 108 candidate classifications unchanged; {len(metric_changes)} scalar performance\nvalues differ, with maximum absolute change {max_change:.6g}. They are not\ncalled bitwise-identical reruns. The final campaign's internal repeats are\nbitwise identical. Production has no changed files.\n\nProduction SHA256: `{identity['current_source_sha256']}`.\n'''
    report.write_text(body,encoding='utf-8',newline='\r\n')
    out=create_campaign(ROOT/'validation/campaigns'/stamp,purpose='v16_rejected_candidate_final_audit',selection=dict(
        candidate=args.matched,analysis=args.analysis,production_unchanged=True,
        simulator_promoted=False,qualified=False,tests_verified=40))
    (out/'logs').mkdir();(out/'references').mkdir()
    for path in sorted((ROOT/'tmp').glob('v16*.log')):shutil.copyfile(path,out/'logs'/path.name)
    for name in ('README.md','CHANGELOG.md'):shutil.copyfile(ROOT/name,out/name)
    references=[]
    for filename,url in [
        ('schobeiri1997.pdf','https://doi.org/10.1155/S1023621X9700016X'),
        ('nasa_tm79280.pdf','https://ntrs.nasa.gov/api/citations/19800002791/downloads/19800002791.pdf'),
        ('v15_tnd7345.pdf','https://ntrs.nasa.gov/api/citations/19740009588/downloads/19740009588.pdf')]:
        path=ROOT/'tmp'/filename;shutil.copyfile(path,out/'references'/filename)
        references.append(dict(file=filename,url=url,sha256=sha(path)))
    write_json_new(out/'reference_sources.json',references)
    write_json_new(out/'input_evidence_sha256.json',inputs)
    write_json_new(out/'verification.json',dict(source=identity,changed_production_files=[],
        tests=dict(passed=40,seconds=float(count[2]),full_suite=False),historical_files_unchanged=811,
        preexisting_v15_source_tests_data_unchanged=len(unchanged),protocol_unchanged=True,
        matched_jobs=108,row_closures=96,row_sensitivities=6,input_jobs_identical=True,
        candidate_classifications_identical_to_first_full_run=True,
        candidate_metric_changes_since_first_full_run=metric_changes,
        simulator_promoted=False,qualified=False,comparison=summary))
    write_json_new(out/'artifact_sha256.json',{p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()})
    print(out,flush=True)


if __name__=='__main__':main()
