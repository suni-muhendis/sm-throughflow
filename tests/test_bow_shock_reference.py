"""Independent gas-dynamic limits; these do not qualify the research closure."""
import numpy as np
import pytest

from validation.bow_shock_reference import bow, oblique, _unique_root


@pytest.mark.parametrize('mach,theta', [(1.2, 90.), (1.6, 70.), (2.3, 45.)])
def test_oblique_shock_conserves_mass_momentum_energy(mach, theta):
    gamma = 1.4
    answer = oblique(mach, theta, gamma)
    mn = mach*np.sin(np.radians(theta))
    density = (gamma+1)*mn**2/(2+(gamma-1)*mn**2)
    pressure = 1+2*gamma/(gamma+1)*(mn**2-1)
    temperature = pressure/density
    # Tangential velocity unchanged; normal mass flux conserved.
    v1n, v1t = mach*np.sin(np.radians(theta)), mach*np.cos(np.radians(theta))
    angle2 = np.radians(theta-answer['deflection'])
    v2n = answer['mach']*np.sqrt(temperature)*np.sin(angle2)
    v2t = answer['mach']*np.sqrt(temperature)*np.cos(angle2)
    assert density*v2n == pytest.approx(v1n, abs=2e-15)
    assert v2t == pytest.approx(v1t, abs=2e-15)
    assert 1/gamma+v1n*v1n == pytest.approx(pressure/gamma+density*v2n*v2n, abs=3e-15)
    assert 1+.2*mach**2 == pytest.approx(temperature*(1+.2*answer['mach']**2), abs=2e-15)
    entropy = np.log(pressure)-gamma*np.log(density)
    assert answer['total_ratio'] == pytest.approx(np.exp(-entropy/(gamma-1)), abs=3e-15)


def test_detachment_scales_with_radius_and_has_correct_asymptote():
    b = bow(1.6, .002)
    large = bow(1.6, .02)
    assert b.angle(0.) == 90.
    assert b.angle(1e8) == pytest.approx(np.degrees(np.arcsin(1/1.6)), abs=1e-12)
    assert large.detachment == pytest.approx(10*b.detachment, abs=1e-16)
    assert large.focus == pytest.approx(10*b.focus, abs=1e-16)
    assert large.sonic_height == pytest.approx(10*b.sonic_height, abs=1e-16)
    assert b.detachment > 0 and b.focus > 0 and b.sonic_height > 0


def test_root_selection_does_not_accept_a_tangent_pole():
    def function(x):
        return (x-.2)/(x-.503)
    assert _unique_root(function, 0., 1.) == pytest.approx(.2, abs=1e-13)
    with pytest.raises(ValueError, match='0 admissible'):
        _unique_root(lambda x: 1/(x-.503), 0., 1.)
