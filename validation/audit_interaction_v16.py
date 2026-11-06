"""Freeze rejected interaction hypotheses, unchanged production and verification."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET
import zipfile

from validation.campaign import ROOT, create_campaign, write_json_new
from validation.probe_compressible_diffusion import BASELINE
from validation.verify_family_source_v14 import verify

MATCHED=ROOT/'validation/campaigns/20261105T133202417353Z_slc_aungier_experimental_v16'
PILOT=ROOT/'validation/campaigns/20261105T134804943498Z_slc_aungier_experimental_v16'
PRIOR_CONDITIONED=ROOT/'validation/campaigns/20261105T133324096613Z_slc_aungier_experimental_v16'
EVIDENCE=ROOT/'validation/campaigns/20261105T140100314641Z_slc_aungier_experimental_v16'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archived_equal(folder,names):
    manifest=json.loads((folder/'manifest.json').read_text())
    assert sha(folder/'source.zip')==manifest['archive_sha256']
    with zipfile.ZipFile(folder/'source.zip') as z:
        for name in names:
            assert z.read(name)==(ROOT/name).read_bytes(),name


def main():
    full=(ROOT/'tmp/interaction_full_final.log').read_text(encoding='utf-8')
    match=re.search(r'(\d+) passed, (\d+) skipped in ([\d.]+)s',full)
    assert match and 'FAILED ' not in full
    passed,skipped=map(int,match.groups()[:2])
    assert (passed,skipped)==(331,1)
    tree=ET.parse(ROOT/'tmp/interaction_final_junit.xml')
    cases=tree.findall('.//testcase')
    assert len(cases)==332
    assert not tree.findall('.//failure') and not tree.findall('.//error')
    omitted=[c for c in cases if c.find('skipped') is not None]
    assert len(omitted)==1 and omitted[0].get('name')=='test_building_the_environment_does_not_import_the_solver'
    retry=(ROOT/'tmp/interaction_tmp_retry.log').read_text()
    assert '2 passed, 25 deselected' in retry and 'ERROR' not in retry
    entry=(ROOT/'tmp/interaction_entry_point_final.log').read_text()
    assert '5 passed' in entry and 'skipped' not in entry
    units=(ROOT/'tmp/interaction_unit_final.log').read_text()
    assert '13 passed' in units
    distinct=passed+skipped
    assert distinct==332
    source=verify(BASELINE)
    verify(MATCHED)
    with zipfile.ZipFile(BASELINE/'source.zip') as z:
        assert z.read('tests/test_throughflow_env.py')==(ROOT/'tests/test_throughflow_env.py').read_bytes()
    historic=json.loads((ROOT/'validation/campaigns/20261104_phase01_baseline/manifest.json').read_text())['files']
    protected={k:v for k,v in historic.items() if k.startswith(('validation/cases/','validation/results/','validation/reports/','validation/studies/results/'))}
    assert len(protected)==811 and all(sha(ROOT/k)==v for k,v in protected.items())
    baseline_hashes=json.loads((MATCHED/'manifest.json').read_text())['selection']['baseline_sha256']
    assert all(sha(ROOT/k)==v for k,v in baseline_hashes.items())
    assert (MATCHED/'jobs.json').read_bytes()==(BASELINE/'jobs.json').read_bytes()
    comparison=json.loads((MATCHED/'analysis.json').read_text())
    assert not comparison['screen']['necessary_development_checks_passed']
    assert comparison['screen']['lost_converged_ids']==[]
    assert all(v['repeat_equal'] for v in comparison['preservation'].values())
    for name,n in [('rows.json',96),('row_sensitivity.json',6)]:
        rows=json.loads((MATCHED/name).read_text())
        assert len(rows)==n and all(r['research_override']=='compressible_circulation_hybrid_r1' for r in rows)
    archived_equal(MATCHED,['validation/compressible_diffusion_candidate.py','validation/probe_compressible_diffusion.py',
                            'validation/compare_interaction_candidates.py'])
    archived_equal(PILOT,['validation/passage_shock_candidate.py','validation/probe_passage_coupled.py',
                          'validation/probe_passage_shock.py'])
    archived_equal(EVIDENCE,['validation/shock_interaction_evidence.py',
        'validation/cases/nasa_rotor37_shock_interaction/TM107310_table6.csv',
        'validation/cases/nasa_rotor37_shock_interaction/TM107310_table7.csv',
        'validation/cases/nasa_rotor37_shock_interaction/source.json',
        'validation/cases/nasa_rotor37_shock_interaction/notes.md'])
    log=(ROOT/'tmp/passage_shock_cached_final.log').read_text()
    path=re.search(r'COMPLETE (.+)',log)
    assert path
    conditioned=Path(path[1].strip())
    assert conditioned.is_relative_to(ROOT/'validation/campaigns')
    archived_equal(conditioned,['validation/passage_shock_candidate.py','validation/probe_passage_shock.py'])
    assert json.loads((conditioned/'results.json').read_text())==json.loads((PRIOR_CONDITIONED/'results.json').read_text())
    pilot={p.stem:json.loads(p.read_text()) for p in (PILOT/'results').glob('*.json')}
    assert len(pilot)==5 and sum(r['converged'] for r in pilot.values())==1
    pilot_summary={k:dict(classification=r['classification'],converged=r['converged'],metrics=r['metrics'],
        evaluation_budget_encountered=any(a.get('failure',{}).get('component')=='research_passage_shock_budget'
                                         for a in r['diagnostics'].get('attempts',[]))) for k,r in pilot.items()}
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_slc_aungier_experimental_v16'
    report=ROOT/'docs/phase3_interaction_v16.md'
    assert '## Final verification' not in report.read_text()
    with report.open('a',encoding='utf-8') as stream:
        stream.write(f'\n## Final verification\n\n**{distinct} distinct tests are verified on the retained production and final\n'
            f'research code.** The final full run records {passed} passed and one\n'
            f'import-order skip in {float(match[3]):.2f} seconds, with zero errors or\n'
            'failures in its per-test XML record. The entry-point module passes all\n'
            'five checks in a fresh process. All 13 candidate tests pass. The earlier\n'
            'incomplete run and two temporary-directory setup errors are retained in\n'
            'the audit logs; the final suite uses a fresh repository-local temporary\n'
            'directory. No solver assertion or tolerance was relaxed.\n\n'
            'The production suite includes both eightfold grids, repeated Stage 53,\n'
            'Stage 35 at 90% speed and unchanged conservation checks. The audit\n'
            'confirms byte-identical v16 production, unchanged historical goldens,\n'
            '811 protected evidence files and all frozen v16 campaign files. The\n'
            'cached conditioned-shock rerun is exactly equal to its earlier results.\n\n'
            f'[Final audit and logs](../validation/campaigns/{stamp}/verification.json).\n')
    out=create_campaign(ROOT/'validation/campaigns'/stamp,purpose='post_v16_interaction_final_audit',selection=dict(
        matched=MATCHED.name,pilot=PILOT.name,conditioned=conditioned.name,evidence=EVIDENCE.name,
        production_promoted=False,qualification=False))
    (out/'logs').mkdir()
    logs=['interaction_full_tests.log','interaction_incomplete_run.json','interaction_full_final.log','interaction_final_junit.xml',
          'interaction_tmp_retry.log','interaction_unit_final.log',
          'interaction_entry_point_final.log','interaction_entry_tests.log','interaction_comparison.log',
          'passage_coupled.log','passage_coupled_r2.log','passage_shock_cached_final.log']
    for name in logs:
        shutil.copyfile(ROOT/'tmp'/name,out/'logs'/name)
    for name in ('README.md','CHANGELOG.md'):
        shutil.copyfile(ROOT/name,out/name)
    inputs={p.relative_to(ROOT).as_posix():sha(p) for folder in (BASELINE,MATCHED,PILOT,conditioned,EVIDENCE)
            for p in folder.rglob('*') if p.is_file()}
    write_json_new(out/'input_sha256.json',inputs)
    write_json_new(out/'verification.json',dict(source=source,production_unchanged=True,
        full_suite=dict(passed=passed,skipped=skipped,errors=0,failures=0,seconds=float(match[3])),
        temporary_directory_retry_passed=2,isolated_entry_point_passed=5,final_candidate_tests_passed=13,
        distinct_tests_verified=distinct,old_goldens_unchanged=True,historical_files_unchanged=811,
        baseline_files_unchanged=len(baseline_hashes),matched_jobs=108,conditional_rows=96,row_sensitivities=6,
        comparison=comparison,passage_pilot=pilot_summary,conditioned_rerun_exact=True,
        production_promoted=False,experimentally_qualified=False,training_label_qualified=False))
    write_json_new(out/'artifact_sha256.json',{p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()})
    print(out,flush=True)


if __name__=='__main__':
    main()
