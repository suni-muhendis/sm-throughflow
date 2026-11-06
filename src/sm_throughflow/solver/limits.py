"""Physical evidence kept separate from iterative feasibility.

The uniform-inlet bound uses the perfect-gas sonic mass flux (NASA Glenn,
https://www.grc.nasa.gov/www/k-12/airplane/mflchk.html, equation 10 at M=1).
No downstream iterate or empirical loss is used to establish that upper bound.
"""
import math

import numpy as np

from .errors import SolverError


def inlet_capacity(flow):
    """Conservative upper bound; None for nonuniform totals or prescribed swirl.

    Surface area includes an inclined quasi-normal. Dropping cos(eps) <= 1
    can only increase capacity. With endwalls, use unblocked area rather than
    trusting an iterated blockage. This is an upper bound, not a choke prediction.
    """
    if (np.size(flow.inlet.P0) != 1 or np.size(flow.inlet.T0) != 1
            or flow.inlet.r_c_theta is not None or np.size(flow.inlet.alpha_deg) > 1):
        return None
    pressure, temperature = float(np.ravel(flow.inlet.P0)[0]), float(np.ravel(flow.inlet.T0)[0])
    angle = 0.0 if flow.inlet.alpha_deg is None else float(np.ravel(flow.inlet.alpha_deg)[0])
    if pressure <= 0 or temperature <= 0 or not -90 < angle < 90:
        return None
    gamma, gas_r = flow.gas.gamma, flow.gas.R
    flux = pressure / math.sqrt(temperature) * math.sqrt(gamma / gas_r)
    flux *= (2 / (gamma + 1)) ** ((gamma + 1) / (2 * (gamma - 1)))
    last = min((row.inlet for row in flow.rows), default=flow.qn.count - 1) if flow.mixing is None else 0
    bounds = []
    for q in range(last + 1):
        area = math.pi * float(flow.qn.r_hub[q] + flow.qn.r_shroud[q]) * float(flow.qn.length[q])
        open_fraction = 1.0 if flow.endwall is not None else float(flow.blockage[q])
        # Only the inlet angle is prescribed. Dropping downstream swirl tightens
        # no bound: it maximizes possible meridional mass flux before any row work.
        angular = math.cos(math.radians(angle)) if q == 0 else 1.0
        bounds.append((flux * area * open_fraction * angular, q, open_fraction))
    capacity, station, open_fraction = min(bounds)
    return dict(basis="uniform_inlet_duct_sonic_upper_bound", capacity_kg_s=capacity, station=station,
                requested_kg_s=flow.mass_flow, capacity_margin=capacity / flow.mass_flow - 1.0,
                open_fraction=open_fraction, independent_of_iteration=True)


def enforce_inlet_capacity(flow):
    evidence = inlet_capacity(flow)
    if evidence is not None and evidence["capacity_margin"] < -1e-10:
        raise SolverError("requested flow exceeds the independent inlet sonic capacity upper bound",
                          kind="physical_capacity_exceeded", component="inlet_duct", station=evidence["station"], details=evidence)
    return evidence


def solution_limits(solution):
    """Indicators on a converged full-model state; neither is a surge prediction."""
    stall, throat = [], []
    for row in solution.rows:
        d = solution.performance[row.name].diagnostics
        if "equivalent_velocity_ratio" in d:
            margin = np.asarray(d["equivalent_velocity_ratio"]) / np.asarray(d["stall_velocity_ratio"]) - 1.0
            if np.any(margin <= 0.0):
                stall.append(dict(row=row.name, minimum_margin=float(np.min(margin))))
        if "throat_capacity_margin" in d and np.any(d["throat_capacity_margin"] <= 0.0):
            throat.append(dict(row=row.name, minimum_margin=float(np.min(d["throat_capacity_margin"]))))
    return dict(stall_criterion_crossed=stall, throat_capacity_exceeded=throat,
                physical_choke_established=False, surge_prediction=False,
                basis="converged_full_model_correlation_indicators")
