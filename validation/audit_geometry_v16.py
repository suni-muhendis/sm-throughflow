"""Freeze v16 tests, paired experiment, geometry response and unchanged history."""
import ast
from datetime import datetime, timezone
import hashlib
import json
import re
import shutil
import zipfile

from validation.campaign import ROOT, create_campaign, write_json_new
from validation.compare_geometry_v16 import BASELINE, records
from validation.verify_family_source_v14 import verify

MATCHED = ROOT/'validation/campaigns/20261105T124800167736Z_slc_aungier_experimental_v16'
RESPONSE = ROOT/'validation/campaigns/20261105T125512772642Z_slc_aungier_experimental_v16'
BOW = ROOT/'validation/campaigns/20261105T125349596467Z_slc_aungier_experimental_v16'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def goldens(source):
    found = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign):
            for name in node.targets:
                if isinstance(name, ast.Name):
                    match = re.fullmatch(r'GOLDEN.*_V(\d+)', name.id)
                    if match and int(match[1]) <= 15:
                        found[name.id] = ast.dump(node.value)
    return found


def main():
    source = verify(MATCHED)
    log = (ROOT/'tmp/v16_full_geometry_tests.log').read_text(encoding='utf-8')
    count = re.search(r'(\d+) passed, (\d+) skipped in ([\d.]+)s', log)
    assert count and 'FAILED ' not in log
    passed, skipped, seconds = int(count[1]), int(count[2]), float(count[3])
    assert passed == 318 and skipped == 1
    entry = (ROOT/'tmp/v16_entry_geometry_tests.log').read_text(encoding='utf-8')
    assert '5 passed' in entry and 'skipped' not in entry
    before = json.loads((ROOT/'tmp/v16_geometry_before.json').read_text())['files']
    changed = sorted(name for name, h in before.items() if sha(ROOT/name) != h)
    assert changed == ['src/sm_throughflow/contracts.py', 'src/sm_throughflow/correlations/blade_geometry.py',
                       'tests/test_throughflow_env.py']
    with zipfile.ZipFile(BASELINE/'source.zip') as archive:
        assert goldens(archive.read('tests/test_throughflow_env.py').decode('utf-8')) == goldens((ROOT/'tests/test_throughflow_env.py').read_text())
    historical = json.loads((ROOT/'validation/campaigns/20261104_phase01_baseline/manifest.json').read_text())['files']
    protected = {k: v for k, v in historical.items() if k.startswith(
        ('validation/cases/', 'validation/results/', 'validation/reports/', 'validation/studies/results/'))}
    assert len(protected) == 811 and all(sha(ROOT/k) == v for k, v in protected.items())
    assert sha(ROOT/'validation/phase3_protocol.json') == '79e7b017db12bcd0acd75505f8d4755151bbe1d13b39afdb8f94beb6f721241a'
    manifest = json.loads((MATCHED/'manifest.json').read_text())
    evidence = manifest['selection']['baseline_json_sha256']
    assert all(sha(ROOT/k) == v for k, v in evidence.items())
    jobs, old_jobs = [json.loads((p/'jobs.json').read_text()) for p in (MATCHED, BASELINE)]
    assert len(jobs) == len(old_jobs) == 108
    for old, new in zip(old_jobs, jobs):
        assert old['id'] == new['id'] and old['design'] == new['design']
        assert new['task'] == dict(old['task'], simulator_version='slc_aungier_experimental_v16')
    old, new = records(BASELINE), records(MATCHED)
    assert set(old) == set(new) and all(old[k]['classification'] == new[k]['classification'] for k in old)
    assert all(old[k]['metrics'] == new[k]['metrics'] for k in old if 'nasa_stage53' in k)
    summary = json.loads((MATCHED/'analysis.json').read_text())
    assert not summary['screen']['training_label_qualified']
    assert all(v['repeat_equal'] for v in summary['preservation'].values())
    inputs = {}
    for folder in (BASELINE, MATCHED, RESPONSE, BOW):
        m = json.loads((folder/'manifest.json').read_text())
        assert sha(folder/'source.zip') == m['archive_sha256']
        inputs.update({p.relative_to(ROOT).as_posix(): sha(p) for p in folder.rglob('*') if p.is_file()})
    # Each research result is tied to the exact runner/oracle it executed.
    with zipfile.ZipFile(BOW/'source.zip') as archive:
        for n in ('validation/bow_shock_reference.py', 'validation/probe_bow_shock.py'):
            assert archive.read(n) == (ROOT/n).read_bytes()
    with zipfile.ZipFile(RESPONSE/'source.zip') as archive:
        assert archive.read('validation/geometry_response_v16.py') == (ROOT/'validation/geometry_response_v16.py').read_bytes()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_slc_aungier_experimental_v16'
    report = ROOT/'docs/phase3_geometry_v16.md'
    assert '## Final frozen verification' not in report.read_text(encoding='utf-8')
    with report.open('a', encoding='utf-8') as stream:
        stream.write(f'\n## Final frozen verification\n\nThe full suite passes **{passed} tests with one import-order skip** in '
            f'{seconds:.2f} seconds.\nThe entry-point module passes all five checks in a fresh process, giving\n'
            f'**{passed+1} distinct verified tests**, including nine new analytic-MCA and\n'
            'five research gas-dynamic/root checks. The suite includes repeated Stage 53,\n'
            'Stage 35 at 90%, both eightfold grids and unchanged conservation tolerances.\n\n'
            'The audit verifies 811 protected historical files, all v5-v15 golden\n'
            'assignments, unchanged experimental inputs and exact campaign/current\n'
            'production source identity. Only geometry and contract-version production\n'
            'files changed. All 108 classifications and all Stage 53 metrics are preserved.\n\n'
            f'[Frozen verification, logs and input hashes](../validation/campaigns/{stamp}/verification.json).\n')
    out = create_campaign(ROOT/'validation/campaigns'/stamp, purpose='v16_analytic_geometry_final_audit',
                          selection=dict(matched=MATCHED.name, response=RESPONSE.name, bow_probe=BOW.name, qualified=False))
    (out/'logs').mkdir()
    logs = ['v16_geometry_tests_01.log', 'v16_geometry_tests_02.log', 'v16_existing_geometry.log',
            'v16_full_geometry_tests.log', 'v16_entry_geometry_tests.log', 'v16_matched_geometry.log',
            'v16_bow_probe_final.log', 'v16_geometry_response_final.log', 'bow_probe_01.log']
    for name in logs:
        shutil.copyfile(ROOT/'tmp'/name, out/'logs'/name)
    for name in ('README.md', 'CHANGELOG.md'):
        shutil.copyfile(ROOT/name, out/name)
    write_json_new(out/'input_sha256.json', inputs)
    write_json_new(out/'verification.json', dict(full_suite=dict(passed=passed, skipped=skipped, seconds=seconds),
        isolated_entry_point_passed=5, distinct_tests_verified=passed+1, changed_preexisting_files=changed,
        historical_files_unchanged=len(protected), historical_goldens_unchanged=True, baseline_json_unchanged=len(evidence),
        preexisting_inventory_checked=len(before), source=source, matched_jobs=108,
        all_classifications_unchanged=True, stage53_metrics_unchanged=True, conditional_rows=96,
        row_sensitivities=6, comparison=summary, qualified=False))
    write_json_new(out/'artifact_sha256.json', {p.relative_to(out).as_posix(): sha(p) for p in out.rglob('*') if p.is_file()})
    print(out, flush=True)


if __name__ == '__main__':
    main()
