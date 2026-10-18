"""Spanwise mixing (Gallimore and Cumpsty, 1986): correlation and the mixing step."""
from types import SimpleNamespace

import numpy as np
import pytest

from sm_throughflow.correlations.spanwise_mixing import mixing_coefficient_ratio
from sm_throughflow.solver import PerfectGas
from sm_throughflow.solver.mixing import mixing_increments

GAS = PerfectGas()


def station(T, vt, vm, r=None):
    r = np.linspace(0.15, 0.25, 11) if r is None else r
    n = r.size
    return SimpleNamespace(r=r, rho=np.full(n, 1.2), Wm=np.broadcast_to(vm, (n,)).astype(float),
                           T=np.broadcast_to(T, (n,)).astype(float), C_theta=np.broadcast_to(vt, (n,)).astype(float))


def flux_integral(st, x):
    """Integral of rho V_m x r dr over the stream-surface cells."""
    r = st.r
    edges = np.concatenate([[r[0]], 0.5 * (r[1:] + r[:-1]), [r[-1]]])
    return float(np.sum(st.rho * st.Wm * x * r * np.diff(edges)))


def test_equation_9_closed_form():
    # (A t/L) [2 omega (t/L) / (3 phi^2)]^(1/3) with A = 0.4
    assert mixing_coefficient_ratio(0.2, 0.03, 0.5) == pytest.approx(0.4 * 0.03 * (2 * 0.2 * 0.03 / 0.75) ** (1 / 3))
    assert mixing_coefficient_ratio(0.0, 0.03, 0.5) == 0.0


def test_uniform_axial_flow_and_solid_body_rotation_do_not_mix():
    r = np.linspace(0.15, 0.25, 11)
    for vt in (0.0, 400.0 * r):  # no strain in solid-body rotation (A1.1)
        dH, ds, drct = mixing_increments(GAS, station(300.0, vt, 150.0, r), np.zeros(11), np.full(11, 0.05), 0.02)
        assert np.allclose(dH, 0.0, atol=1e-9) and np.allclose(ds, 0.0, atol=1e-12) and np.allclose(drct, 0.0, atol=1e-12)


def test_mixing_conserves_energy_and_angular_momentum_and_flattens_profiles():
    r = np.linspace(0.15, 0.25, 11)
    st = station(np.linspace(290.0, 310.0, 11), 30.0 / r, np.linspace(130.0, 170.0, 11), r)
    dH, ds, drct = mixing_increments(GAS, st, np.zeros(11), np.full(11, 0.05), 0.05)
    assert abs(flux_integral(st, dH)) <= 1e-12 * flux_integral(st, np.abs(dH))
    assert abs(flux_integral(st, drct)) <= 1e-12 * flux_integral(st, np.abs(drct))
    assert flux_integral(st, ds) > 0.0  # mixing is irreversible


def test_without_swirl_total_enthalpy_diffuses():
    # With Pr_t = 1 the energy flux is mu dH0/dr when there is no swirl (a swirl adds -mu V_t^2 / r).
    r = np.linspace(0.15, 0.25, 11)
    st = station(np.linspace(290.0, 310.0, 11), 0.0, np.linspace(130.0, 170.0, 11), r)
    dH, _, _ = mixing_increments(GAS, st, np.zeros(11), np.full(11, 0.05), 0.05)
    H = GAS.cp * st.T + 0.5 * st.Wm ** 2
    assert np.ptp(H + dH) < np.ptp(H)
    assert dH[0] > 0.0 > dH[-1]


def test_sub_steps_keep_a_long_gap_stable():
    r = np.linspace(0.15, 0.25, 11)
    st = station(np.where(r < 0.2, 290.0, 310.0), 0.0, 150.0, r)
    dH, _, _ = mixing_increments(GAS, st, np.zeros(11), np.full(11, 2.0), 0.05)
    T_new = st.T + dH / GAS.cp
    assert T_new.min() >= 290.0 - 1e-6 and T_new.max() <= 310.0 + 1e-6
