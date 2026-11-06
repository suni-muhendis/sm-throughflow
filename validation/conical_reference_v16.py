"""Research oracle: source-native NASA conical MCA geometry, not production.

TN D-7345 eqs. 1-4, 9 and printed p. 10: constant local d(kappa)/ds,
constant-angle thickness paths, surface tangency to edge circles. Printed
KIC/KTC/KOC and axial positions specify the meanline directly. No PHISS,
measured loss, efficiency or fitted family coefficient enters construction.
"""
from dataclasses import dataclass
import numpy as np
from scipy.optimize import root, minimize_scalar

NODES, WEIGHTS = np.polynomial.legendre.leggauss(32)
NODES, WEIGHTS = (NODES+1.)*.5, WEIGHTS*.5


@dataclass
class Cone:
    radius: float
    angle: float

    def path(self, start, kappa, rate, length):
        """(meridional position, cylindrical theta) along a constant-local-turn path."""
        t = np.asarray(length, dtype=float)
        ds = t[...,None]*NODES
        dk = rate*ds
        m = ds*np.cos(kappa+dk*.5)*np.sinc(dk/(2*np.pi))
        radial = self.radius+np.sin(self.angle)*(start[0]+m)
        if np.any(radial<=0): raise ValueError('path crosses cone apex')
        theta = t*np.sum(WEIGHTS*np.sin(kappa+dk)/radial,axis=-1)
        endm = t*np.cos(kappa+rate*t*.5)*np.sinc(rate*t/(2*np.pi))
        return np.stack([start[0]+endm,start[1]+theta],axis=-1)

    def xy(self, point):
        """Isometric developed coordinates, with a stable cylindrical limit."""
        m,theta=np.asarray(point).T
        sa=np.sin(self.angle);eps=sa*theta
        # R0(cos(eps)-1), R0 sin(eps) evaluated without division by sin(alpha).
        x=m*np.cos(eps)-.5*self.radius*sa*theta**2*np.sinc(eps/(2*np.pi))**2
        y=m*np.sin(eps)+self.radius*theta*np.sinc(eps/np.pi)
        return np.array([x,y]).T

    def tangent(self, point, kappa):
        angle=kappa+np.sin(self.angle)*np.asarray(point)[...,1]
        return np.stack([np.cos(angle),np.sin(angle)],axis=-1)


def check_root(fun, guess):
    result=root(fun,guess,tol=1e-10)
    residual=np.max(abs(fun(result.x)))
    if not np.isfinite(residual) or residual>1e-9:
        raise ValueError(f'conical geometry residual {residual}: {result.message}')
    return result.x


def segment(cone, start, kappa, end_m, end_angle):
    dm=end_m-start[0];dk=end_angle-kappa
    length=dm/(np.cos(.5*(kappa+end_angle))*np.sinc(dk/(2*np.pi)))
    rate=dk/length
    return rate,length,cone.path(start,kappa,rate,length)


def meanline(raw):
    f=lambda key:float(raw[key])
    chord=f('AERO CHORD')
    cone=Cone(f('RI')/chord,np.radians(f('CONE ANGLE')))
    k1,kt,k2=np.radians([f(k) for k in ('KIC','KTC','KOC')])
    mt,mm,me=[(f(z)-f('ZI'))/(chord*np.cos(cone.angle)) for z in ('ZTC','ZMC','ZO')]
    first=np.zeros(2)
    c1,s1,transition=segment(cone,first,k1,mt,kt)
    c2,s2,last=segment(cone,transition,kt,me,k2)
    if mm<=mt:
        km=np.arcsin(np.sin(k1)+c1*mm)
        cm,sm,maximum=segment(cone,first,k1,mm,km)
    else:
        km=np.arcsin(np.sin(kt)+c2*(mm-mt))
        cm,sm,maximum=segment(cone,transition,kt,mm,km)
    return dict(cone=cone,first=first,last=last,transition=transition,maximum=maximum,
                k1=k1,kt=kt,k2=k2,km=km,front_first=mm<=mt,
                half_thickness=.5*f('TM')/chord,
                radius_in=.5*f('TI')/chord,radius_out=.5*f('TO')/chord,
                front_rate=c1,rear_rate=c2,front_length=s1,rear_length=s2)


def arc_to_circle(cone,start,kappa,centre,radius,side,direction):
    """Constant-local-turn segment ending tangent to an intrinsic edge circle."""
    origin=cone.xy(start);target=cone.xy(centre)
    tangent=cone.tangent(start,kappa);normal=np.array([-tangent[1],tangent[0]])
    d=origin-target
    rho=(radius**2-d@d)/(2*(normal@d-side*radius))
    global_rate=1/rho
    rate0=global_rate-np.sin(cone.angle)*np.sin(kappa)/(cone.radius+np.sin(cone.angle)*start[0])
    length0=direction*np.linalg.norm(d)
    def residual(v):
        rate,length=v
        end=cone.path(start,kappa,rate,length)
        d=cone.tangent(end,kappa+rate*length)
        normal=np.array([-d[1],d[0]])
        return cone.xy(end)-side*radius*normal-target
    rate,length=check_root(residual,[rate0,length0])
    if direction*length<=0 or abs(rate*length)>np.pi:
        raise ValueError('wrong conical surface branch')
    return rate,length


def surfaces(raw,points=401):
    d=meanline(raw);cone=d['cone'];out=[]
    for side in (1.,-1.):
        maximum=cone.path(d['maximum'],d['km']+side*np.pi/2,0.,d['half_thickness'])
        if d['front_first']:
            near,far=d['first'],d['last'];rn,rf=d['radius_in'],d['radius_out'];direction=-1.
        else:
            near,far=d['last'],d['first'];rn,rf=d['radius_out'],d['radius_in'];direction=1.
        c1,length1=arc_to_circle(cone,maximum,d['km'],near,rn,side,direction)
        def crossing(v):
            a=cone.path(maximum,d['km'],c1,v[0])
            b=cone.path(d['transition'],d['kt']+side*np.pi/2,0.,v[1])
            return (a-b)*np.array([1.,cone.radius])
        length_t,thickness_t=check_root(crossing,[d['transition'][0]-maximum[0],d['half_thickness']])
        transition=cone.path(maximum,d['km'],c1,length_t)
        kt=d['km']+c1*length_t
        c2,length2=arc_to_circle(cone,transition,kt,far,rf,side,-direction)
        length_a=abs(length1-length_t);length_b=abs(length2)
        s=np.linspace(0,length_a+length_b,points)
        if d['front_first']:
            coordinate=length1+np.minimum(s,length_a)
            path=cone.path(maximum,d['km'],c1,coordinate)
            angles=d['km']+c1*coordinate
            rear=s>length_a
            path[rear]=cone.path(transition,kt,c2,s[rear]-length_a)
            angles[rear]=kt+c2*(s[rear]-length_a)
        else:
            coordinate=length2+np.minimum(s,length_b)
            path=cone.path(transition,kt,c2,coordinate)
            angles=kt+c2*coordinate
            rear=s>length_b
            path[rear]=cone.path(maximum,d['km'],c1,length_t+s[rear]-length_b)
            angles[rear]=d['km']+c1*(length_t+s[rear]-length_b)
        out.append(dict(path=path,kappa=angles,xy=cone.xy(path),
                        maximum=maximum,transition=transition,thickness_transition=thickness_t,
                        rates=[c1,c2],lengths=[length1,length_t,length2]))
    return d,out


def shock_foot(raw,blade_count):
    d,ss=surfaces(raw);cone=d['cone'];surface=ss[0]
    adjacent=np.array([0.,2*np.pi/blade_count]);target=cone.xy(adjacent)
    # Local cubic interpolation gives a continuous location and direction;
    # the dense source path and exact path angles are retained for checking.
    from scipy.interpolate import CubicSpline
    s=np.r_[0.,np.cumsum(np.linalg.norm(np.diff(surface['xy'],axis=0),axis=1))]
    xy=CubicSpline(s,surface['xy']);ka=CubicSpline(s,surface['kappa']);th=CubicSpline(s,surface['path'][:,1])
    distances=np.linalg.norm(surface['xy']-target,axis=1);j=int(np.argmin(distances))
    result=minimize_scalar(lambda a:np.sum((xy(a)-target)**2),bounds=(s[max(0,j-1)],s[min(len(s)-1,j+1)]),method='bounded',options={'xatol':1e-14})
    candidates=[0.,s[-1],result.x];foot=min(candidates,key=lambda a:np.sum((xy(a)-target)**2))
    local=float(ka(foot));developed=local+np.sin(cone.angle)*(float(th(foot))-adjacent[1])
    return dict(local_foot_deg=float(np.degrees(local)),developed_foot_deg=float(np.degrees(developed)),
                leading_deg=float(np.degrees(surface['kappa'][0])),
                foot_path_fraction=foot/s[-1],turn_rate_reconstructed=d['front_rate']/d['rear_rate'],
                printed_turn_rate=float(raw.get('TURN RATE','nan')))
