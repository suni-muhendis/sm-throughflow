"""Freeze v15 verification without rewriting historical experiments or goldens."""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import re
import shutil
import zipfile

from validation.campaign import ROOT, create_campaign, write_json_new
from validation.compare_family_v15 import BASELINE
from validation.report_family_v15 import PROBES
from validation.verify_family_source_v14 import verify


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def references(source):
    result = {}
    for node in ast.parse(source).body:
        if not isinstance(node, ast.Assign): continue
        for target in node.targets:
            if not isinstance(target, ast.Name): continue
            match = re.search(r'^GOLDEN.*_V(\d+)$', target.id)
            if match and int(match[1]) <= 14:
                result[target.id] = ast.dump(node.value)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('matched'); p.add_argument('analysis'); args=p.parse_args()
    matched, analysis = [ROOT/'validation/campaigns'/name for name in (args.matched,args.analysis)]
    identity = verify(matched)
    log = (ROOT/'tmp/v15_full_tests.log').read_text(encoding='utf-8')
    count = re.search(r'(\d+) passed, (\d+) skipped in ([\d.]+)s',log)
    assert count and 'FAILED ' not in log
    passed, skipped, seconds = int(count[1]), int(count[2]), float(count[3])
    assert skipped == 1
    entry = (ROOT/'tmp/v15_entry_tests.log').read_text(encoding='utf-8')
    assert '5 passed' in entry and 'skipped' not in entry
    manifest = json.loads((matched/'manifest.json').read_text(encoding='utf-8'))
    baseline = manifest['selection']['baseline_evidence_sha256']
    assert len(baseline)==114 and all(sha(ROOT/k)==v for k,v in baseline.items())
    historical = json.loads((ROOT/'validation/campaigns/20261104_phase01_baseline/manifest.json').read_text(encoding='utf-8'))['files']
    protected = {k:v for k,v in historical.items() if k.startswith(
        ('validation/cases/','validation/results/','validation/reports/','validation/studies/results/'))}
    assert len(protected)==811 and all(sha(ROOT/k)==v for k,v in protected.items())
    assert sha(ROOT/'validation/phase3_protocol.json')=='79e7b017db12bcd0acd75505f8d4755151bbe1d13b39afdb8f94beb6f721241a'
    prior_audit = ROOT/'validation/campaigns/20261105T091815599857Z_slc_aungier_experimental_v14'
    with zipfile.ZipFile(prior_audit/'source.zip') as archive:
        for name in ('tests/test_throughflow_env.py','tests/test_solver_mattingly.py'):
            assert references(archive.read(name).decode('utf-8'))==references((ROOT/name).read_text(encoding='utf-8'))
        changed = [n for n in archive.namelist() if n.startswith('src/') and n.endswith('.py')
                   and archive.read(n)!=(ROOT/n).read_bytes()]
    assert set(changed)=={'src/sm_throughflow/contracts.py','src/sm_throughflow/correlations/nasa_lewis.py',
                          'src/sm_throughflow/solver/aungier_row.py'}
    jobs = json.loads((matched/'jobs.json').read_text(encoding='utf-8'))
    prior_jobs = {j['id']:j for j in json.loads((BASELINE/'jobs.json').read_text(encoding='utf-8'))}
    assert len(jobs)==108 and {j['id'] for j in jobs}=={p.stem for p in (matched/'results').glob('*.json')}
    for j in jobs:
        prior = prior_jobs[j['id']]
        assert j['design']==prior['design'] and j['task']==dict(prior['task'],simulator_version=j['task']['simulator_version'])
    assert len(json.loads((matched/'rows.json').read_text(encoding='utf-8')))==96
    assert len(json.loads((matched/'row_sensitivity.json').read_text(encoding='utf-8')))==6
    summary = json.loads((analysis/'summary.json').read_text(encoding='utf-8'))
    assert not summary['qualified'] and not summary['training_design_ranking_qualified']
    assert all(summary[r]['repeat_bitwise_equal'] for r in ('original','projected'))
    inputs = {}
    for folder in [BASELINE,prior_audit,matched,analysis,*[ROOT/'validation/campaigns'/name for name in PROBES]]:
        m = json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
        assert sha(folder/'source.zip')==m['archive_sha256']
        inputs.update({p.relative_to(ROOT).as_posix():sha(p) for p in folder.rglob('*.json')})
    reference = ROOT/'tmp/v15_tnd7345.pdf'
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_slc_aungier_experimental_v15'
    report = ROOT/'docs/phase3_family_v15.md'
    assert '## Final frozen verification' not in report.read_text(encoding='utf-8')
    with report.open('a',encoding='utf-8') as stream:
        stream.write(f'\n## Final frozen verification\n\nThe full suite passes **{passed} tests with one import-order skip** in\n'
            f'{seconds:.2f} seconds. The entry-point module passes all five tests in a\n'
            f'fresh process, including that skipped check: **{passed+1} distinct tests verified**.\n'
            'This includes 18 new equivalent-camber tests, Stage 53 repeated convergence,\n'
            'Stage 35 fine-grid/90% regressions, conservation and disabled-score checks.\n\n'
            'The audit verifies 811 protected historical files, 114 v14 baseline JSON\n'
            'artifacts, the frozen protocol and all v5–v14 golden assignments unchanged.\n'
            'All 108 design/task pairs differ from v14 only by simulator version.\n'
            'The simulation campaign and final production package are byte-identical.\n\n'
            f'Production SHA256: `{identity["current_source_sha256"]}`.\n\n'
            f'[Frozen audit](../validation/campaigns/{stamp}/manifest.json) includes\n'
            'test logs, input hashes, original NASA source PDF and source archive.\n'
            'The initial focused test run failed because its synthetic MCA fixture\n'
            'omitted mandatory section-shape input; the corrected fixture and passing\n'
            'reruns are retained. No failed run is represented as passed evidence.\n')
    output = create_campaign(ROOT/'validation/campaigns'/stamp,purpose='v15_final_equivalent_camber_verification',
        selection=dict(baseline=BASELINE.name,matched=args.matched,analysis=args.analysis,
                       qualified=False,distinct_tests_verified=passed+1))
    (output/'logs').mkdir(); (output/'references').mkdir()
    for path in sorted((ROOT/'tmp').glob('v15*.log')):
        shutil.copyfile(path,output/'logs'/path.name)
    for name in ('README.md','CHANGELOG.md'):
        shutil.copyfile(ROOT/name,output/name)
    shutil.copyfile(reference,output/'references/NASA_TN_D7345.pdf')
    for name in ('v15_carter_p148.png','v15_carter-151.png','v15_geometry-008.png'):
        shutil.copyfile(ROOT/'tmp'/name,output/'references'/name)
    write_json_new(output/'reference_sources.json',dict(pdf_sha256=sha(reference),
        url='https://ntrs.nasa.gov/api/citations/19740009588/downloads/19740009588.pdf',
        inspected_printed_pages=[4,5,18,144,147],pdf_page_offset=4))
    write_json_new(output/'input_evidence_sha256.json',inputs)
    write_json_new(output/'verification.json',dict(full_suite=dict(passed=passed,skipped=skipped,seconds=seconds),
        distinct_tests_verified=passed+1,isolated_entry_point_passed=5,new_equivalent_camber_tests=18,
        historical_files_unchanged=811,baseline_v14_json_unchanged=114,historical_goldens_unchanged=True,
        protocol_unchanged=True,matched_jobs=108,row_closures=96,row_sensitivities=6,
        source=identity,changed_production_files=changed,comparison=summary,qualified=False))
    write_json_new(output/'artifact_sha256.json',{p.relative_to(output).as_posix():sha(p)
                                               for p in output.rglob('*') if p.is_file()})
    print(output,flush=True)


if __name__=='__main__':
    main()
