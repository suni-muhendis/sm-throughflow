"""Check the wake reference against a published low-speed DCA reduction."""
import csv
from dataclasses import asdict
import json

import numpy as np

from validation.campaign import ROOT, create_campaign, write_json_new
from validation.wake_flux_reference import reduce_wake


def evaluate():
    source = ROOT / "validation/cases/nasa_dca_cascade_wake/CR185118_vol2_table80.csv"
    with source.open(newline="") as stream:
        reader = csv.reader(stream)
        for _ in range(3):
            next(reader)
        samples = np.array([row[:3] for row in reader], dtype=float)
    assert samples.shape == (81, 3)
    y, velocity, _ = samples.T
    y = y / 1000
    assert np.all(np.diff(y) > 0)
    pitch = .2286 / 2.14 * np.cos(np.deg2rad(-.6))
    # Trapezoidal integration of the measured profile, with the unsurveyed
    # portion assigned the edge state. No curve is fitted to measured loss.
    segments = np.diff(y)
    weights = np.r_[segments[0], segments[:-1] + segments[1:], segments[-1]] / 2
    weights = np.r_[weights, pitch - weights.sum()]
    rho, gas_constant, gamma = 1.205, 287.05, 1.4
    cp = gamma * gas_constant / (gamma - 1)
    head = .5 * rho * 33.28**2
    comparisons = {}
    for count in (5, 10, 15):
        edge_velocity = np.mean(np.r_[velocity[:count], velocity[-count:]])
        speeds = np.r_[velocity, edge_velocity]
        edge_temperature = 300. - edge_velocity**2 / (2 * cp)
        pressure = rho * gas_constant * edge_temperature
        temperature = 300. - speeds**2 / (2 * cp)
        result = reduce_wake(weights, np.full_like(speeds, pressure), temperature,
                             speeds, np.zeros_like(speeds), edge_mass_flux=rho * edge_velocity)
        edge_total_pressure = pressure * (300. / edge_temperature)**(cp / gas_constant)
        # Independent low-Mach limit: momentum implies pressure recovery
        # rho Var(u). Energy then gives the mixed total-pressure deficit.
        mean_speed = np.average(speeds, weights=weights)
        variance = np.average((speeds - mean_speed)**2, weights=weights)
        incompressible_loss = .5 * rho * (edge_velocity**2 - mean_speed**2 - 2 * variance) / head
        # CR-185118 Volume I, printed p. 33. This relation applies to
        # the survey plane. It uses a wake-shape approximation.
        speed_ratio = speeds / edge_velocity
        displacement_over_pitch = np.dot(weights, 1 - speed_ratio) / pitch
        momentum_over_pitch = np.dot(weights, speed_ratio * (1 - speed_ratio)) / pitch
        shape_factor = displacement_over_pitch / momentum_over_pitch
        lieblein_roudebush = (
            2 * momentum_over_pitch * (np.cos(np.deg2rad(44.5)) / np.cos(np.deg2rad(-.6)))**2
            * (1 - displacement_over_pitch)**-3 * 2 * shape_factor / (3 * shape_factor - 1)
        )
        comparisons[str(count)] = dict(
            edge_speed=float(edge_velocity), state=asdict(result),
            edge_to_survey_loss=float((edge_total_pressure - result.mass_average_total_pressure) / head),
            edge_to_mixed_loss=float((edge_total_pressure - result.total_pressure) / head),
            mass_average_to_mixed_pressure_difference=float(
                (result.mass_average_total_pressure - result.total_pressure) / head
            ),
            incompressible_loss=float(incompressible_loss),
            incompressible_displacement_thickness_m=float(displacement_over_pitch * pitch),
            incompressible_momentum_thickness_m=float(momentum_over_pitch * pitch),
            lieblein_roudebush_survey_loss=float(lieblein_roudebush),
        )
    return dict(
        measured_samples=len(y), measured_width_m=float(y[-1] - y[0]),
        assumed_projected_pitch_m=float(pitch), comparisons=comparisons,
        reported_loss_at_same_plane_from_velocity_reduction=.018,
        reported_measured_blade_passage_loss=.028,
        profile_is_prescribed=True, prediction_qualified=False,
    )


def main():
    result = evaluate()
    output = create_campaign(
        purpose="planar_wake_flux_low_mach_data_reduction",
        selection=dict(source="NASA CR-185118 Table 80 and Volume I Table 2", research_only=True),
    )
    write_json_new(output / "analysis.json", result)
    print(json.dumps(result, indent=2), flush=True)
    print(output, flush=True)


if __name__ == "__main__":
    main()
