"""Wall-step positivity, independent ODE accuracy and captured machine failures."""
import json
from pathlib import Path

import numpy as np
import pytest

from sm_throughflow.solver.endwall import EndwallBoundaryLayers, _Edge, WallState, blade_force_defect
from sm_throughflow.solver.errors import SolverError


def captured(name):
    value = json.loads((Path(__file__).parent/'fixtures'/name).read_text())['inputs']
    for field in ('e1', 'e2'):
        value[field] = _Edge(**value[field])
    for field in ('s1', 'predictor'):
        value[field] = WallState(**value[field])
    return value


def integrate(wall, v):
    return wall._integrate_gap(v['e1'], v['e2'], v['s1'], v['initial'], v['omega_w'],
                               v['blade'], ('captured', v['wall']), v['wall'], v['station'])


def test_captured_stage38_gap_needs_wall_resolution_not_a_looser_tolerance():
    inputs = captured('v9_stage38_endwall_gap.json')
    with pytest.raises(SolverError) as failure:
        integrate(EndwallBoundaryLayers(max_passes=200, subdivisions=1), inputs)
    assert not failure.value.diagnostics['details']['physical_limit_established']
    values = []
    for count in (8, 16, 32):
        state, _, info = integrate(EndwallBoundaryLayers(max_passes=200, subdivisions=count), inputs)
        assert all(row['residual'] <= 1e-8 and row['iterations'] <= 200 for row in info)
        assert state.theta11 > 0 and state.delta1 > 0
        values.append(state.theta11)
    assert abs(values[1]/values[2]-1) < .01
    # Piecewise profile limiters need not give monotone grid differences.
    assert (max(values)-min(values))/values[-1] < .01


def test_divergent_stage35_gap_can_be_marched_but_is_not_a_machine_capacity_proof():
    inputs = captured('v9_stage35_endwall_gap.json')
    wall = EndwallBoundaryLayers(max_passes=200, subdivisions=8)
    first = integrate(wall, inputs)
    wall.reset()
    again = integrate(wall, inputs)
    assert first == again
    # The very thick result is deliberately visible; a local integration root
    # is not an admissible whole-machine solution or a physical choke label.
    assert first[0].delta1 > .1
    assert all(row['residual'] <= 1e-8 for row in first[2])


def test_positive_growing_ode_explains_coarse_trapezoid_failure_and_second_order_accuracy(monkeypatch):
    wall = EndwallBoundaryLayers(max_passes=200)
    e1 = _Edge(r=1., rho=1., vm=100., c_theta=0., P=287.05*288.15, T=288.15, phi=0., m=0.)
    e2 = _Edge(**dict(e1.__dict__, m=1.))
    # X'=3X, M'=3M keeps H1=1.4: exact positive solution exp(3m).
    # A single trapezoid step instead has a negative amplification factor.
    initial = np.array([.7, 10., 0.])
    s1 = wall._state(e1, *initial, 0., 1/7)
    def source(edge, state, *args):
        return 3.*wall._conserved(edge, state)
    monkeypatch.setattr(wall, '_sources', source)
    arguments = (e1, e2, s1, initial, 0., dict(g=.04, gap=0., omega=0.), ('analytic', 'hub'), 'hub', 1)
    with pytest.raises(SolverError):
        wall._integrate_gap(*arguments)
    errors = []
    for count in (8, 16, 32):
        wall.reset()
        wall.subdivisions = count
        state, _, _ = wall._integrate_gap(*arguments)
        actual = wall._conserved(e2, state)[1]/initial[1]
        discrete = ((1+1.5/count)/(1-1.5/count))**count
        assert actual == pytest.approx(discrete, rel=1e-7)
        errors.append(abs(actual/np.exp(3.)-1))
    assert errors[0]/errors[1] > 3.8 and errors[1]/errors[2] > 3.8


def test_force_defect_saturation_does_not_overflow():
    with np.errstate(over='raise', invalid='raise'):
        assert blade_force_defect(1e300, .04, .001) == pytest.approx(.12*.04+.0005)


def test_wall_budget_exhaustion_remains_a_numerical_failure():
    with pytest.raises(SolverError) as failure:
        integrate(EndwallBoundaryLayers(max_passes=1, subdivisions=8), captured('v9_stage38_endwall_gap.json'))
    assert failure.value.diagnostics['kind'] == 'numerical_failure'
    assert failure.value.diagnostics['iterations'] == 1
    assert failure.value.diagnostics['residual'] > 1e-8


def test_rejected_coupled_trial_rolls_back_endwall_state_and_recovers_same_root(monkeypatch):
    from scripts.run_throughflow import build_case
    from sm_core import make_env
    from sm_throughflow.solver.reposition import CoupledRepositioning
    d, t = build_case(1)
    env = make_env('turbomachinery_throughflow')
    reference = env.evaluate('baseline', t, 'one', d)
    assert reference.status == 'success', reference.error_message
    marker = dict(armed=False, injected=False)
    step, solve = CoupledRepositioning.step, EndwallBoundaryLayers.solve
    def arm(self, *args, **kwargs):
        before = self.accepted
        result = step(self, *args, **kwargs)
        if self.accepted > before and not marker['injected']:
            marker['armed'] = True
        return result
    def fail_once(self, *args, **kwargs):
        if marker['armed']:
            marker.update(armed=False, injected=True)
            self._delta_nu[('discarded_trial',)] = 123.
            raise SolverError('forced rejected coupled trial', component='endwall')
        assert ('discarded_trial',) not in self._delta_nu
        return solve(self, *args, **kwargs)
    monkeypatch.setattr(CoupledRepositioning, 'step', arm)
    monkeypatch.setattr(EndwallBoundaryLayers, 'solve', fail_once)
    result = env.evaluate('rollback', t, 'one', d)
    assert marker['injected'] and result.status == 'success', result.error_message
    conv = result.raw_simulation_output['operating_points'][0]['convergence']
    assert len(conv['attempts']) == 1
    assert conv['repositioning']['backtracked_evaluations'] >= 1
    for key in ('pressure_ratio_total', 'efficiency_isentropic', 'power_W', 'exit_blockage'):
        assert result.metrics[key] == pytest.approx(reference.metrics[key], rel=2e-7)
