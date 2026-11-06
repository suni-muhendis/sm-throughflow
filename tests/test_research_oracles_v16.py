"""Independent limits for research oracles; passing does not qualify physics."""
import numpy as np
import pytest
from validation.conical_reference_v16 import Cone
from validation.shock_reference_v16 import circular_arc,shock,inverse_pm
from sm_throughflow.correlations import aungier as A


@pytest.mark.parametrize('angle',[-35.,0.,45.])
def test_constant_angle_cone_path_matches_closed_form(angle):
    cone=Cone(3.,np.radians(angle));kappa=.7;length=.9
    m=length*np.cos(kappa);sine=np.sin(cone.angle)
    theta=(np.tan(kappa)/sine*np.log1p(sine*m/cone.radius)
           if sine else length*np.sin(kappa)/cone.radius)
    np.testing.assert_allclose(cone.path([0.,0.],kappa,0.,length),[m,theta],atol=5e-16)


def test_cylinder_turning_path_matches_circle():
    cone=Cone(2.,0.);kappa=.8;rate=-.6;length=.7
    expected=[(np.sin(kappa+rate*length)-np.sin(kappa))/rate,
              (np.cos(kappa)-np.cos(kappa+rate*length))/(rate*cone.radius)]
    np.testing.assert_allclose(cone.path([0.,0.],kappa,rate,length),expected,atol=3e-16)


def test_nasa_tnd5437_cone_example_turn_and_radius():
    # TN D-5437 printed p. 3 / figure 3: 45deg cone, 45->0deg local
    # turning, r_exit/r_inlet=1.4. Constant turn gives C=-1.25/r_inlet.
    cone=Cone(1.,np.pi/4);rate=-1.25;length=np.pi/5
    end=cone.path([0.,0.],np.pi/4,rate,length)
    assert 1.+np.sin(cone.angle)*end[0]==pytest.approx(1.4,abs=3e-16)
    assert np.pi/4+rate*length==0.


@pytest.mark.parametrize('angle',[-35.,0.,45.])
def test_cone_unwrapping_preserves_local_length_and_tangent(angle):
    cone=Cone(3.,np.radians(angle));s=.65;eps=1e-5;k=.8;c=-.4
    points=cone.path([0.,0.],k,c,np.array([s-eps,s,s+eps]))
    xy=cone.xy(points);derivative=(xy[2]-xy[0])/(2*eps)
    np.testing.assert_allclose(derivative,cone.tangent(points[1],k+c*s),atol=2e-11)
    assert np.linalg.norm(derivative)==pytest.approx(1.,abs=2e-11)


def test_fast_pm_inverse_matches_bisection_over_probe_domain():
    mach=np.r_[np.linspace(1.,1.1,50),np.linspace(1.1,6.,250)]
    nu=A.prandtl_meyer_angle(mach)
    np.testing.assert_allclose(inverse_pm(nu,1.4),A.mach_from_prandtl_meyer_angle(nu),atol=8e-14,rtol=0.)


def test_schobeiri_published_circular_reference_and_balance():
    # Part I p. 173 reports approximately 9.5deg for M=1.2, S/R=.5,
    # beta_t=30deg from circumferential. Do not fit to this rounded value.
    result=shock(1.2,60.,circular_arc(60.,2.,45.))
    assert result['status']=='unique'
    r=result['roots'][0]
    assert r['expansion_deg']==pytest.approx(9.5,abs=.3)
    assert r['mach']==pytest.approx(1.55,abs=.03)
    assert r['normal_mach']>1.
    beta=np.pi/3;theta=np.radians(r['expansion_deg']);ms=r['mach'];ks=np.radians(r['flow_angle_deg'])
    x=2.*(np.sin(beta)-np.sin(beta-theta));y=2.*(np.cos(beta-theta)-np.cos(beta))
    temp=(1.+.2*1.2**2)/(1.+.2*ms**2)
    flux=ms/1.2*temp**3*((1.-2*y)*np.cos(ks)+2*x*np.sin(ks))
    assert flux==pytest.approx(np.cos(beta),abs=4e-10)
    assert ms*np.sqrt(temp)*np.sin(ks)==pytest.approx(1.2*np.sin(beta),abs=1e-14)
    assert A.prandtl_meyer_angle(ms)-A.prandtl_meyer_angle(1.2)==pytest.approx(np.degrees(theta),abs=1e-12)
    assert 0.<result['loss']<1.


def test_shock_oracle_does_not_invent_subsonic_shock_or_missing_root():
    curve=circular_arc(60.,2.,2.)
    assert shock(.9,60.,curve)==dict(status='subsonic',loss=0.,roots=[])
    result=shock(1.2,60.,curve)
    assert result['status']=='no_root' and result['loss'] is None


def test_research_reference_is_mesh_converged_and_repeatable():
    a=shock(1.2,60.,circular_arc(60.,2.,45.,201))
    b=shock(1.2,60.,circular_arc(60.,2.,45.,801))
    assert a['loss']==pytest.approx(b['loss'],abs=2e-9)
    assert b==shock(1.2,60.,circular_arc(60.,2.,45.,801))
