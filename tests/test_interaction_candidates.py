"""Gas-dynamic and domain checks, not experimental qualification."""
import numpy as np
import pytest

from validation.passage_shock_candidate import Surface, area_ratio, area_mach, references, shock
from validation.compressible_diffusion_candidate import density_correction, override
from sm_throughflow.correlations import aungier as A
from sm_throughflow.correlations.blade_geometry import section, throat_opening_ratio_geometric
from sm_throughflow.solver.aungier_row import AungierCompressorRow


def cascade(camber=10., stagger=56., solidity=1.3):
    p,q,_ = section('dca','circular_arc',camber,.05,edge_radius=.001)
    throat = throat_opening_ratio_geometric('dca','circular_arc',camber,stagger,.05,solidity,edge_radius=.001)
    return Surface(p,stagger,solidity,.05,.001,throat,q)


@pytest.mark.parametrize('mach',[.1,.6,.99,1.,1.01,1.6,3.])
def test_area_relation_satisfies_mass_energy_with_critical_state(mach):
    area=area_ratio(mach)
    temperature=1.2/(1.+.2*mach**2)
    density=temperature**2.5
    speed=mach*np.sqrt(temperature)
    assert area*density*speed == pytest.approx(1.,abs=3e-15)
    assert temperature+.2*speed**2 == pytest.approx(1.2,abs=3e-15)
    assert area_mach(area,supersonic=mach>1.) == pytest.approx(mach,abs=2e-13)


def test_insufficient_area_is_a_domain_failure_not_a_clipped_sonic_state():
    with pytest.raises(ValueError,match='below critical'):
        area_mach(.99)


def test_reference_and_interpolated_shock_pressures_share_one_loss_budget():
    s=cascade()
    refs=references(1.2,s,56.)
    assert refs['U']['exit_pressure']>refs['CN']['exit_pressure']>refs['CO']['exit_pressure']
    beta=s.choke_angle(1.2)-.5
    head=1.-(1.+.2*1.2**2)**-3.5
    for hi,lo in [('U','CN'),('CN','CO')]:
        pressure=.5*(refs[hi]['exit_pressure']+refs[lo]['exit_pressure'])
        answer=shock(1.2,beta,56.,pressure,s)
        assert answer['loss']==pytest.approx(.5*(refs[hi]['loss']+refs[lo]['loss']),abs=2e-14)
        assert answer['total_ratio']==pytest.approx(1.-head*answer['loss'],abs=2e-14)
        assert 0 < answer['total_ratio'] <= 1.
    with pytest.raises(ValueError,match='below the choked oblique'):
        shock(1.2,beta,56.,.5*refs['CO']['exit_pressure'],s)
    with pytest.raises(ValueError,match='subsonic'):
        shock(.99,beta,56.,.7,s)


def test_supported_high_pressure_branch_does_not_require_low_pressure_reference():
    # This geometry has an inadmissible CO exit area, but U/CN remain
    # meaningful. Rejecting a hypothetical CO must not reject a U query.
    s=cascade(30.,35.,1.7)
    u=references(1.2,s,25.,through='U')['U']
    answer=shock(1.2,s.choke_angle(1.2)-.1,25.,u['exit_pressure']+.01,s)
    assert answer['regime']=='choked_U_limit'
    assert set(answer['references'])=={'U'}


def test_inlet_cache_does_not_hold_exit_angle_or_mutable_reference_results():
    s=cascade()
    first=references(1.2,s,56.,through='U')
    changed=references(1.2,s,54.,through='U')
    assert changed['U']['exit_pressure'] != first['U']['exit_pressure']
    assert changed['U']['total_ratio'] == first['U']['total_ratio']
    repeated=references(1.2,s,56.,through='U')
    assert repeated==first
    first['U']['ma']=-1.
    assert references(1.2,s,56.,through='U')['U']['ma']>1.


def test_linearized_compressibility_has_incompressible_and_no_diffusion_limits():
    np.testing.assert_array_equal(density_correction(0.,[.5,1.,1.5]),1.)
    np.testing.assert_array_equal(density_correction([0.,.5,1.5],1.),1.)
    # Euler linearization: dp/rho=-V2*(V2-V1); dp=a1^2*d(rho).
    v1,v2,a1=300.,180.,340.
    expected=1.-v2*(v2-v1)/a1**2
    assert density_correction(v1/a1,v2/v1)==pytest.approx(expected,abs=3e-16)
    with pytest.raises(ValueError,match='nonpositive'):
        density_correction(2.,2.)


def test_research_override_is_restored_after_exception():
    row,ratio=AungierCompressorRow.__call__,A.max_velocity_ratio_annular
    with pytest.raises(RuntimeError):
        with override():
            assert AungierCompressorRow.__call__ is not row
            raise RuntimeError('sentinel')
    assert AungierCompressorRow.__call__ is row
    assert A.max_velocity_ratio_annular is ratio
