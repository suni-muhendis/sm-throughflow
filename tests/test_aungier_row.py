"""Aungier's blade-row model assembled on the stream surfaces of the throughflow solver."""
import numpy as np
import pytest

from sm_throughflow.correlations import aungier as A
from sm_throughflow.solver import Annulus, ExitGeometry, InletCondition, PerfectGas, QuasiNormals, Throughflow, polytropic_efficiency
from sm_throughflow.solver.aungier_row import AungierCompressorRow, BladeSections, TipClearance, smooth_loss
from sm_throughflow.solver.quasi_normal import solve_quasi_normal

GAS = PerfectGas()
R_HUB, R_TIP = 0.30, 0.50
OMEGA, C_X = 500.0, 150.0


def _stage(rows="RS"):
    """A subsonic free-vortex stage in a cylindrical annulus: rotor on gap 1, stator on gap 3."""
    annulus = Annulus.from_points([(0.0, R_HUB), (0.5, R_HUB)], [(0.0, R_TIP), (0.5, R_TIP)])
    qn = QuasiNormals.on(annulus, [0.0, 0.1, 0.16, 0.22, 0.28, 0.4])
    r = np.linspace(R_HUB, R_TIP, 6)
    k = 0.3 * OMEGA * 0.4 ** 2  # r C_theta behind the rotor
    beta1 = np.degrees(np.arctan2(-OMEGA * r, C_X))
    beta2 = np.degrees(np.arctan2(k / r - OMEGA * r, C_X))
    alpha2 = np.degrees(np.arctan2(k / r, C_X))
    chord, t_c = np.full(6, 0.06), np.full(6, 0.08)
    rotor = AungierCompressorRow(BladeSections(r, beta1 + 2.0, beta2 + 6.0, chord, t_c), 30, OMEGA, GAS, row_number=1, clearance=TipClearance(5e-4, "shroud"))
    stator = AungierCompressorRow(BladeSections(r, alpha2 - 2.0, np.full(6, -6.0), chord, t_c), 40, 0.0, GAS, row_number=2, clearance=TipClearance(5e-4, "hub"))
    blade_rows = []
    if "R" in rows:
        blade_rows.append(rotor.blade_row("R1", 1))
    if "S" in rows:
        blade_rows.append(stator.blade_row("S1", 3))
    flow = Throughflow(annulus, qn, InletCondition(P0=101325.0, T0=288.15, alpha_deg=0.0), mass_flow=85.954, rows=blade_rows, gas=GAS)
    return flow, rotor, stator


@pytest.fixture(scope="module")
def stage():
    flow, rotor, stator = _stage()
    return flow.solve(tol=1e-8, max_iterations=300), rotor, stator


def test_smoothing_keeps_the_wall_sheet_integrals():
    dp = np.array([5.0, 1.0, 3.0, 2.0, 8.0, 4.0, 9.0])
    out = smooth_loss(dp)
    assert out[1:-1] == pytest.approx((dp[:-2] + 2 * dp[1:-1] + dp[2:]) / 4)
    # Trapezoidal integral over the two stream sheets next to each wall, the book's stated property.
    assert out[0] + 2 * out[1] + out[2] == pytest.approx(dp[0] + 2 * dp[1] + dp[2])
    assert out[-1] + 2 * out[-2] + out[-3] == pytest.approx(dp[-1] + 2 * dp[-2] + dp[-3])
    linear = np.linspace(1.0, 2.0, 7)
    assert smooth_loss(linear) == pytest.approx(linear)


def test_stage_converges_and_conserves_mass(stage):
    sol, _, _ = stage
    assert sol.convergence.converged
    assert [s.mass_flow for s in sol.stations] == pytest.approx([85.954] * len(sol.stations), rel=1e-9)
    eta = polytropic_efficiency(GAS, sol.stations[0], sol.stations[-1])
    assert 0.85 < eta < 0.95
    for name in ("R1", "S1"):
        d = sol.performance[name].diagnostics
        assert np.all((d["loss"] > 0.015) & (d["loss"] < 0.06))
        assert np.all((d["deviation"] > 3.0) & (d["deviation"] < 10.0))
    # The clearance loss rises linearly from the far wall toward the gap.
    assert sol.performance["R1"].diagnostics["clearance_loss"][0] == 0.0
    assert sol.performance["S1"].diagnostics["clearance_loss"][-1] == 0.0


def test_stage_is_deterministic(stage):
    sol, _, _ = stage
    again = _stage()[0].solve(tol=1e-8, max_iterations=300)
    for a, b in zip(sol.stations, again.stations):
        assert np.array_equal(a.Wm, b.Wm) and np.array_equal(a.s, b.s)


def test_rotor_assembly_matches_the_correlations_on_a_stream_surface(stage):
    # Mid-span: the stream surface rises across the rotor even in a cylindrical
    # annulus, so the sections are projected onto it (9-1 to 9-6), and the
    # cascade frame flips the rotor's negative angles.
    sol, rotor, _ = stage
    inlet, exit = sol.stations[1], sol.stations[2]
    d = sol.performance["R1"].diagnostics
    j = 5
    r1, r2 = inlet.r[j], exit.r[j]
    cos_phi = np.cos(np.arctan2(r2 - r1, exit.z[j] - inlet.z[j]))
    assert cos_phi < 1.0 - 1e-5
    k1 = -np.degrees(np.arctan(cos_phi * np.tan(np.radians(rotor.sections.at("kappa_in", r1)))))
    k2 = -np.degrees(np.arctan(cos_phi * np.tan(np.radians(rotor.sections.at("kappa_out", r2)))))
    theta, gamma = k1 - k2, 0.5 * (k1 + k2)
    t_c = 0.08 * cos_phi
    sigma = 0.06 / cos_phi / (np.pi * (r1 + r2) / 30)
    beta1 = -np.degrees(np.arctan2(inlet.C_theta[j] - OMEGA * r1, inlet.Wm[j]))
    alpha_star = A.design_angle_of_attack(theta, sigma, t_c)
    i_star = alpha_star + gamma - k1
    assert d["design_incidence"][j] == pytest.approx(i_star, abs=1e-9)
    assert d["incidence"][j] == pytest.approx(beta1 - k1, abs=1e-9)
    delta_star = A.lieblein_design_deviation(k1 + i_star, theta, sigma, t_c)
    assert d["design_deviation"][j] == pytest.approx(delta_star, abs=1e-9)
    delta = A.off_design_deviation(delta_star, A.deviation_slope(k1 + i_star, sigma), beta1 - k1, i_star, exit.Wm[j] / inlet.Wm[j])
    assert d["deviation"][j] == pytest.approx(delta, abs=1e-6)  # converged to the exit flow
    # The exit flow carries the model's angle back in the solver frame.
    assert -np.degrees(exit.beta[j]) == pytest.approx(k2 + d["deviation"][j], abs=1e-6)


def test_a_mirrored_row_has_the_same_loss():
    # A stator drawn for negative swirl is the same cascade: same loss, mirrored exit angle.
    annulus = Annulus.from_points([(0.0, R_HUB), (0.3, R_HUB)], [(0.0, R_TIP), (0.3, R_TIP)])
    qn = QuasiNormals.on(annulus, [0.0, 0.1, 0.2])
    r = np.linspace(R_HUB, R_TIP, 3)
    results = []
    for sign in (1.0, -1.0):
        row = AungierCompressorRow(BladeSections(r, sign * np.full(3, 38.0), sign * np.full(3, -4.0), np.full(3, 0.05), np.full(3, 0.1)), 40, 0.0, GAS)
        flow = Throughflow(annulus, qn, InletCondition(P0=101325.0, T0=288.15, alpha_deg=sign * 40.0), 60.0, rows=[row.blade_row("S", 1)], gas=GAS)
        results.append(flow.solve(tol=1e-9))
    plus, minus = (s.performance["S"] for s in results)
    assert plus.loss == pytest.approx(minus.loss, rel=1e-9)
    assert plus.exit_angle == pytest.approx(-minus.exit_angle, abs=1e-12)


def test_wake_blockage_narrows_the_flow_area():
    # K_W multiplies the mass integral (7-5): half the area, twice the velocity at fixed density.
    y = np.linspace(0.0, 0.2, 11)
    common = dict(t=y / y[-1], r=0.3 + y, eps=np.zeros(11), phi=np.zeros(11), kappa=np.zeros(11), lam=0.0, omega=0.0,
                  I=np.full(11, GAS.enthalpy(288.15)), s=np.zeros(11), swirl=np.zeros(11))
    open_ = solve_quasi_normal(GAS, y, mass_flow=1.0, **common)
    blocked = solve_quasi_normal(GAS, y, mass_flow=1.0, wake=np.full(11, 0.5), **common)
    assert blocked.Wm == pytest.approx(2.0 * open_.Wm, rel=1e-3)
    assert np.sum(blocked.tube_mass_flows) == pytest.approx(1.0, rel=1e-6)


def test_section_range_is_enforced():
    sections = BladeSections([0.3, 0.4], [40.0, 40.0], [10.0, 10.0], [0.05, 0.05], [0.1, 0.1])
    with pytest.raises(ValueError):
        sections.at("chord", [0.29])
    with pytest.raises(ValueError):
        AungierCompressorRow(sections, 30, 0.0, profile="naca65", a_c=0.4)
