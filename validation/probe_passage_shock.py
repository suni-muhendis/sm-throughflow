"""Conditioned assessment of the explicit choked shock candidate; no fitting."""
import numpy as np

from validation.campaign import create_campaign, write_json_new
from validation.phase3 import V, plain, Simulator
from validation.phase3_rows import measured_states, geometry_file, row_model
from validation.passage_shock_candidate import Surface, shock, references
from sm_throughflow.contracts import ThroughflowDesignV2
from sm_throughflow.correlations.blade_geometry import section, _stagger, _arc_length
from sm_throughflow.solver.rows import ExitGeometry

ANCHORS = {35: '3978', 36: '4272', 37: '4182', 38: '4120'}


def pressure_contours(design, index):
    design = ThroughflowDesignV2.model_validate(design)
    row = design.rows[index]
    curves = []
    for sec in Simulator._sections(row, design.passage.stations):
        _, lower, _ = section(row.profile, row.camberline, sec['camber'], sec['t_c'],
                              row.max_camber_location, row.edge_radius_to_chord, **sec['shape'])
        p = _stagger(lower, sec['stagger'])*sec['solidity']
        arc = _arc_length(p[:, 0], p[:, 1])
        curves.append(np.column_stack([np.interp(np.linspace(0., 1., 401), arc, p[:, k]) for k in (0, 1)]))
    return np.array(curves), row.edge_radius_to_chord


def surfaces(model, inlet, exit_geometry, pressure, radius):
    part = model._inlet_part(inlet, exit_geometry)
    geometry = part['g']
    coordinate = np.clip(inlet.t, 0., 1.)*(len(pressure)-1)
    lower = np.minimum(coordinate.astype(int), len(pressure)-2)
    weight = (coordinate-lower)[:, None, None]
    fields = [(1.-weight)*v[lower]+weight*v[lower+1] for v in (model.shock_surfaces, pressure)]
    cp = np.cos(np.arctan2(exit_geometry.r-inlet.r, exit_geometry.z-inlet.z))
    for values in fields:
        values[:, :, 0] /= cp[:, None]
    opening = np.interp(exit_geometry.t, np.linspace(0., 1., len(model.throat_over_pitch)), model.throat_over_pitch)
    result = []
    for i, (suction, pressure) in enumerate(zip(*fields)):
        stagger, sigma = geometry['stagger'][i], geometry['sigma'][i]
        p, q = [_stagger(v, -stagger)/sigma for v in (suction, pressure)]
        result.append(Surface(p, stagger, sigma, geometry['t_c'][i], radius*cp[i], opening[i], q))
    return result, part


def main():
    out = create_campaign(purpose='choked_passage_shock_conditioned_candidate', selection=dict(
        prototype=True, release_evidence=False, training_label_qualified=False,
        source='10.1115/1.4053852',
        limitation='Constructed-contour extension; supersonic only; no AVDR or viscous interaction'))
    print(out, flush=True)
    results = []
    for n, reading in ANCHORS.items():
        case = V.CASES[f'nasa_stage{n}']()
        point = next(p for p in case.measured_points(100) if p['reading'] == reading)
        inlet, exit, _ = measured_states(case.rotor_elements[reading], V.L.read_geometry(geometry_file(case.case_id, 0)),
                                        point['rpm'], point['mass_flow'])
        model = row_model(case.design, 0, point['rpm'])
        geometry = ExitGeometry(exit.t, exit.y, exit.r, exit.z)
        pressure, radius = pressure_contours(case.design, 0)
        span, part = surfaces(model, inlet, geometry, pressure, radius)
        baseline = model(inlet, exit, geometry)
        values = []
        for i, surface in enumerate(span):
            args = (part['mach1'][i], part['beta1'][i], abs(np.degrees(baseline.exit_angle[i])),
                    exit.P[i]/part['pt1'][i], surface)
            try:
                value = shock(*args)
                value['status'] = 'evaluated_inviscid_research'
            except ValueError as exc:
                value = dict(status='unsupported', error=str(exc))
                try:
                    value['references'] = references(args[0], surface, args[2])
                except ValueError as more:
                    value['reference_error'] = str(more)
            value.update(inlet_mach=float(args[0]), inlet_angle=float(args[1]), exit_angle=float(args[2]),
                         exit_static_pressure_ratio=float(args[3]), baseline_loss=float(part['pointwise_shock'][i]),
                         baseline_diffusion=float(baseline.diagnostics['equivalent_diffusion'][i]),
                         baseline_blockage=float(baseline.wake_blockage[i]),
                         choke_angle=surface.choke_angle(args[0]),
                         avdr=float(exit.rho[i]*exit.Wm[i]/(inlet.rho[i]*inlet.Wm[i])),
                         measured_span=0 < i < len(span)-1)
            values.append(value)
            print(n, i, value['status'], value.get('regime', value.get('error')), value.get('loss'), flush=True)
        results.append(dict(stage=n, reading=reading, points=values))
    write_json_new(out/'results.json', plain(results))
    print('COMPLETE', out, flush=True)


if __name__ == '__main__':
    main()
