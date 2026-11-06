"""Compare a common-edge junction and free-wake momentum to NASA DCA data."""
import csv
import json

import numpy as np

from validation.campaign import ROOT, create_campaign, write_json_new
from validation.probe_blade_layer import read_table
from validation.probe_compressible_diffusion import BASELINE
from validation.probe_wake_flux import evaluate as evaluate_profile
from validation.verify_family_source_v14 import verify
from validation.wake_junction_reference import WakeMoments, join, march_momentum, pressure_deficits

NU = 1.5e-5  # CR-185118 Vol. I, nomenclature, 0.150 cm²/sec.
CHORD = 0.2286

# First and last velocity samples of Vol. II tables 77–80, read visually
# from printed pp. 113–120. These are edge proxies, not a reduction of
# all of the profiles or an estimate of statistical uncertainty.
EDGE_SAMPLES = (
    ("106.0", 77, ("26.30", "25.49")),
    ("109.7", 78, ("25.77", "25.28")),
    ("131.9", 79, ("24.86", "24.72")),
    ("152.6", 80, ("24.06", "23.95")),
)


def evaluate():
    rows = read_table(15)
    wake = {row[0]: row for row in rows if row[1] == "W"}
    x = np.array([float(p) for p, _, _ in EDGE_SAMPLES]) * CHORD / 100
    speed_samples = np.array([samples for _, _, samples in EDGE_SAMPLES], dtype=float)
    reported_h, reported_energy_h, reported_re = np.array(
        [wake[p][2:5] for p, _, _ in EDGE_SAMPLES], dtype=float,
    ).T
    speed = speed_samples.mean(axis=1)
    measured_theta = NU * reported_re / speed
    reynolds_marches = {}
    for name, profile in (("mean", speed), ("first", speed_samples[:, 0]), ("last", speed_samples[:, 1])):
        theta = march_momentum(x, profile, reported_h, NU * reported_re[0] / profile[0])
        reynolds_marches[name] = (theta * profile / NU).tolist()
    # Solve the final speed ratio needed to match the measured Re drop
    # with a log-linear speed history. The H history remains measured.
    log_speed_response = march_momentum(x, np.exp((x - x[0]) / (x[-1] - x[0])), reported_h, 1.)
    exponent = np.log(log_speed_response[-1]) + 1
    implied_speed_ratio = float(np.exp(np.log(reported_re[-1] / reported_re[0]) / exponent))

    junction_rows = [next(row for row in rows if row[0] == x and row[1] == side)
                     for x, side in (("98.4", "P"), ("97.6", "S"))]
    # Express both survey moments at the same nominal edge speed to
    # expose the additive junction's budget. This does not match the
    # unmeasured edge states at the actual trailing-edge junction.
    inputs = []
    for row in junction_rows:
        shape, energy_h, reynolds = map(float, row[2:5])
        theta = NU * reynolds / speed[0]
        inputs.append(WakeMoments(shape * theta, theta, energy_h * theta))
    junction = {}
    for gap in (0., 2 * 0.0009144):
        entry = join(*inputs, dead_gap=gap)
        junction[str(gap)] = dict(
            theta_m=float(entry.momentum), displacement_m=float(entry.displacement),
            kinetic_thickness_m=float(entry.kinetic_energy),
            common_edge_reynolds=float(entry.momentum * speed[0] / NU),
        )

    # Use the existing raw far wake to compare the moment-only loss
    # reduction with the independently computed perfect-gas reduction.
    source = ROOT / "validation/cases/nasa_dca_cascade_wake/CR185118_vol2_table80.csv"
    with source.open(newline="") as stream:
        rows = list(csv.reader(stream))[3:]
    y, u = np.array([row[:2] for row in rows], dtype=float).T
    profile = evaluate_profile()
    width = profile["assumed_projected_pitch_m"]
    edge = profile["comparisons"]["10"]["edge_speed"]
    q = u / edge
    y /= 1000
    moments = WakeMoments(*(float(np.trapezoid(integrand, y)) for integrand in (
        1 - q, q * (1 - q), q * (1 - q**2),
    )))
    survey, mixed = pressure_deficits(moments, width)
    scale = (edge / 33.28)**2
    return dict(
        edge_samples=EDGE_SAMPLES, mean_edge_speed=speed.tolist(),
        reported_shape=reported_h.tolist(), reported_energy_shape=reported_energy_h.tolist(),
        reported_reynolds=reported_re.tolist(), measured_theta_m=measured_theta.tolist(),
        initial_edge_speed=speed[0], reynolds_marches=reynolds_marches,
        measured_mean_speed_ratio=float(speed[-1] / speed[0]),
        implied_speed_ratio_with_log_linear_history=implied_speed_ratio,
        common_edge_junction=junction,
        far_wake_loss=dict(
            incompressible_survey=float(survey * scale), incompressible_mixed=float(mixed * scale),
            perfect_gas_survey=profile["comparisons"]["10"]["edge_to_survey_loss"],
            perfect_gas_mixed=profile["comparisons"]["10"]["edge_to_mixed_loss"],
        ),
    )


def main():
    identity = verify(BASELINE)
    result = evaluate()
    assert evaluate() == result
    output = create_campaign(
        purpose="nasa_dca_wake_junction_and_momentum_compatibility",
        selection=dict(research_only=True, source="NASA CR-185118 Vol. I Table 15 and Vol. II Tables 77–80",
                       training_label_qualified=False),
    )
    write_json_new(output / "analysis.json", dict(source=identity, result=result))
    print(json.dumps(result, indent=2), flush=True)
    print(output, flush=True)


if __name__ == "__main__":
    main()
