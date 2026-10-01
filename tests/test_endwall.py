"""Aungier's end-wall boundary-layer analysis (chapter 8)."""
import numpy as np
import pytest
from scipy.integrate import quad

from sm_throughflow.solver import Annulus, InletCondition, PerfectGas, QuasiNormals, Throughflow
from sm_throughflow.solver import endwall as EW
from sm_throughflow.solver.endwall import EndwallBoundaryLayers

GAS = PerfectGas()


def test_power_law_profile_relations_follow_from_the_profiles():
    # V_m/V_me = eta^n, V_theta/V_theta,e = eta^m, constant density (8-18 to 8-26).
    n, m, delta = 0.3, 0.2, 0.02
    delta1 = delta * quad(lambda e: 1 - e ** n, 0, 1)[0]
    theta11 = delta * quad(lambda e: e ** n * (1 - e ** n), 0, 1)[0]
    theta12 = delta * quad(lambda e: e ** n * (1 - e ** m), 0, 1)[0]
    delta2 = delta * quad(lambda e: 1 - e ** m, 0, 1)[0]
    theta22 = delta * quad(lambda e: e ** m * (1 - e ** m), 0, 1)[0]
    n_, H1, d1, d = EW.meridional_profile(delta - delta1, theta11)
    assert (n_, H1, d1, d) == pytest.approx((n, 2 * n + 1, delta1, delta))
    m_, d2, t22, H2 = EW.tangential_profile(theta12, n, delta)
    assert (m_, d2, t22, H2) == pytest.approx((m, delta2, theta22, 2 * m + 1))
    assert EW.theta12_from_exponent(m, n, delta) == pytest.approx(theta12)


@pytest.mark.parametrize("m", [0.04, 0.0, -0.3, -0.8])
def test_extended_profile_relations_follow_from_8_28(m):
    n, delta = 0.25, 0.02
    a = 0.1705 * (1 - 20 * m)

    def f(e):
        return e ** 0.05 + a * (1 - e) ** 2 * e ** 0.1  # (8-28)

    delta2 = delta * quad(lambda e: 1 - f(e), 0, 1)[0]
    theta22 = delta * quad(lambda e: f(e) * (1 - f(e)), 0, 1)[0]
    theta12 = delta * quad(lambda e: e ** n * (1 - f(e)), 0, 1)[0]
    m_, d2, t22, H2 = EW.tangential_profile(theta12, n, delta)
    assert m_ == pytest.approx(m, abs=1e-6)  # (8-31) is exact
    assert d2 == pytest.approx(delta2, rel=1e-6)  # (8-29) is exact
    # (8-30) is a two-term fit, exact slope 0.95 and continuity with the power law at
    # m = 0.05; the exact integral is -0.00044 + 0.9502 m - 1.5126 m^2. The book's form
    # is kept (Aungier calibrated with it); it is within 6% of the integral down to m = -0.8.
    assert t22 == pytest.approx(delta * (0.95 * m - 1.684 * m * m))
    assert theta22 / delta == pytest.approx(-0.000438 + 0.950205 * m - 1.51256 * m * m, abs=2e-6)
    assert abs(t22 - theta22) <= 0.065 * abs(theta22) + 5e-4 * delta  # the dropped intercept
    assert H2 == pytest.approx(d2 / t22, rel=1e-9)  # (8-32)


def test_the_two_profiles_meet_at_m_005():
    n, delta = 0.2, 0.02
    theta12 = EW.theta12_from_exponent(0.05, n, delta)
    below = EW.tangential_profile(theta12 * (1 - 1e-9), n, delta)
    above = EW.tangential_profile(theta12 * (1 + 1e-9), n, delta)
    assert below == pytest.approx(above, rel=1e-5)  # (8-30) rounds 0.05/(1.05 x 1.1) to 0.04329


def test_streamwise_thicknesses_project_the_two_profiles():
    n, m, delta, beta = 0.3, 0.15, 0.02, np.radians(35.0)
    c, s = np.cos(beta), np.sin(beta)

    def vs(e):  # V_s / V_e (8-37) with V_me = V_e cos(beta), V_theta,e = V_e sin(beta)
        return e ** n * c * c + e ** m * s * s

    d_star = delta * quad(lambda e: 1 - vs(e), 0, 1)[0]
    theta = delta * quad(lambda e: vs(e) * (1 - vs(e)), 0, 1)[0]
    d1 = delta * n / (n + 1)
    t11 = delta * n / ((n + 1) * (2 * n + 1))
    d2 = delta * m / (m + 1)
    t22 = d2 / (2 * m + 1)
    t12 = EW.theta12_from_exponent(m, n, delta)
    assert EW.streamwise_thicknesses(d1, t11, d2, t22, t12, beta) == pytest.approx((d_star, theta))


def test_ludwieg_tillmann_in_its_usual_form():
    # c_f = 0.246 x 10^(-0.678 H) Re_theta^-0.268.
    for H, re in ((1.3, 2000.0), (1.8, 8000.0)):
        # 1.561 is 0.678 ln 10 = 1.56115 rounded.
        assert EW.ludwieg_tillmann(H, re) == pytest.approx(0.246 * 10 ** (-0.678 * H) * re ** -0.268, rel=5e-4)
    assert EW.ludwieg_tillmann(3.0, 100.0) == EW.ludwieg_tillmann(2.4, 250.0)  # the limits of section 8.4


def test_blade_force_defect_reproduces_figure_8_6():
    g = 0.04
    for d_over_g in (0.05, 0.15, 0.3):
        nu = EW.blade_force_defect(d_over_g * g, g, 0.0)
        x3 = (8 * d_over_g) ** 3
        assert nu / (0.12 * g) == pytest.approx(x3 / (1 + x3))
    assert EW.defect_correction_factor(10.0, g) == pytest.approx(0.5, abs=1e-6)  # F -> 1/2 (8-55)


def test_annular_duct_boundary_layer_grows_like_a_turbulent_flat_plate():
    # A long, wide annulus with uniform axial flow: each wall is close to a flat
    # plate, and theta should grow like the 1/7-power law theta = 0.036 x Re_x^-0.2
    # counted from a virtual origin that matches the inlet theta.
    annulus = Annulus.from_points([(0.0, 1.0), (2.0, 1.0)], [(0.0, 1.2), (2.0, 1.2)])
    qn = QuasiNormals.on(annulus, np.linspace(0.0, 2.0, 21))
    walls = EndwallBoundaryLayers(inlet_blockage=0.004)
    flow = Throughflow(annulus, qn, InletCondition(P0=101325.0, T0=288.15), mass_flow=60.0, gas=GAS, endwall=walls, curvature="none")
    sol = flow.solve(tol=1e-9)
    st = sol.stations[0]
    nu_k = EW.sutherland_air(st.T[0]) / st.rho[0]
    u = st.Wm[0]

    def law_theta(x):
        return 0.036 * x * (u * x / nu_k) ** -0.2

    hub = sol.endwall.hub
    x0 = [x for x in np.geomspace(1e-3, 10.0, 4000) if law_theta(x) >= hub[0].theta11][0]
    expected = law_theta(x0 + 2.0)
    assert hub[-1].theta11 == pytest.approx(expected, rel=0.15)
    assert 1.25 < hub[-1].H1 < 1.45  # a turbulent flat-plate shape factor


def test_tangential_momentum_survives_a_change_of_wall_frame():
    walls = EndwallBoundaryLayers()
    edge = EW._Edge(r=0.3, rho=1.2, vm=150.0, c_theta=80.0, P=1e5, T=288.0, phi=0.0, m=0.0)
    n, delta = 0.25, 0.02
    theta11 = delta * n / ((n + 1) * (2 * n + 1))
    theta12 = EW.theta12_from_exponent(0.2, n, delta)
    X = edge.r * edge.rho * edge.vm * (delta - delta * n / (n + 1))
    M = edge.r * edge.rho * edge.vm ** 2 * theta11
    T = edge.r ** 2 * edge.rho * edge.vm * edge.c_theta * theta12
    stationary = walls._state(edge, X, M, T, 0.0, 0.2)
    rotating = walls._state(edge, *walls._conserved(edge, stationary), 500.0, stationary.m)
    # (8-68): C_theta,e theta12 = W_theta,e theta12'.
    assert rotating.c_theta12 == pytest.approx(stationary.c_theta12)
    assert (edge.c_theta - 500.0 * edge.r) * rotating.theta12 == pytest.approx(edge.c_theta * stationary.theta12)
    # A frame without tangential edge velocity keeps the product for the next one.
    still = walls._state(edge, *walls._conserved(edge, stationary), edge.c_theta / edge.r, stationary.m)
    assert still.c_theta12 == pytest.approx(stationary.c_theta12)


def test_stage_blockage_grows_and_converges():
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))
    from test_aungier_row import _stage

    flow = _stage()[0]
    flow.endwall = EndwallBoundaryLayers(inlet_blockage=0.02)
    sol = flow.solve(tol=1e-8, max_iterations=400)
    assert sol.convergence.converged
    blockage = 1.0 - sol.blockage
    assert blockage[0] == pytest.approx(0.02, rel=1e-6)
    assert 0.025 < blockage[-1] < 0.06
    assert np.all(np.diff(blockage) > -0.002)  # the blockage builds through the stage
    assert sol.endwall.blockage == pytest.approx(blockage, abs=1e-6)
    assert [s.mass_flow for s in sol.stations] == pytest.approx([85.954] * len(sol.stations), rel=1e-9)
    again = _stage()[0]
    again.endwall = EndwallBoundaryLayers(inlet_blockage=0.02)
    assert np.array_equal(again.solve(tol=1e-8, max_iterations=400).blockage, sol.blockage)
