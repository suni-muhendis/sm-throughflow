"""v9 original wall controls and bidirectional mass-shooting regressions."""
from copy import deepcopy
import json
from pathlib import Path

import numpy as np
import pytest

from scripts.run_throughflow import build_case
from sm_throughflow.contracts import ThroughflowDesignV2, ThroughflowTaskV2
from sm_throughflow.geometry import station_grid
from sm_throughflow.simulator import SlcAungierSimulator
from sm_throughflow.solver.gas import PerfectGas
from sm_throughflow.solver.geometry import Annulus, QuasiNormals, surface_geometry
from sm_throughflow.solver.quasi_normal import solve_quasi_normal
from validation.compare_geometry_v9 import make_jobs
from validation.phase3 import projected_geometry


def test_captured_real_machine_root_is_independent_of_start_and_repeatable():
    # Exact first v8 failure at Stage35, design speed, half rotor-stator gap.
    # Capture: campaigns/20261104T194452331854Z_slc_aungier_experimental_v8.
    raw = json.loads((Path(__file__).parent/'fixtures/v8_stage35_gap_failed_quasi_normal.json').read_text())
    inputs = {k: np.asarray(v) if isinstance(v, list) else v for k, v in raw['inputs'].items()}
    gas = PerfectGas()
    recovered = solve_quasi_normal(gas=gas, **inputs)
    again = solve_quasi_normal(gas=gas, **inputs)
    known_branch = solve_quasi_normal(gas=gas, **dict(inputs, wm_guess=np.full_like(inputs['r'], 300.)))
    assert recovered.solver_diagnostics['two_sided_bracket_recovery']
    assert recovered.mass_flow == pytest.approx(20.82, abs=2e-12)
    np.testing.assert_array_equal(recovered.Wm, again.Wm)
    np.testing.assert_allclose(recovered.Wm, known_branch.Wm, rtol=2e-11)
    np.testing.assert_allclose(recovered.I, inputs['I'], rtol=2e-15)
    assert recovered.solver_diagnostics['residual'] <= inputs.get('tol', 1e-12)


def test_manufactured_radial_enthalpy_gradient_matches_exact_momentum_solution():
    # d(Wm^2/2)/dr=dI/dr, zero swirl/entropy/curvature: an independent exact root.
    gas = PerfectGas()
    errors = []
    for n in (41, 81):
        t = np.linspace(0., 1., n)
        r = .2 + .1*t
        I = 350000. - 30000.*t
        exact = np.sqrt(300.**2 - 60000.*t)
        mass = 2*np.pi*np.trapezoid(r*gas.density(I-.5*exact**2, 0.)*exact, r)
        out = solve_quasi_normal(gas, r-r[0], t, r, t*0, t*0, t*0, 0., 0., I, t*0,
                                 mass, swirl=t*0)
        assert out.solver_diagnostics['two_sided_bracket_recovery']
        assert out.mass_flow == pytest.approx(mass, rel=2e-13)
        errors.append(float(np.max(np.abs(out.Wm-exact))))
    assert max(errors) < 1e-10


def test_squared_velocity_form_converges_on_captured_oscillating_profile():
    raw = json.loads((Path(__file__).parent/'fixtures/v9_unsquared_profile_failure.json').read_text())
    assert raw['diagnostics']['residual'] > .01  # old 200-iteration failure
    inputs = {k: np.asarray(v) if isinstance(v, list) else v for k, v in raw['inputs'].items()}
    result = solve_quasi_normal(gas=PerfectGas(), **inputs)
    assert result.mass_flow == pytest.approx(inputs['mass_flow'], abs=2e-12)
    assert result.solver_diagnostics['residual'] <= 1e-12
    assert result.solver_diagnostics['iterations'] < 20
    np.testing.assert_allclose(result.I, inputs['I'], rtol=2e-15)


def test_interior_wall_controls_change_geometry_without_duplicating_row_work():
    d, task = build_case(1)
    row = d['rows'][0]
    x = .5*(row['leading_edge_axial_m']+row['trailing_edge_axial_m'])
    stations = d['passage']['stations']
    hub = np.interp(x, [p['axial_m'] for p in stations], [p['hub_radius_m'] for p in stations])
    tip = np.interp(x, [p['axial_m'] for p in stations], [p['shroud_radius_m'] for p in stations])
    # Outward bulge has no hidden minimum area. Both original walls are retained.
    stations.append(dict(axial_m=x, hub_radius_m=float(hub), shroud_radius_m=float(tip+.0002)))
    stations.sort(key=lambda p: p['axial_m'])
    design = ThroughflowDesignV2.model_validate(d)
    vertices, z, indices = station_grid(design)
    assert x in [p.axial_m for p in vertices] and x not in z
    assert z[indices[row['row_id']]+1] == row['trailing_edge_axial_m']
    t = ThroughflowTaskV2.model_validate(task)
    flow, _ = SlcAungierSimulator.build(design, t, t.operating_points[0])
    assert len(flow.row_at) == len(d['rows'])
    fractions = np.tile(np.linspace(0., 1., 11), (flow.qn.count, 1))
    original = surface_geometry(flow.qn, fractions, 'full', flow.annulus)
    chord = surface_geometry(flow.qn, fractions, 'full')
    assert original.m[-1, -1] > chord.m[-1, -1]
    assert np.max(np.abs(original.kappa-chord.kappa)) > .01


def test_collinear_wall_controls_are_representation_invariant():
    a = Annulus.from_points([(0., .2), (.5, .21), (1., .2)], [(0., .3), (.5, .32), (1., .3)])
    b = Annulus.from_points([(0., .2), (.25, .205), (.5, .21), (1., .2)],
                            [(0., .3), (.25, .31), (.5, .32), (1., .3)])
    qn = QuasiNormals.on(a, [0., .2, .8, 1.])
    t = np.tile(np.linspace(0., 1., 9), (4, 1))
    ga, gb = (surface_geometry(qn, t, 'full', v) for v in (a, b))
    for name in ('m', 'phi', 'kappa', 'r', 'z'):
        np.testing.assert_allclose(getattr(ga, name), getattr(gb, name), rtol=2e-14, atol=1e-14)


def test_matched_campaign_keeps_archived_tasks_and_design_perturbations():
    from validation import run as V
    original = V.CASES['nasa_stage35']().design
    projected, _ = projected_geometry(original)
    projected['rows'][0]['tip_clearance_m'] *= 1.5
    source = dict(id='clearance', case='nasa_stage35', design=projected, task={'numerics': {'max_iterations': 200}})
    before = deepcopy(source)
    a, b = make_jobs([source])
    assert source == before
    assert a['design'] == projected and a['task'] == b['task'] == source['task']
    assert b['design']['rows'] == projected['rows']
    assert b['design']['passage'] == original['passage']
