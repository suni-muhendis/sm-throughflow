"""Random, smooth perturbations of a whole design, shared by the robustness and search studies."""
import copy

import numpy as np

from sweeps import _span

SPAN = np.linspace(0.0, 1.0, 11)

#: Perturbation sizes at unit amplitude.
SIZES = {"stagger_deg": 3.0, "camber_deg": 3.0, "chord": 0.10, "t_c": 0.15, "blades": 0.15, "clearance_span": 0.01}


def _smooth(rng, size):
    """A random linear-plus-quadratic distribution over the span, peak magnitude about ``size``."""
    a, b, c = rng.uniform(-1.0, 1.0, 3)
    shape = a + b * (SPAN - 0.5) * 2.0 + c * ((SPAN - 0.5) * 2.0) ** 2
    return size * shape / max(1.0, np.max(np.abs(shape)))


def perturb(design, rng, amplitude=1.0, vector=None):
    """A perturbed copy of ``design``. With ``vector`` (a dict of per-row parameter draws) the
    perturbation is that vector; otherwise one is drawn from ``rng``. Returns (design, vector)."""
    d = copy.deepcopy(design)
    vec = vector if vector is not None else []
    for k, row in enumerate(d["rows"]):
        if vector is None:
            v = {"stagger": _smooth(rng, SIZES["stagger_deg"]), "camber": _smooth(rng, SIZES["camber_deg"]),
                 "chord": _smooth(rng, SIZES["chord"]), "t_c": _smooth(rng, SIZES["t_c"]),
                 "blades": float(rng.uniform(-1.0, 1.0)) * SIZES["blades"],
                 "clearance": float(rng.uniform(-1.0, 1.0)) * SIZES["clearance_span"]}
            vec.append(v)
        else:
            v = vector[k]
        s_in = np.sign(np.mean(row["metal_angle_in_deg"])) or 1.0
        turn = 1.0 if np.mean(np.asarray(row["metal_angle_in_deg"]) - np.asarray(row["metal_angle_out_deg"])) > 0 else -1.0
        k_in = np.asarray(row["metal_angle_in_deg"]) + s_in * amplitude * v["stagger"]
        k_out = np.asarray(row["metal_angle_out_deg"]) + s_in * amplitude * v["stagger"] - turn * amplitude * v["camber"]
        row["metal_angle_in_deg"] = [float(x) for x in k_in]
        row["metal_angle_out_deg"] = [float(x) for x in k_out]
        row["chord_m"] = [float(c * (1.0 + amplitude * e)) for c, e in zip(row["chord_m"], v["chord"])]
        row["thickness_to_chord"] = [float(t * (1.0 + amplitude * e)) for t, e in zip(row["thickness_to_chord"], v["t_c"])]
        row["blade_count"] = max(2, int(round(row["blade_count"] * (1.0 + amplitude * v["blades"]))))
        change = amplitude * float(v["clearance"]) * _span(d, row)  # added to the baseline gap, never below zero
        for key in ("tip_clearance_m", "hub_clearance_m"):
            if row.get(key) is not None and change != 0.0:
                row[key] = max(0.0, float(row[key]) + change)
    return d, vec
