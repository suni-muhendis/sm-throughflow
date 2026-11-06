"""Repeat the DCA trailing-edge probes with local displacement feedback."""
import json

import numpy as np

from validation.campaign import create_campaign, write_json_new
from validation.cascade_displacement_patch import AttachedPatch, PatchFailure, solve_patches
from validation.periodic_cascade_reference import prepare
from validation.probe_blade_layer import evaluate as evaluate_measured_edge, read_table
from validation.probe_compressible_diffusion import BASELINE
from validation.probe_periodic_cascade import geometry
from validation.verify_family_source_v14 import verify


def evaluate(panels, *, end_percent, kutta_percent=None, measured_edge=None):
    xy, pitch, stagger, kutta, _ = geometry(panels)
    suction = np.arange(kutta[1], kutta[1] + panels + 1)[::-1]
    chord_percent = 100 * ((xy[:, 0] + 1j * xy[:, 1]) * np.exp(-1j * stagger)).real / 0.2286 + 50
    centre_percent = (chord_percent[:-1] + chord_percent[1:]) / 2
    suction_panels = suction[1:]
    if kutta_percent is not None:
        kutta = tuple(int(idx[np.argmin(abs(centre_percent[idx] - kutta_percent))])
                      for idx in (np.arange(panels), suction_panels))
    system = prepare(xy, pitch, 33.28, 44.5, kutta)
    arc = np.r_[0., np.cumsum(system.length[suction_panels])]
    start, end = np.interp([10.4, end_percent], chord_percent[suction], arc)
    if measured_edge is None:
        measured_edge = evaluate_measured_edge()
    patch = AttachedPatch(
        suction, float(start), float(end),
        measured_edge["seed_re_theta"] * 1.5e-5 / measured_edge["start_velocity"], measured_edge["seed_hk"],
    )
    baseline = system.solve()
    record = dict(
        panels_per_side=panels, end_percent=end_percent,
        kutta_percent_chord=centre_percent[list(kutta)].tolist(),
        baseline_exit_angle=baseline.exit_angle_deg, measured_exit_angle=-0.6,
    )
    try:
        result = solve_patches(
            system, (patch,), total_temperature=measured_edge["total_temperature_K"],
            total_pressure=measured_edge["total_pressure_Pa"],
        )
    except PatchFailure as exc:
        return dict(record, status=exc.reason, iterations=exc.iteration, error=str(exc))
    table = read_table(13)
    errors = {}
    for name, indices, column in (("pressure", np.arange(panels), 0), ("suction", suction_panels, 3)):
        taps = np.array([[float(r[column]), float(r[column+1])] for r in table if r[column]])
        old = np.interp(taps[:, 0], centre_percent[indices], baseline.pressure_coefficient[indices])
        new = np.interp(taps[:, 0], centre_percent[indices], result.cascade.pressure_coefficient[indices])
        entry = dict(
            baseline_rms=float(np.sqrt(np.mean((old-taps[:, 1])**2))),
            coupled_rms=float(np.sqrt(np.mean((new-taps[:, 1])**2))),
            taps=np.c_[taps, old, new].tolist(),
        )
        if name == "suction":
            active = (taps[:, 0] >= 10.4) & (taps[:, 0] <= end_percent)
            entry.update(
                active_taps=int(active.sum()),
                baseline_active_rms=float(np.sqrt(np.mean((old[active]-taps[active, 1])**2))),
                coupled_active_rms=float(np.sqrt(np.mean((new[active]-taps[active, 1])**2))),
            )
        errors[name] = entry
    return dict(
        record, status="converged", iterations=result.iterations,
        initial_residual=result.initial_residual, residual=result.residual,
        prescribed_normal_peak_fraction=float(np.max(abs(np.diff(result.flux) / system.length)) / 33.28),
        net_prescribed_flux=float(np.diff(result.flux).sum()), net_source=result.cascade.net_source,
        normal_residual=result.cascade.normal_residual,
        coupled_exit_angle=result.cascade.exit_angle_deg,
        final_patch_displacement_m=float(result.layers[0].displacement_thickness[-1]),
        pressure_comparison=errors,
    )


def main():
    identity = verify(BASELINE)
    measured = evaluate_measured_edge()
    settings = [(96, 30.1, None), (192, 30.1, None), (384, 30.1, None),
                (192, 24.5, None), (192, 30.1, 98.), (192, 30.1, 99.)]
    results = [evaluate(n, end_percent=end, kutta_percent=kutta, measured_edge=measured)
               for n, end, kutta in settings]
    assert evaluate(192, end_percent=30.1, measured_edge=measured) == results[1]
    output = create_campaign(
        purpose="periodic_dca_local_displacement_feedback",
        selection=dict(research_only=True, source="NASA CR-185118 Tables 13 and 15",
                       training_label_qualified=False),
    )
    write_json_new(output / "analysis.json", dict(source=identity, results=results))
    for row in results:
        print(json.dumps(row, default=str) if "pressure_comparison" not in row else json.dumps(
            {**row, "pressure_comparison": {
                side: {k: v for k, v in values.items() if k != "taps"}
                for side, values in row["pressure_comparison"].items()
            }}), flush=True)
    print(output, flush=True)


if __name__ == "__main__":
    main()
