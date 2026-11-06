"""Checks on a completed solution, independent of the nonlinear stopping test."""
import numpy as np

from .errors import PhysicalStateError


def verify_solution(flow, solution, tolerance):
    """Return balance residuals or reject an inadmissible converged solution.

    Entropy is monotone along a stream surface only without radial mixing.
    With mixing, test the integrated balance instead. Energy tolerances include
    the outer stream-tube placement error for integrated quantities.
    """
    stations = solution.stations
    mass_error = share_error = energy_error = power_error = 0.0
    duct_momentum_error = duct_momentum_flux_error = 0.0
    entropy_min = np.inf
    mean_entropy_min = np.inf
    energy_scale = max(float(np.max(np.abs(stations[0].H))), 1.0)
    for q, st in enumerate(stations):
        for key in ("Wm", "T", "T0", "P", "P0", "rho", "a"):
            value = np.asarray(getattr(st, key))
            if not np.all(np.isfinite(value)) or np.any(value <= 0.0):
                raise PhysicalStateError("{} must be finite and positive".format(key), component="verification", station=q)
        for key in ("H", "s", "C_theta", "r", "y"):
            if not np.all(np.isfinite(getattr(st, key))):
                raise PhysicalStateError("non-finite {}".format(key), component="verification", station=q)
        if np.any(np.diff(st.y) <= 0.0):
            raise PhysicalStateError("stream surfaces are not ordered", component="verification", station=q)
        masses = st.tube_mass_flows
        mass_error = max(mass_error, abs(float(np.sum(masses)) / flow.mass_flow - 1.0))
        share_error = max(share_error, float(np.max(np.abs(masses / flow.mass_flow - 1.0 / (flow.n - 1)))))
    for q, (a, b) in enumerate(zip(stations, stations[1:])):
        row = flow.row_at.get(q)
        omega = 0.0 if row is None else row.omega
        if row is None:
            rct_a, rct_b = a.r * a.C_theta, b.r * b.C_theta
            angular_scale = max(float(np.max(np.abs(rct_a))), 1.0)
            if flow.mixing is None:
                duct_momentum_error = max(duct_momentum_error, float(np.max(np.abs(rct_b - rct_a))) / angular_scale)
            duct_momentum_flux_error = max(duct_momentum_flux_error,
                abs(b.mass_average(rct_b) - a.mass_average(rct_a)) / angular_scale)
        work = omega * (b.r * b.C_theta - a.r * a.C_theta)
        if flow.mixing is None:
            energy_error = max(energy_error, float(np.max(np.abs(b.H - a.H - work))) / energy_scale)
        # Includes mixing: radial energy/torque redistribution has zero net flux.
        expected = omega * (b.mass_average(b.r * b.C_theta) - a.mass_average(a.r * a.C_theta))
        actual = b.mass_average(b.H) - a.mass_average(a.H)
        power_error = max(power_error, abs(actual - expected) / energy_scale)
        entropy_min = min(entropy_min, float(np.min(b.s - a.s)))
        mean_entropy_min = min(mean_entropy_min, b.mass_average(b.s) - a.mass_average(a.s))
    checks = dict(mass_relative_error=mass_error, tube_share_error=share_error,
                  energy_relative_error=energy_error if flow.mixing is None else None,
                  integrated_energy_relative_error=power_error,
                  duct_angular_momentum_relative_error=duct_momentum_error if flow.mixing is None else None,
                  duct_angular_momentum_flux_relative_error=duct_momentum_flux_error,
                  min_stream_entropy_change_j_kg_k=entropy_min,
                  min_mean_entropy_change_j_kg_k=mean_entropy_min)
    limits = dict(mass_relative_error=1e-9, tube_share_error=max(10.0 * tolerance, 1e-8),
                  energy_relative_error=1e-10, integrated_energy_relative_error=max(20.0 * tolerance, 1e-8),
                  duct_angular_momentum_relative_error=1e-10,
                  duct_angular_momentum_flux_relative_error=max(20.0 * tolerance, 1e-8))
    for key, limit in limits.items():
        if checks[key] is not None and checks[key] > limit:
            raise PhysicalStateError("{} exceeds the conservation tolerance".format(key), component="verification",
                                     residual=checks[key], details={"limit": limit})
    if flow.mixing is None and entropy_min < -1e-8:
        raise PhysicalStateError("entropy decreases along an unmixed stream surface", component="verification", residual=entropy_min)
    if mean_entropy_min < -max(20.0 * tolerance * flow.gas.cp, 1e-8):
        raise PhysicalStateError("negative integrated entropy production", component="verification", residual=mean_entropy_min)
    return dict(checks, limits=limits)
