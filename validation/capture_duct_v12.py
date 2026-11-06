"""Capture the first failed v11 Stage 35 duct wall interval verbatim."""
import inspect
import json
from dataclasses import asdict, is_dataclass
from validation.probe_iteration_v12 import BASELINE
from validation.campaign import ROOT, write_json_new
from validation.phase3 import plain
from sm_throughflow.contracts import ThroughflowTaskV2, ThroughflowDesignV2, SIMULATOR_VERSION
from sm_throughflow.simulator import SlcAungierSimulator
from sm_throughflow.provenance import runtime_identity

assert SIMULATOR_VERSION == 'slc_aungier_experimental_v11'
job = next(j for j in json.loads((BASELINE/'jobs.json').read_text()) if j['id']=='projected__nasa_stage35_90_3979')
task = ThroughflowTaskV2.model_validate(job['task'])
flow,_ = SlcAungierSimulator.build(ThroughflowDesignV2.model_validate(job['design']),task,task.operating_points[0])
original = flow.endwall._solve_gap
class Captured(BaseException):pass
def capture(*args,**kwargs):
    try:return original(*args,**kwargs)
    except Exception as exc:
        values = inspect.signature(original).bind(*args,**kwargs).arguments
        values = {k:asdict(v) if is_dataclass(v) else v for k,v in values.items()}
        write_json_new(ROOT/'tests/fixtures/v11_stage35_3979_duct_gap.json',plain(dict(
            source=runtime_identity(),job_id=job['id'],inputs=values,failure=exc.diagnostics)))
        raise Captured()
flow.endwall._solve_gap=capture
try:flow.solve(tol=task.numerics.tolerance,max_iterations=200)
except Captured:print('CAPTURED')
