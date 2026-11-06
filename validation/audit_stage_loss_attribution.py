"""Attribute the v16 Stage 35–38 efficiency differences without fitting."""
from hashlib import sha256
import json

import numpy as np

from sm_throughflow.contracts import ThroughflowTaskV2
from sm_throughflow.solver.aungier_row import smooth_loss
from sm_throughflow.solver.gas import PerfectGas
from sm_throughflow.solver.rows import ExitGeometry
from validation.campaign import create_campaign, write_json_new
from validation.phase3_rows import V, geometry_file, measured_states, reconstructed_loss, row_model
from validation.probe_compressible_diffusion import BASELINE
from validation.screen_candidate_v16 import ANCHORS
from validation.verify_family_source_v14 import verify


PAIRS = ((35, 36), (37, 38), (35, 37), (36, 38))


def efficiency_budget(values, exponent):
    """NASA energy-average pressure ratios on a common rotor work basis."""
    work = values["rotor_tr"] - 1
    if work <= 0:
        raise ValueError("a positive rotor temperature rise is required")
    rotor, stage = (values[key] ** exponent for key in ("rotor_pr", "stage_pr"))
    rotor_eta = (rotor - 1) / work
    downstream_penalty = (rotor - stage) / work
    stage_eta = (stage - 1) / work
    return dict(rotor_eta=rotor_eta, downstream_penalty=downstream_penalty, stage_eta=stage_eta,
                reported_rotor_eta=values["rotor_eta"], reported_stage_eta=values["stage_eta"],
                stage_reporting_residual=values["stage_eta"] - stage_eta)


def core_average(values, tube_flows, core):
    """Average only tubes bounded by two measured core samples."""
    interior = core[:-1] & core[1:]
    if not np.any(interior):
        raise ValueError("the traverse does not contain a core tube")
    return float(np.average((values[:-1][interior] + values[1:][interior]) / 2,
                            weights=tube_flows[interior]))


def postprocess_loss(loss, head, cap, smoothing):
    capped = np.minimum(loss, cap)
    return smooth_loss(capped * head) / head if smoothing else capped


def shock_scale_curve(nonshock, shock, head, cap, smoothing, tube_flows, core):
    """Exact conditioned mean versus a nonnegative direct-shock multiplier."""
    clipping = (shock > 0) & (nonshock < cap)
    scales = np.unique(np.r_[0., 1., (cap - nonshock[clipping]) / shock[clipping]])
    means = []
    for scale in scales:
        loss = postprocess_loss(nonshock + scale * shock, head, cap, smoothing)
        means.append(core_average(loss, tube_flows, core))
    # The loss is affine between clipping knots and constant after the last.
    return dict(scales=scales.tolist(), means=means)


def maximum_shock_scale_difference(lower, higher):
    """Bound the loss delta for a common scale by checking the union of knots."""
    scales = np.union1d(lower["scales"], higher["scales"])
    delta = (np.interp(scales, higher["scales"], higher["means"])
             - np.interp(scales, lower["scales"], lower["means"]))
    i = int(np.argmax(delta))
    return dict(loss_delta=float(delta[i]), scale=float(scales[i]), zero_scale_delta=float(delta[0]))


def conditioned_budget(case, reading, point, index, gas):
    elements = (case.rotor_elements, case.stator_elements)[index][reading]
    geometry = V.L.read_geometry(geometry_file(case.case_id, index))
    rpm, mass = point["rpm"], point["mass_flow"]
    inlet, exit, samples = measured_states(elements, geometry, rpm, mass, rotor=index == 0)
    model = row_model(case.design, index, rpm, gas)
    performance = model(inlet, exit, ExitGeometry(exit.t, exit.y, exit.r, exit.z))
    d = performance.diagnostics
    span = np.array([100., *(r.get("PERCENT SPAN", V.RP_SPAN[int(r["RP"])]) for r in samples), 0.])
    core = (15 <= span) & (span <= 85)
    printed = np.array([np.nan, *(r["LOSS COEFF TOT"] for r in samples), np.nan])
    rebuilt = reconstructed_loss(inlet, exit, gas)
    shock = d["shock_loss"]
    profile = d["profile_loss"] - shock
    leakage = d["clearance_loss"] + d["seal_loss"]
    fixed = performance.loss - shock
    head = gas.pressure(inlet.h + .5 * (inlet.Wm**2 + inlet.W_theta**2), inlet.s) - inlet.P
    zero_shock = postprocess_loss(profile + leakage, head, model.max_loss, model.smoothing)
    values = dict(printed=printed, reconstructed=rebuilt, predicted=performance.loss,
                  shock=shock, nonshock_profile=profile, leakage=leakage,
                  limit_and_smoothing=fixed - profile - leakage, fixed_nonshock=fixed,
                  zero_direct_shock=zero_shock)
    means = {name: core_average(a, inlet.tube_mass_flows, core) for name, a in values.items()}
    points = [dict(span_from_tip=float(span[n]), core=bool(core[n]),
                   **{name: float(a[n]) for name, a in values.items()})
              for n in range(1, len(span) - 1)]
    curve = shock_scale_curve(profile + leakage, shock, head, model.max_loss, model.smoothing,
                              inlet.tube_mass_flows, core)
    if not np.isclose(np.interp(1., curve["scales"], curve["means"]), means["predicted"], rtol=1e-13):
        raise RuntimeError("unit shock scale did not reproduce the closure")
    return dict(core_means=means, points=points, direct_shock_scale_curve=curve)


def compare_pair(low, high):
    def difference(key, source):
        return high[source][key] - low[source][key]

    result = {}
    for name in ("measured", "v16"):
        result[name] = {key: difference(key, name) for key in low[name]}
    measured, model = result["measured"], result["v16"]
    result["diagnostic_substitutions"] = dict(
        measured_rotor_only=measured["rotor_eta"] - model["downstream_penalty"],
        measured_downstream_only=model["rotor_eta"] - measured["downstream_penalty"],
    )
    return result


def evaluate(jobs, records):
    outputs = {}
    cases = {f"nasa_stage{s}" for s in ANCHORS}
    for job in jobs:
        if job["case"] not in cases or job["group"] != "coupled":
            continue
        record = records[job["id"]]
        if job["efficiency_temperature_basis"] != "rotor_tr":
            raise ValueError("the attribution requires rotor work as the efficiency denominator")
        entry = dict(classification=record["classification"], speed=job["speed"],
                     measured=efficiency_budget(record["measurement"], 2 / 7))
        if record["converged"]:
            gas = ThroughflowTaskV2.model_validate(job["task"]).gas
            entry["v16"] = efficiency_budget(record["metrics"], gas.gas_constant_j_kg_k / gas.cp_j_kg_k)
        outputs[job["id"]] = entry

    anchors, comparisons = {}, {}
    for representation in ("original", "projected"):
        anchors[representation] = {s: outputs[f"{representation}__nasa_stage{s}_100_{reading}"]
                                   for s, reading in ANCHORS.items()}
        comparisons[representation] = {
            f"{a}-{b}": compare_pair(anchors[representation][a], anchors[representation][b]) for a, b in PAIRS
        }

    rows = {}
    for stage, reading in ANCHORS.items():
        case = V.CASES[f"nasa_stage{stage}"]()
        point = next(p for p in case.measured_points(100) if p["reading"] == reading)
        rows[stage] = {name: conditioned_budget(case, reading, point, index, PerfectGas())
                       for index, name in enumerate(("rotor", "stator"))}
    rotor_comparisons = {}
    for a, b in PAIRS[:2]:
        lower, higher = (rows[s]["rotor"] for s in (a, b))
        delta = {key: higher["core_means"][key] - value for key, value in lower["core_means"].items()}
        bound = maximum_shock_scale_difference(lower["direct_shock_scale_curve"], higher["direct_shock_scale_curve"])
        rotor_comparisons[f"{a}-{b}"] = dict(delta=delta, common_direct_shock_scale_bound=bound)
    return dict(coupled=outputs, anchors=anchors, comparisons=comparisons,
                conditioned_rows=rows, conditioned_rotor_comparisons=rotor_comparisons)


def main():
    identity = verify(BASELINE)
    inputs = [BASELINE / "jobs.json", *sorted((BASELINE / "results").glob("*.json"))]
    raw = {p.relative_to(BASELINE).as_posix(): p.read_bytes() for p in inputs}
    jobs = json.loads(raw["jobs.json"])
    records = {p.stem: json.loads(raw[p.relative_to(BASELINE).as_posix()]) for p in inputs[1:]}
    if len(jobs) != 108 or {j["id"] for j in jobs} != records.keys():
        raise ValueError("expected the complete frozen v16 comparison")
    result = evaluate(jobs, records)
    if result != evaluate(jobs, records):
        raise RuntimeError("the repeated attribution results differ")
    output = create_campaign(
        purpose="v16_stage_35_38_rotor_and_downstream_loss_attribution",
        selection=dict(baseline=BASELINE.name, research_only=True, training_label_qualified=False,
                       inputs_sha256={name: sha256(data).hexdigest() for name, data in raw.items()}),
    )
    write_json_new(output / "analysis.json", dict(source=identity, result=result))
    print(output, flush=True)


if __name__ == "__main__":
    main()
