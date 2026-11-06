"""Conditioned-state feasibility probe of an unchoked detached-shock oracle."""
import numpy as np

from validation.bow_shock_reference import Surface, unchoked
from validation.campaign import create_campaign, write_json_new
from validation.phase3 import V, plain
from validation.phase3_rows import measured_states, geometry_file, row_model
from sm_throughflow.correlations.blade_geometry import _stagger
from sm_throughflow.solver.rows import ExitGeometry


ANCHORS = {35: '3978', 36: '4272', 37: '4182', 38: '4120'}


def surfaces(model, inlet, exit_geometry, radius):
    part = model._inlet_part(inlet, exit_geometry)
    geometry = part['g']
    curves = model.shock_surfaces
    coordinate = np.clip(inlet.t, 0., 1.)*(len(curves)-1)
    lower = np.minimum(coordinate.astype(int), len(curves)-2)
    weight = (coordinate-lower)[:, None, None]
    curves = (1.-weight)*curves[lower]+weight*curves[lower+1]
    cp = np.cos(np.arctan2(exit_geometry.r-inlet.r, exit_geometry.z-inlet.z))
    curves[:, :, 0] /= cp[:, None]
    opening = np.interp(exit_geometry.t, np.linspace(0., 1., len(model.throat_over_pitch)), model.throat_over_pitch)
    result = []
    for i, curve in enumerate(curves):
        stagger, sigma = geometry['stagger'][i], geometry['sigma'][i]
        p = _stagger(curve, -stagger)/sigma
        result.append(Surface(p, stagger, sigma, geometry['t_c'][i], radius*cp[i], opening[i]))
    return result, part


def main():
    out = create_campaign(purpose='unchoked_bow_shock_feasibility', selection=dict(
        prototype=True, release_evidence=False,
        source='10.1115/1.4053852',
        limitation='Unchoked branch only, constructed planar contour extension; no AVDR or viscous interaction'))
    print(out, flush=True)
    results = []
    for n, reading in ANCHORS.items():
        case = V.CASES[f'nasa_stage{n}']()
        point = next(p for p in case.measured_points(100) if p['reading'] == reading)
        inlet, exit, _ = measured_states(case.rotor_elements[reading], V.L.read_geometry(geometry_file(case.case_id, 0)),
                                        point['rpm'], point['mass_flow'])
        model = row_model(case.design, 0, point['rpm'])
        geometry = ExitGeometry(exit.t, exit.y, exit.r, exit.z)
        span, part = surfaces(model, inlet, geometry, case.design['rows'][0]['edge_radius_to_chord'])
        values = []
        for i, surface in enumerate(span):
            try:
                value = unchoked(part['mach1'][i], part['beta1'][i], surface, enforce_regime=False)
                value['baseline_loss'] = part['pointwise_shock'][i]
            except ValueError as exc:
                value = dict(error=str(exc), inlet_mach=part['mach1'][i], inlet_angle=part['beta1'][i],
                             choke_angle=surface.choke_angle(max(1., part['mach1'][i])))
            values.append(value)
            print(n, i, value, flush=True)
        results.append(dict(stage=n, reading=reading, points=values))
    write_json_new(out/'results.json', plain(results))
    print('COMPLETE', out, flush=True)


if __name__ == '__main__':
    main()
