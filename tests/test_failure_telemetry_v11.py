"""Rejected trial evidence must survive failed as well as returned attempts."""
import pytest

from scripts.run_throughflow import build_case
from sm_throughflow.contracts import ThroughflowDesignV2, ThroughflowTaskV2
from sm_throughflow.simulator import SlcAungierSimulator
from sm_throughflow.solver.errors import SolverError


def flow():
    d,t=build_case(1)
    task=ThroughflowTaskV2.model_validate(t)
    return SlcAungierSimulator.build(ThroughflowDesignV2.model_validate(d),task,task.operating_points[0])[0]


def test_exhausted_backtracking_preserves_each_rejected_evaluation(monkeypatch):
    solver=flow()
    original=solver._coupled_iteration
    count=0
    def fail_after_checkpoint(*args):
        nonlocal count
        count+=1
        if count>2:raise SolverError('persistent injected failure',component='test')
        return original(*args)
    monkeypatch.setattr(solver,'_coupled_iteration',fail_after_checkpoint)
    with pytest.raises(SolverError) as failure:
        solver._solve(1e-7,200,4.,method='anderson')
    evidence=failure.value.diagnostics
    trace=evidence['repositioning']
    assert trace['backtracked_evaluations']==8
    assert [r['iteration'] for r in trace['rejected_evaluations']]==list(range(3,11))
    assert [r['fraction'] for r in trace['rejected_evaluations']]==[.5**i for i in range(8)]
    assert evidence['outer_evaluation']==11==solver._effort['outer_iterations']
    assert evidence['kind']=='numerical_failure'


def test_failed_attempt_summaries_keep_repositioning_evidence():
    solver=flow()
    result=solver.solve(tol=1e-7,max_iterations=2)
    assert not result.convergence.converged
    for attempt in result.convergence.attempts:
        trace=attempt.get('repositioning',attempt.get('failure',{}).get('repositioning'))
        assert trace is not None
        assert 'backtracked_evaluations' in trace
