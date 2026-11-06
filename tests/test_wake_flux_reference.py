"""Manufactured planar traverses for the research reduction."""
import numpy as np
import pytest

from validation.wake_flux_reference import reduce_wake

R = 287.05
GAMMA = 1.4
CP = GAMMA * R / (GAMMA - 1)


def test_uniform_oblique_traverse_keeps_its_state():
    result = reduce_wake([1, 2], [90000, 90000], [270, 270], [210, 210], [140, 140],
                         edge_mass_flux=90000 * 210 / (R * 270))
    assert result.pressure == pytest.approx(90000, rel=1e-13)
    assert result.temperature == pytest.approx(270, rel=1e-13)
    assert result.normal_velocity == pytest.approx(210, rel=1e-13)
    assert result.tangential_velocity == pytest.approx(140, rel=1e-13)
    assert result.total_pressure == pytest.approx(result.mass_average_total_pressure, rel=1e-13)
    assert result.blockage == pytest.approx(0, abs=1e-14)
    assert result.mixing_entropy_over_R == pytest.approx(0, abs=1e-14)


def test_nonuniform_traverse_conserves_all_fluxes_and_produces_entropy():
    width = np.array([.1, .3, .6])
    pressure = np.full(3, 94000.)
    normal = np.array([75., 190., 270.])
    tangent = np.array([20., 70., 100.])
    temperature = 320. - (normal**2 + tangent**2) / (2 * CP)
    rho = pressure / (R * temperature)
    result = reduce_wake(width, pressure, temperature, normal, tangent,
                         edge_mass_flux=rho[-1] * normal[-1])
    momentum = result.pressure / (R * result.temperature) * result.normal_velocity
    assert momentum == pytest.approx(np.sum(width * rho * normal), rel=1e-13)
    assert result.pressure + momentum * result.normal_velocity == pytest.approx(
        np.sum(width * (pressure + rho * normal**2)), rel=1e-13)
    assert momentum * result.tangential_velocity == pytest.approx(
        np.sum(width * rho * normal * tangent), rel=1e-13)
    assert CP * result.temperature + .5 * (
        result.normal_velocity**2 + result.tangential_velocity**2
    ) == pytest.approx(CP * 320., rel=1e-13)
    assert result.blockage > 0
    assert result.mixing_entropy_over_R > 0
    assert result.total_pressure < result.mass_average_total_pressure


def test_equal_blockage_does_not_determine_mixed_out_loss():
    # Uniform density and pressure at the traverse yield equal mass flux
    # for both profiles. Their momentum and energy fluxes differ.
    ref_flux = 94000 * 280 / (R * 290)
    uniform = reduce_wake([1, 1], [94000, 94000], [290, 290], [180, 180], [0, 0],
                          edge_mass_flux=ref_flux)
    wake = reduce_wake([1, 1], [94000, 94000], [290, 290], [80, 280], [0, 0],
                       edge_mass_flux=ref_flux)
    assert wake.blockage == pytest.approx(uniform.blockage, abs=1e-14)
    assert wake.mixing_entropy_over_R > uniform.mixing_entropy_over_R
    assert wake.total_pressure != pytest.approx(uniform.total_pressure)


@pytest.mark.parametrize("speed", [-10, 0, 360])
def test_reverse_and_supersonic_normal_flow_are_outside_scope(speed):
    with pytest.raises(ValueError):
        reduce_wake([1, 1], [94000, 94000], [290, 290], [80, speed], [0, 0],
                    edge_mass_flux=200)
