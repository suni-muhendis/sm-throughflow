"""Verification of the streamline-curvature solver against exact results.

Steps 1-6 of docs/throughflow_solver.md: flows with closed-form solutions, and
the conservation laws a lossless blade row must obey on every stream surface.
"""
import numpy as np
import pytest

from sm_throughflow.solver import (
    CURVATURE_MODELS,
    Annulus,
    BladeRow,
    InletCondition,
    PerfectGas,
    PrescribedRow,
    QuasiNormals,
    Throughflow,
)

GAS = PerfectGas()
HUB, TIP = 0.25, 0.35
ANNULUS = Annulus.from_points([(0.0, HUB), (0.5, HUB)], [(0.0, TIP), (0.5, TIP)])
INLET = InletCondition(P0=101325.0, T0=288.15, alpha_deg=0.0)


def _duct(n_qn=3):
    return QuasiNormals.on(ANNULUS, np.linspace(0.0, 0.5, n_qn))


def test_uniform_axial_flow_is_exact():
    solution = Throughflow(ANNULUS, _duct(), INLET, mass_flow=20.0).solve()
    assert solution.convergence.converged
    for station in solution.stations:
        area = np.pi * (TIP**2 - HUB**2)
        assert station.Wm == pytest.approx(np.full(11, 20.0 / (station.rho[0] * area)), rel=1e-12)
        assert np.ptp(station.s) == pytest.approx(0.0, abs=1e-12)
        assert station.mass_flow == pytest.approx(20.0, rel=1e-12)


def test_free_vortex_keeps_the_meridional_velocity_uniform():
    # r C_theta constant with uniform H and s: Wm dWm/dr = 0 (Dixon and Hall, eq. 6.6b).
    inlet = InletCondition(P0=101325.0, T0=288.15, r_c_theta=20.0)
    solution = Throughflow(ANNULUS, _duct(), inlet, mass_flow=20.0).solve()
    for station in solution.stations:
        assert station.Wm == pytest.approx(np.full(11, station.Wm[0]), rel=1e-12)
        assert station.r * station.C_theta == pytest.approx(np.full(11, 20.0), rel=1e-12)


def _forced_vortex_error(surfaces):
    # C_theta = K r with uniform H and s: Wm dWm/dr = -2 K^2 r, so
    # Wm^2 = Wm_hub^2 - 2 K^2 (r^2 - r_hub^2).
    K = 200.0
    span = np.linspace(0.0, 1.0, 401)
    radius = HUB + span * (TIP - HUB)
    inlet = InletCondition(P0=101325.0, T0=288.15, r_c_theta=K * radius**2)
    solution = Throughflow(ANNULUS, _duct(), inlet, mass_flow=20.0, stream_surfaces=surfaces).solve()
    station = solution.stations[0]
    exact = np.sqrt(station.Wm[0] ** 2 - 2.0 * K**2 * (station.r**2 - HUB**2))
    return float(np.max(np.abs(station.Wm - exact) / exact))


def test_forced_vortex_matches_the_closed_form_and_converges_at_second_order():
    errors = [_forced_vortex_error(n) for n in (11, 21, 41)]
    assert errors[0] < 2e-4
    assert errors[0] / errors[1] > 3.5
    assert errors[1] / errors[2] > 3.5


def _stage(curvature="full", stator_loss=0.0, basis="inlet"):
    """A free-vortex rotor (equal work at every radius) and an axial-exit stator."""
    omega, K, wm = 1000.0, 15.0, 152.0
    radius = HUB + np.linspace(0.0, 1.0, 11) * (TIP - HUB)
    beta_rotor = np.degrees(np.arctan((K / radius - omega * radius) / wm))
    rows = [
        BladeRow("rotor", 1, omega, PrescribedRow(beta_rotor)),
        BladeRow("stator", 3, 0.0, PrescribedRow(0.0, loss=stator_loss, basis=basis)),
    ]
    quasi_normals = QuasiNormals.on(ANNULUS, [0.0, 0.10, 0.15, 0.20, 0.25, 0.35])
    problem = Throughflow(ANNULUS, quasi_normals, INLET, mass_flow=33.0, rows=rows, curvature=curvature)
    return problem, problem.solve(), beta_rotor


@pytest.mark.parametrize("curvature", CURVATURE_MODELS)
def test_a_lossless_stage_conserves_energy_and_entropy_on_every_stream_surface(curvature):
    _, solution, _ = _stage(curvature)
    assert solution.convergence.converged
    duct_in, rotor_exit, duct_mid, stator_exit, duct_out = solution.stations[0], *solution.stations[2:6]
    rotor_in, stator_in = solution.stations[1], solution.stations[3]
    # Rotor: rothalpy conserved, so H2 - H1 = omega (r2 C_theta2 - r1 C_theta1) (Euler), s unchanged.
    euler = (rotor_exit.H - rotor_in.H) - 1000.0 * (rotor_exit.r * rotor_exit.C_theta - rotor_in.r * rotor_in.C_theta)
    assert np.max(np.abs(euler)) < 1e-8
    assert rotor_exit.s == pytest.approx(rotor_in.s, abs=1e-10)
    # Stator and ducts: H and s unchanged on every stream surface.
    for upstream, downstream in ((rotor_exit, stator_in), (stator_in, stator_exit), (stator_exit, duct_out), (duct_in, rotor_in)):
        assert downstream.H == pytest.approx(upstream.H, rel=1e-14)
        assert downstream.s == pytest.approx(upstream.s, abs=1e-10)
    # So the mass-averaged total temperature does not change across the stator.
    assert stator_exit.mass_average(stator_exit.T0) == pytest.approx(stator_in.mass_average(stator_in.T0), abs=1e-6)


def test_every_stream_tube_carries_its_share_of_the_mass_flow():
    _, solution, _ = _stage()
    for station in solution.stations:
        assert station.tube_mass_flows / 33.0 == pytest.approx(np.full(10, 0.1), abs=1e-8)
        assert station.mass_flow == pytest.approx(33.0, rel=1e-12)


def test_blade_rows_release_the_flow_at_the_prescribed_angles():
    _, solution, beta_rotor = _stage()
    rotor_exit, stator_exit = solution.stations[2], solution.stations[4]
    expected = np.radians(np.interp(rotor_exit.t, np.linspace(0.0, 1.0, 11), beta_rotor))
    assert rotor_exit.beta == pytest.approx(expected, abs=1e-12)
    assert stator_exit.alpha == pytest.approx(np.zeros(11), abs=1e-12)


def test_an_inlet_based_loss_lowers_total_pressure_by_its_definition():
    _, solution, _ = _stage(stator_loss=0.04)
    stator_in, stator_exit = solution.stations[3], solution.stations[4]
    assert stator_exit.P0 == pytest.approx(stator_in.P0 - 0.04 * (stator_in.P0 - stator_in.P), rel=1e-12)
    assert np.all(stator_exit.s > stator_in.s)
    assert stator_exit.H == pytest.approx(stator_in.H, rel=1e-14)


def test_an_exit_based_loss_lowers_total_pressure_by_its_definition():
    _, solution, _ = _stage(stator_loss=0.04, basis="exit")
    stator_in, stator_exit = solution.stations[3], solution.stations[4]
    loss = (stator_in.P0 - stator_exit.P0) / (stator_exit.P0 - stator_exit.P)
    assert loss == pytest.approx(np.full(11, 0.04), rel=1e-9)
