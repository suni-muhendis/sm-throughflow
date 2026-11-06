"""Condition the attached layer on the NASA DCA suction-side measurements."""
import csv
import json

import numpy as np
from scipy.interpolate import PchipInterpolator

from sm_throughflow.solver.endwall import sutherland_air
from validation.blade_layer_reference import march
from validation.campaign import ROOT, create_campaign, write_json_new
from validation.probe_compressible_diffusion import BASELINE
from validation.verify_family_source_v14 import verify

CASE = ROOT / "validation/cases/nasa_dca_cascade_layer"


def read_table(number):
    with (CASE / f"CR185118_vol1_table{number}.csv").open(newline="", encoding="utf-8") as stream:
        return list(csv.reader(stream))[3:]


def evaluate(rtol=1e-8, *, seed_percent=10.4):
    # CR-185118 Volume I, Appendix A. The printed chord is measured between
    # the edge-circle centres and the suction surface is an arc of R = 189.1 mm.
    chord, radius = 0.2286, 0.1891
    def to_arc(percent):
        return radius * np.arcsin((np.asarray(percent) / 100 - 0.5) * chord / radius)

    def to_percent(arc):
        return 100 * (radius * np.sin(np.asarray(arc) / radius) / chord + 0.5)

    pressure_samples = np.array([[float(row[3]), float(row[5])] for row in read_table(13) if row[3]])
    suction = {float(row[0]): row for row in read_table(15) if row[1] == "S"}
    stations = to_arc(pressure_samples[:, 0])
    speed = PchipInterpolator(stations, pressure_samples[:, 1])
    seed = to_arc(seed_percent)
    samples = np.unique(np.r_[stations, to_arc([19.7, 30.1, 40.5]),
                              to_arc(np.linspace(20., 45., 251))])
    sample = np.r_[seed, samples[samples > seed]]

    # The report assumes nu = 0.150 cm²/s. Choose a reference total pressure
    # to reproduce this viscosity-to-density ratio at the initial edge state.
    # 300 K is a reference assumption. The low-speed data do not give Tt.
    nu, total_temperature, gas_constant, gamma = 1.5e-5, 300., 287.05, 1.4
    cp = gamma * gas_constant / (gamma - 1)
    speed0 = float(speed(seed))
    temperature0 = total_temperature - speed0**2 / (2 * cp)
    pressure0 = sutherland_air(temperature0) / nu * gas_constant * temperature0
    pt = pressure0 * (total_temperature / temperature0)**(cp / gas_constant)
    hk0, re0 = map(float, suction[seed_percent][6:8])
    result = march(stations, pressure_samples[:, 1], theta0=re0 * nu / speed0, hk0=hk0,
                   total_temperature=total_temperature, total_pressure=pt, sample_at=sample, rtol=rtol)
    points = []
    for percent in (p for p in (19.7, 30.1, 40.5) if p > seed_percent):
        record = suction[percent]
        x = to_arc(percent)
        index = np.searchsorted(result.arc, x)
        predicted = None
        if index < len(result.arc) and result.arc[index] == x:
            predicted = dict(
                momentum_thickness_m=float(result.momentum_thickness[index]),
                displacement_thickness_m=float(result.displacement_thickness[index]),
                reynolds_theta=float(result.reynolds_theta[index]),
                kinematic_shape=float(result.kinematic_shape[index]),
                dissipation_W_per_m=float(result.dissipation_power_per_span[index]),
            )
        points.append(dict(percent_chord=percent, prediction=predicted,
                           spline_fit=dict(h12=record[2], reynolds_theta=record[4]),
                           falkner_skan_fit=dict(h12=record[6], reynolds_theta=record[7])))
    # The authors located separation using H12 = 3.5 in their spline fit.
    # Compare that proxy as well as the model's own zero-shear event.
    shape = result.displacement_thickness / result.momentum_thickness
    crossings = np.flatnonzero((shape[:-1] < 3.5) & (shape[1:] >= 3.5))
    proxy = None
    if len(crossings):
        i = crossings[0]
        proxy = float(to_percent(np.interp(3.5, shape[i:i+2], result.arc[i:i+2])))
    return dict(
        seed_percent_chord=seed_percent, seed_hk=hk0, seed_re_theta=re0,
        start_velocity=speed0, total_pressure_Pa=float(pt), total_temperature_K=total_temperature,
        predicted_zero_shear_percent_chord=float(to_percent(result.arc[-1])) if result.separated else None,
        predicted_h12_3p5_percent_chord=proxy,
        reported_spline_separation_percent_chord=31.9,
        points=points, rtol=rtol, training_label_qualified=False,
    )


def main():
    identity = verify(BASELINE)
    result, tighter = evaluate(), evaluate(rtol=1e-10)
    later_seed = evaluate(seed_percent=19.7)
    assert evaluate() == result
    output = create_campaign(
        purpose="conditioned_laminar_blade_layer",
        selection=dict(source="NASA CR-185118 Volume I Tables 13 and 15", research_only=True),
    )
    report = dict(source=identity, nominal=result, tighter=tighter, later_seed=later_seed)
    write_json_new(output / "analysis.json", report)
    print(json.dumps(report, indent=2), flush=True)
    print(output, flush=True)


if __name__ == "__main__":
    main()
