"""A repeating-stage subsonic axial compressor in the v2 contracts, solved with simulator v5.

The blading is a free-vortex design (r C_theta constant across the span)
with a fixed allowance for incidence and deviation; it is a reference case
for the environment, not a validated machine.

    python scripts/run_throughflow_v2.py --stages 3
"""
import argparse
import json
import math

import numpy as np

SPAN = np.linspace(0.0, 1.0, 11)


def build_case(stages=3, rpm=4775.0, mass_flow=80.0, axial_velocity=150.0, work_coefficient=0.30, chord=0.05, gap=0.02,
               stream_surfaces=11, inlet_guide_vane=False):
    omega = rpm * 2.0 * math.pi / 60.0
    hub_in, hub_out, tip_in, tip_out = 0.30, 0.33, 0.50, 0.485
    k = work_coefficient * omega * 0.4 ** 2  # r C_theta added by each rotor at the reference radius 0.4 m

    def angles(r, swirl_in, swirl_out, frame_speed):
        w_in = np.degrees(np.arctan2(swirl_in / r - frame_speed * r, axial_velocity))
        w_out = np.degrees(np.arctan2(swirl_out / r - frame_speed * r, axial_velocity))
        return w_in, w_out

    rows, x = [], 0.08
    length_guess = 0.08 + stages * 2 * (0.05 + gap) + 0.1
    hub = lambda z: hub_in + (hub_out - hub_in) * z / length_guess
    tip = lambda z: tip_in + (tip_out - tip_in) * z / length_guess

    def add(row_id, stage_id, row_type, k_in, k_out, blade_count):
        nonlocal x
        stagger = 0.5 * (k_in + k_out)  # circular arc
        width = float(np.max(chord * np.abs(np.cos(np.radians(stagger)))))
        row = {
            "row_id": row_id, "row_type": row_type, "leading_edge_axial_m": round(x, 6), "trailing_edge_axial_m": round(x + width, 6),
            "blade_count": blade_count, "profile": "naca65", "camberline": "naca65",
            "metal_angle_in_deg": [round(float(v), 4) for v in k_in], "metal_angle_out_deg": [round(float(v), 4) for v in k_out],
            "chord_m": [chord] * 11, "thickness_to_chord": [0.07] * 11,
        }
        if stage_id is not None:
            row["stage_id"] = stage_id
        if row_type == "rotor":
            row["tip_clearance_m"] = 4e-4
        else:
            row["hub_clearance_m"] = 4e-4
        rows.append(row)
        x += width + gap

    def radius(span):
        z = x + 0.02
        return hub(z) + span * (tip(z) - hub(z))

    swirl = 0.0
    if inlet_guide_vane:
        r = radius(SPAN)
        a_out = np.degrees(np.arctan2(k / r, axial_velocity))
        add("IGV", None, "stator", np.zeros(11), a_out + 3.0 * np.sign(a_out), 40)
        swirl = k
    for s in range(stages):
        r = radius(SPAN)
        b_in, b_out = angles(r, swirl, swirl + k, omega)
        add("R{}".format(s + 1), "stage{}".format(s + 1), "rotor", b_in + 2.0, b_out + 6.0, 36)
        r = radius(SPAN)
        # Each stator returns the flow to the stage's inlet swirl; the last one to axial.
        target = 0.0 if s == stages - 1 else swirl
        a_in, a_out = angles(r, swirl + k, target, 0.0)
        add("S{}".format(s + 1), "stage{}".format(s + 1), "stator", a_in - 2.0, a_out - 6.0, 44)
        swirl = target
    length = x + 0.08
    design = {
        "schema_version": "throughflow_design_v2", "machine_type": "compressor", "flow_path": "axial",
        "passage": {"stations": [
            {"axial_m": 0.0, "hub_radius_m": hub_in, "shroud_radius_m": tip_in},
            {"axial_m": round(length, 6), "hub_radius_m": round(hub(length), 6), "shroud_radius_m": round(tip(length), 6)},
        ]},
        "rows": rows,
    }
    task = {
        "task_schema_version": "throughflow_task_v2",
        "inlet": {"total_pressure_pa": 101325.0, "total_temperature_k": 288.15, "flow_angle_deg": 0.0},
        "operating_points": [{"name": "design", "mass_flow_kg_s": mass_flow, "shaft_speed_rpm": rpm}],
        "numerics": {"stream_surfaces": stream_surfaces},
    }
    return design, task


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--stages", type=int, default=3)
    parser.add_argument("--json", action="store_true", help="print the design and task instead of solving")
    args = parser.parse_args()
    design, task = build_case(args.stages)
    if args.json:
        print(json.dumps({"design": design, "task": task}, indent=2))
        return
    from sm_core import make_env

    result = make_env("turbomachinery_throughflow").evaluate("v2-demo", task, "repeating-{}".format(args.stages), design)
    print(result.status, result.simulator_version, result.error_message or "")
    for key in ("pressure_ratio_total", "efficiency_polytropic", "power_W", "exit_blockage", "min_stall_margin", "max_loss_coefficient", "solver_iterations"):
        if key in result.metrics:
            print("{:28s} {:.6g}".format(key, result.metrics[key]))


if __name__ == "__main__":
    main()
