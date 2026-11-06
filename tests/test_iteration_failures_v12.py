"""Independent duct accuracy and terminal continuation/step diagnostics."""
import numpy as np
import pytest
from scripts.run_throughflow import build_case
from sm_throughflow.contracts import ThroughflowDesignV2, ThroughflowTaskV2
from sm_throughflow.simulator import SlcAungierSimulator
from sm_throughflow.solver.errors import SolverError
from sm_throughflow.solver.endwall import EndwallBoundaryLayers, _Edge
from sm_throughflow.solver.reposition import CoupledRepositioning
from sm_throughflow.solver.throughflow import Throughflow


def test_duct_wall_march_matches_positive_exponential_at_second_order(monkeypatch):
    wall=EndwallBoundaryLayers(max_passes=200)
    e1=_Edge(r=1.,rho=1.,vm=100.,c_theta=0.,P=287.05*288.15,T=288.15,phi=0.,m=0.)
    e2=_Edge(**dict(vars(e1),m=1.))
    initial=np.array([.7,10.,0.])
    state=wall._state(e1,*initial,0.,1/7)
    monkeypatch.setattr(wall,'_sources',lambda edge,state,*args:3*wall._conserved(edge,state))
    args=(e1,e2,state,initial,0.,None,('analytic','hub'),'hub',1)
    with pytest.raises(SolverError):wall._integrate_gap(*args)
    errors=[]
    for count in (8,16,32):
        wall.subdivisions=count
        actual,_,info=wall._integrate_gap(*args)
        growth=wall._conserved(e2,actual)[1]/initial[1]
        assert growth==pytest.approx(((1+1.5/count)/(1-1.5/count))**count,rel=1e-7)
        assert all(d['residual']<=1e-8 for d in info)
        errors.append(abs(growth/np.exp(3.)-1))
    assert errors[0]/errors[1]>3.8 and errors[1]/errors[2]>3.8


def inputs():
    d,t=build_case(1)
    t['numerics']['duct_subdivisions']=4
    return ThroughflowDesignV2.model_validate(d),ThroughflowTaskV2.model_validate(t)


def test_failed_coarse_seed_keeps_original_attempt_and_total_effort(monkeypatch):
    def fail(self,*args,**kwargs):
        self._effort=dict(outer_iterations=3,station_solves=5,row_model_calls=2,endwall_solves=1)
        raise SolverError('forced current-iterate capacity',kind='quasi_normal_capacity',component='test',
            attempts=[dict(converged=False,effort=dict(self._effort))],effort=dict(self._effort))
    monkeypatch.setattr(Throughflow,'solve',fail)
    design,task=inputs()
    with pytest.raises(SolverError) as failure:
        SlcAungierSimulator.solve_state(design,task,task.operating_points[0])
    d=failure.value.diagnostics
    assert d['kind']=='quasi_normal_capacity'
    assert [a['grid_role'] for a in d['attempts']]==['requested_initial','coarse_seed']
    assert [a['duct_subdivisions'] for a in d['attempts']]==[4,1]
    assert d['effort']==dict(outer_iterations=6,station_solves=10,row_model_calls=4,endwall_solves=2)
    assert d['grid_continuation_failure']['component']=='test'


def test_failed_acceleration_construction_keeps_its_local_trace(monkeypatch):
    def fail(*args,**kwargs):raise SolverError('forced step failure',component='repositioning')
    monkeypatch.setattr(CoupledRepositioning,'step',fail)
    design,task=inputs()
    flow,_=SlcAungierSimulator.build(design,task,task.operating_points[0])
    with pytest.raises(SolverError) as failure:
        flow._solve(1e-7,200,4.,method='anderson')
    d=failure.value.diagnostics
    assert d['component']=='repositioning' and d['outer_evaluation']==1
    assert d['repositioning']['method']=='anderson'
    assert d['repositioning']['preconditioner']=='elliptic_half_step'
    assert d['repositioning']['rejected_evaluations']==[]
