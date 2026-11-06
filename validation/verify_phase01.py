"""Small synthetic resolution campaign, independent axial/radial refinement.

Run: python validation/verify_phase01.py
This is numerical verification, not experimental validation or a release gate.
"""
import copy
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from campaign import create_campaign, write_json_new
from scripts.run_throughflow import build_case
from sm_core import make_env


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-iterations", type=int, default=400)
    parser.add_argument("--axial", type=int, nargs="+", default=[1, 2, 4, 8, 16])
    parser.add_argument("--radial", type=int, nargs="+", default=[11, 21, 41])
    args = parser.parse_args()
    if not 10 <= args.max_iterations <= 3000:
        parser.error("max iterations must lie in [10, 3000]")
    if any(not 1 <= n <= 16 for n in args.axial) or any(not 5 <= n <= 41 for n in args.radial):
        parser.error("axial subdivisions must lie in [1, 16], radial surfaces in [5, 41]")
    cases = [("axial", 11, n) for n in dict.fromkeys(args.axial)]
    cases += [("radial", n, 1) for n in dict.fromkeys(args.radial)]
    path = create_campaign(purpose="phase01_synthetic_verification", selection=cases)
    print(path, flush=True)
    env = make_env("turbomachinery_throughflow")
    design, task = build_case(1)
    summaries = []
    for axis, surfaces, subdivisions in cases:
        effective_task = copy.deepcopy(task)
        effective_task["numerics"].update(stream_surfaces=surfaces, duct_subdivisions=subdivisions,
                                          max_iterations=args.max_iterations)
        result = env.evaluate("resolution", effective_task, "synthetic_one_stage", design)
        record = dict(axis=axis, surfaces=surfaces, subdivisions=subdivisions,
                      design=design, task=effective_task, evaluation=result.model_dump(mode="json"))
        write_json_new(path / "results" / ("{}_{}_{}.json".format(axis, surfaces, subdivisions)), record)
        summaries.append(record)
        print(axis, surfaces, subdivisions, result.status, result.metrics.get("pressure_ratio_total"), flush=True)
    lines = ["# Synthetic resolution verification", "", "See manifest.json and results/ for frozen inputs and source.", "",
             "| Axis | Surfaces | Duct subdivisions | Status | PR | Isentropic efficiency |", "|---|---|---|---|---|---|"]
    for r in summaries:
        e = r["evaluation"]
        lines.append("| {} | {} | {} | {} | {} | {} |".format(r["axis"], r["surfaces"], r["subdivisions"], e["status"],
                      e["metrics"].get("pressure_ratio_total"), e["metrics"].get("efficiency_isentropic")))
    lines += ["", "These are sensitivity observations on one synthetic design, not general grid-independence evidence.",
              "Blade rows remain single gaps. Axial refinement changes ducts only."]
    with (path / "resolution.md").open("x", encoding="utf-8") as stream:
        stream.write("\n".join(lines) + "\n")
    if any(r["evaluation"]["status"] != "success" for r in summaries):
        raise SystemExit("Some resolutions failed; retain their diagnostics and do not claim convergence.")


if __name__ == "__main__":
    main()
