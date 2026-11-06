"""Low-speed pressure comparison with the NASA CR-185118 DCA cascade."""
import json

import numpy as np

from validation.blade_layer_reference import march, march_from_stagnation
from validation.campaign import create_campaign, write_json_new
from validation.periodic_cascade_reference import solve
from validation.probe_blade_layer import evaluate as evaluate_measured_edge, read_table
from validation.probe_compressible_diffusion import BASELINE
from validation.verify_family_source_v14 import verify


def geometry(panels_per_side):
    """Build two circles and two rounded edges from Appendix A and Table 1.

    Keep the printed centres and edge radii. Recompute the large radii to
    restore exact tangency lost in the printed rounding of the radii.
    """
    half_chord, edge_radius = 0.1143, 0.0009144
    pitch, stagger = 0.1068, np.deg2rad(20.5)
    angle = np.linspace(0, np.pi, panels_per_side + 1)
    fraction = (1 - np.cos(angle)) / 2
    centres = (0.2197, 0.1495)
    radii = [np.hypot(half_chord, y) + sign * edge_radius
             for y, sign in zip(centres, (-1, 1))]
    ends = [half_chord * radius / np.hypot(half_chord, centre)
            for centre, radius in zip(centres, radii)]
    sides = []
    for centre, radius, end in zip(centres, radii, ends):
        x = (2 * fraction - 1) * end
        sides.append(x + 1j * (np.sqrt(radius**2 - x**2) - centre))
    pressure, suction = sides

    def edge(start, end, centre):
        a, b = np.angle([start - centre, end - centre])
        count = panels_per_side // 6 + 8
        return centre + edge_radius * np.exp(1j * np.linspace(a, a + (b - a) % (2 * np.pi), count + 1)[1:-1])

    trailing = edge(pressure[-1], suction[-1], half_chord)
    leading = edge(suction[0], pressure[0], -half_chord)
    z = np.r_[pressure, trailing, suction[::-1], leading, pressure[0]] * np.exp(1j * stagger)
    return np.c_[z.real, z.imag], pitch, stagger, (panels_per_side - 1, panels_per_side + len(trailing) + 1), radii


def layer_history(result, chord_percent, kutta_pair, total_temperature, total_pressure):
    """Trace each wall out of the leading-edge zero in the computed speed."""
    speeds = result.tangential_speed
    candidates = [
        i for i in range(len(speeds))
        if speeds[i] < 0 <= speeds[(i + 1) % len(speeds)] and chord_percent[i] < 5
    ]
    if len(candidates) != 1:
        return dict(status="leading_edge_stagnation_ambiguous", candidates=len(candidates))
    i = candidates[0]
    j = (i + 1) % len(speeds)
    fraction = -speeds[i] / (speeds[j] - speeds[i])
    origin = (1 - fraction) * result.centres[i] + fraction * result.centres[j]
    origin_percent = (1 - fraction) * chord_percent[i] + fraction * chord_percent[j]
    report = dict(status="stagnation_found", stagnation_percent_chord=float(origin_percent))
    n = len(speeds)
    for side, start, stop, step in (
        ("pressure", j, kutta_pair[0], 1), ("suction", i, kutta_pair[1], -1),
    ):
        indices = (start + step * np.arange((step * (stop - start)) % n + 1)) % n
        points = np.vstack([origin, result.centres[indices]])
        arc = np.r_[0., np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))]
        velocity = np.r_[0., step * speeds[indices]]
        try:
            layer = march_from_stagnation(arc, velocity, total_temperature=total_temperature,
                                          total_pressure=total_pressure)
        except (ValueError, RuntimeError) as exc:
            report[side] = dict(status="march_unavailable", error=str(exc))
            continue
        report[side] = dict(status="zero_shear" if layer.separated else "attached",
                            last_percent_chord=float(np.interp(
                                layer.arc[-1], arc, np.r_[origin_percent, chord_percent[indices]],
                            )), last_displacement_m=float(layer.displacement_thickness[-1]))
    return report


def evaluate(panels, *, kutta_chord=None, run_layers=True):
    contour, pitch, stagger, kutta, radii = geometry(panels)
    side_indices = np.arange(kutta[1], kutta[1] + panels)[::-1]
    if kutta_chord is not None:
        centres = (contour[1:] + contour[:-1]) / 2
        x = 100 * ((centres[:, 0] + 1j * centres[:, 1]) * np.exp(-1j * stagger)).real / 0.2286 + 50
        kutta = tuple(int(idx[np.argmin(abs(x[idx] - kutta_chord))])
                      for idx in (np.arange(panels), side_indices))
    result = solve(contour, pitch, 33.28, 44.5, kutta)
    coordinates = result.centres[:, 0] + 1j * result.centres[:, 1]
    chord_percent = 100 * ((coordinates * np.exp(-1j * stagger)).real / 0.2286 + 0.5)
    table = read_table(13)
    pressures = {}
    for name, offset, indices in (
        ("pressure", 0, np.arange(panels)),
        ("suction", 3, side_indices),
    ):
        measured = np.array([[float(r[offset]), float(r[offset + 1])] for r in table if r[offset]])
        predicted = np.interp(measured[:, 0], chord_percent[indices], result.pressure_coefficient[indices])
        pressures[name] = dict(
            rms_cp_error=float(np.sqrt(np.mean((predicted - measured[:, 1])**2))),
            samples=np.c_[measured, predicted].tolist(),
        )
    delta = np.diff(contour, axis=0)
    normal_times_length = np.c_[delta[:, 1], -delta[:, 0]]
    force = -0.5 * 33.28**2 * result.pressure_coefficient @ normal_times_length
    ux = 33.28 * np.cos(np.deg2rad(44.5))
    vy = 33.28 * np.sin(np.deg2rad(44.5))
    vy_out = vy + result.circulation / pitch
    momentum_force = np.array([0.5 * pitch * (vy_out**2 - vy**2), ux * pitch * (vy - vy_out)])
    restart = None
    if run_layers:
        # Attribution only. Bypass the unresolved nose layer using the
        # same observed seed as the earlier measured-edge experiment.
        measured_edge = evaluate_measured_edge()
        xy = result.centres[side_indices]
        arc = np.r_[0., np.cumsum(np.linalg.norm(np.diff(xy, axis=0), axis=1))]
        start = np.interp(10.4, chord_percent[side_indices], arc)
        layer = march(
            arc, -result.tangential_speed[side_indices],
            theta0=measured_edge["seed_re_theta"] * 1.5e-5 / measured_edge["start_velocity"],
            hk0=measured_edge["seed_hk"], total_temperature=measured_edge["total_temperature_K"],
            total_pressure=measured_edge["total_pressure_Pa"], sample_at=[start, arc[-1]],
        )
        restart = dict(
            seed_percent_chord=10.4,
            predicted_edge_zero_shear_percent_chord=float(np.interp(
                layer.arc[-1], arc, chord_percent[side_indices],
            )) if layer.separated else None,
            measured_edge_zero_shear_percent_chord=measured_edge["predicted_zero_shear_percent_chord"],
        )
    return dict(
        panels_per_side=panels, adjusted_radii_m=radii, normal_residual=result.normal_residual,
        net_source=result.net_source, predicted_outlet_angle_deg=result.exit_angle_deg,
        measured_outlet_angle_deg=-0.6, pressure_comparison=pressures,
        pressure_force_per_density=force.tolist(), momentum_force_per_density=momentum_force.tolist(),
        relative_force_residual=float(np.linalg.norm(force - momentum_force) / np.linalg.norm(momentum_force)),
        kutta_percent_chord=chord_percent[list(kutta)].tolist(),
        conditioned_layers=layer_history(result, chord_percent, kutta, 300., 104000.) if run_layers else None,
        suction_restart=restart,
    )


def main():
    identity = verify(BASELINE)
    results = [evaluate(n) for n in (48, 96, 192, 384, 768)]
    assert evaluate(96) == results[1]
    sensitivity = [evaluate(192, kutta_chord=x, run_layers=False) for x in (98., 99.)]
    output = create_campaign(
        purpose="periodic_dca_surface_pressure_reference",
        selection=dict(research_only=True, source="NASA CR-185118 Volume I Table 13",
                       training_label_qualified=False),
    )
    write_json_new(output / "analysis.json", dict(source=identity, results=results, kutta_sensitivity=sensitivity))
    for row in results + sensitivity:
        print(json.dumps({**row, "pressure_comparison": {
            key: value["rms_cp_error"] for key, value in row["pressure_comparison"].items()
        }}), flush=True)
    print(output, flush=True)


if __name__ == "__main__":
    main()
