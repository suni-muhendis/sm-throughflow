"""Reproducible capacity and grid probe of the planar interaction reference."""
import json

import numpy as np

from validation.campaign import create_campaign, write_json_new
from validation.displaced_passage_reference import PassageFailure, _inlet_capacity, solve
from validation.passage_shock_candidate import area_mach, static_ratio
from validation.probe_compressible_diffusion import BASELINE
from validation.verify_family_source_v14 import verify


def evaluate():
    gap, length, temperature, pressure = 0.012, 0.06, 300., 100000.
    flux_sonic = pressure * np.sqrt(1.4 / (287.05 * temperature)) / 1.2**3
    theta0, hk0 = 0.00009, 2.59
    inlet_capacity = _inlet_capacity(gap, theta0, hk0, temperature, pressure)
    results = []
    for fraction in (0.4, 0.75, 0.90, 0.95, 0.98, 1.02):
        mach_bare = area_mach(1 / fraction) if fraction < 1 else None
        pressure_bare = pressure * static_ratio(mach_bare) if mach_bare is not None else None
        for nodes in (17, 33, 65) if fraction == 0.4 else (33,):
            arc = np.linspace(0., length, nodes)
            result = dict(nodes=nodes, requested_fraction_of_bare_sonic_capacity=fraction,
                          inlet_limit_fraction_of_bare_capacity=inlet_capacity / (flux_sonic * gap),
                          inviscid_mach=mach_bare, inviscid_pressure_Pa=pressure_bare)
            try:
                coupled = solve(
                    arc, np.full_like(arc, gap), mass_per_span=fraction * flux_sonic * gap,
                    total_temperature=temperature, total_pressure=pressure, theta0=theta0, hk0=hk0,
                )
            except PassageFailure as exc:
                result.update(status=exc.reason, iterations=exc.iteration)
            else:
                result.update(
                    status="converged", iterations=coupled.iterations,
                    inlet_mach=float(coupled.mach[0]), exit_mach=float(coupled.mach[-1]),
                    exit_pressure_Pa=float(coupled.static_pressure[-1]),
                    exit_blockage=float(1 - coupled.effective_gap[-1] / gap),
                    relative_mass_residual=coupled.relative_mass_residual,
                    relative_gap_residual=coupled.relative_gap_residual,
                )
            results.append(result)
    return results


def main():
    identity = verify(BASELINE)
    results = evaluate()
    assert evaluate() == results
    output = create_campaign(
        purpose="symmetric_passage_displacement_feedback",
        selection=dict(research_only=True, manufactured_case=True, training_label_qualified=False),
    )
    report = dict(source=identity, rows=results)
    write_json_new(output / "analysis.json", report)
    print(json.dumps(report, indent=2), flush=True)
    print(output, flush=True)


if __name__ == "__main__":
    main()
