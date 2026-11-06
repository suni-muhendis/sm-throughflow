"""Screen shock closures against measured total rotor loss at v16 anchors."""
import hashlib
import json

import numpy as np

from sm_throughflow.solver.gas import PerfectGas
from validation.campaign import ROOT, create_campaign, write_json_new
from validation.phase3 import V
from validation.phase3_rows import geometry_file, measured_states, reconstructed_loss, row_model
from validation.probe_compressible_diffusion import BASELINE
from validation.verify_family_source_v14 import verify
from sm_throughflow.solver.rows import ExitGeometry

CONDITIONED = ROOT / "validation/campaigns/20261105T135347389077Z_slc_aungier_experimental_v16"


def compare():
    results = []
    for anchor in json.loads((CONDITIONED / "results.json").read_text()):
        stage, reading = anchor["stage"], anchor["reading"]
        case = V.CASES[f"nasa_stage{stage}"]()
        point = next(p for p in case.measured_points(100) if p["reading"] == reading)
        inlet, exit, measurements = measured_states(
            case.rotor_elements[reading],
            V.L.read_geometry(geometry_file(case.case_id, 0)),
            point["rpm"], point["mass_flow"],
        )
        gas = PerfectGas()
        rebuilt = reconstructed_loss(inlet, exit, gas)
        model = row_model(case.design, 0, point["rpm"], gas)
        diagnostics = model(inlet, exit, ExitGeometry(exit.t, exit.y, exit.r, exit.z)).diagnostics
        points = [p for p in anchor["points"] if p["measured_span"]]
        for index, (probe, row) in enumerate(zip(points, measurements, strict=True), start=1):
            assert np.isclose(probe["inlet_mach"], diagnostics["relative_inlet_mach"][index], rtol=1e-13)
            assert np.isclose(probe["baseline_loss"], diagnostics["pointwise_shock_loss"][index], rtol=1e-13)
            span = row.get("PERCENT SPAN", V.RP_SPAN[int(row["RP"])])
            printed = row.get("LOSS COEFF TOT")
            # Larger of the two readings is a conservative screen. The
            # reconstruction difference is not a measurement uncertainty bound.
            total = max(rebuilt[index], printed) if printed is not None else rebuilt[index]
            record = dict(
                stage=stage, reading=reading, span_from_tip=span, core=15 <= span <= 85,
                avdr=probe["avdr"], regime=probe.get("regime"), printed_total=printed,
                reconstructed_total=float(rebuilt[index]), screened_total=float(total),
            )
            for name, shock in (
                ("v16_pointwise", probe["baseline_loss"]),
                ("v16_integrated", diagnostics["shock_loss"][index]),
                ("passage_r2", probe.get("loss")),
            ):
                record[name] = None if shock is None else dict(
                    shock=float(shock), remaining=float(total - shock),
                )
            results.append(record)
    return results


def main():
    identity = verify(BASELINE)
    verify(CONDITIONED)
    results = compare()
    summary = {}
    for group, rows in (("all_measured", results), ("core", [r for r in results if r["core"]])):
        summary[group] = {}
        for model in ("v16_pointwise", "v16_integrated", "passage_r2"):
            evaluated = [r[model]["remaining"] for r in rows if r[model] is not None]
            summary[group][model] = dict(
                evaluated=len(evaluated), unavailable=len(rows) - len(evaluated),
                over_total=sum(r < 0 for r in evaluated), minimum_remaining=min(evaluated),
            )
    source = CONDITIONED / "results.json"
    output = create_campaign(
        purpose="conditioned_shock_loss_budget_screen",
        selection=dict(
            baseline=BASELINE.name, conditioned=CONDITIONED.name,
            conditioned_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            research_only=True, training_label_qualified=False,
        ),
    )
    write_json_new(output / "analysis.json", dict(source=identity, summary=summary, points=results))
    print(json.dumps(summary, indent=2), flush=True)
    print(output, flush=True)


if __name__ == "__main__":
    main()
