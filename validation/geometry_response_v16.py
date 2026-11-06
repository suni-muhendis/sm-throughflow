"""Reproduce the sampling defect against frozen v15 at fixed chord coordinates."""
import json
import types
import zipfile

import numpy as np
from scipy.interpolate import CubicSpline

from sm_throughflow.correlations import blade_geometry as current
from validation.campaign import create_campaign, write_json_new
from validation.compare_geometry_v16 import BASELINE


def main():
    archived = types.ModuleType('sm_throughflow.correlations.archived_v15_geometry')
    archived.__package__ = 'sm_throughflow.correlations'
    with zipfile.ZipFile(BASELINE/'source.zip') as source:
        code = source.read('src/sm_throughflow/correlations/blade_geometry.py')
        # Its only local imported functions come from the unchanged Aungier module.
        from validation.campaign import ROOT
        assert source.read('src/sm_throughflow/correlations/aungier.py') == (ROOT/'src/sm_throughflow/correlations/aungier.py').read_bytes()
    exec(compile(code, 'archived_v15_geometry', 'exec'), archived.__dict__)
    out = create_campaign(purpose='v16_fixed_coordinate_geometry_response', selection=dict(
        baseline=BASELINE.name, manufactured_fixture=True, experimental_evidence=False))
    results = dict(fixture=dict(camber=30., thickness=.07, edge=.002, transition=.417,
                               turning_ratio=.4, maximum_thickness_location=.671234567),
                   chord_samples=np.linspace(.02, .98, 201).tolist(), responses=[], apex_responses=[])
    for step in (1e-3, 1e-4, 1e-5, 1e-6, 1e-7):
        response, apex = dict(step=step), dict(step=step)
        for label, module in [('v15', archived), ('v16', current)]:
            def shape(x):
                p = module.section('mca', 'multiple_circular_arc', 30., .07, edge_radius=.002,
                    transition=.417, turning_ratio=.4, max_thickness_at=x)[0]
                return CubicSpline(p[:, 0], p[:, 1])(results['chord_samples'])
            response[label] = float(np.max(abs((shape(.671234567+step)-shape(.671234567-step))/(2*step))))
            apex[label] = (module.mca_shape(30., .417+step, .4)[1]-module.mca_shape(30., .417-step, .4)[1])/(2*step)
        results['responses'].append(response)
        results['apex_responses'].append(apex)
    write_json_new(out/'sensitivity.json', results)
    print(out, flush=True)
    print(json.dumps(results, indent=2), flush=True)


if __name__ == '__main__':
    main()
