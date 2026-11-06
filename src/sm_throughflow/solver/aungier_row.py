"""Aungier's axial-compressor blade-row model, applied on every stream surface.

R. H. Aungier, *Axial-Flow Compressors*, ASME Press, 2003: the cascade
correlations of chapter 6 (``sm_throughflow.correlations.aungier``), the
stream-surface blade geometry of section 9.1 and the loss limit and smoothing
of section 9.2. docs/compressor_row_model.md describes the assembly and the
choices the book leaves open.
"""
from dataclasses import dataclass
from typing import Callable, Optional, Sequence, Union

import numpy as np

from ..correlations import aungier as A
from ..correlations import nasa_lewis as L
from .gas import PerfectGas
from .errors import PhysicalStateError, SolverError
from .quasi_normal import StationFlow
from .rows import BladeRow, ExitGeometry, RowPerformance

PROFILES = ("naca65", "c4", "dca", "mca")
CAMBERLINES = ("naca65", "circular_arc", "parabolic_arc", "multiple_circular_arc")
_DEFAULT_CAMBERLINE = {"naca65": "naca65", "c4": "circular_arc", "dca": "circular_arc", "mca": "multiple_circular_arc"}


@dataclass(frozen=True)
class BladeSections:
    """Blade sections on cylinders of radius ``radius`` (m), hub to tip.

    ``kappa_in`` and ``kappa_out`` are the blade angles in degrees from the
    axial direction, positive toward rotation (the solver's sign convention);
    ``chord`` is in metres and ``t_c`` is the maximum thickness to chord.
    With ``coordinate="span"`` the ``radius`` values are span fractions
    (0 at the hub, 1 at the shroud) instead, and each stream surface takes
    kappa_in at its span fraction on the row's inlet quasi-normal, kappa_out at
    its span fraction on the exit quasi-normal and the rest at their mean.
    """

    radius: Sequence[float]
    kappa_in: Sequence[float]
    kappa_out: Sequence[float]
    chord: Sequence[float]
    t_c: Sequence[float]
    coordinate: str = "radius"

    def __post_init__(self):
        r = np.asarray(self.radius, dtype=float)
        if self.coordinate not in ("radius", "span"):
            raise ValueError("coordinate must be 'radius' or 'span'")
        if r.ndim != 1 or r.size < 2 or np.any(np.diff(r) <= 0.0):
            raise ValueError("section radii must be at least two increasing values")
        for name in ("kappa_in", "kappa_out", "chord", "t_c"):
            if np.asarray(getattr(self, name), dtype=float).shape != r.shape:
                raise ValueError("{} needs one value per section radius".format(name))

    def at(self, name, r):
        radius = np.asarray(self.radius, dtype=float)
        r = np.asarray(r, dtype=float)
        span = radius[-1] - radius[0]
        if np.any(r < radius[0] - 1e-6 * span) or np.any(r > radius[-1] + 1e-6 * span):
            raise ValueError("stream surfaces at {} {:.6g} to {:.6g} lie outside the blade sections ({:.6g} to {:.6g})".format(self.coordinate, r.min(), r.max(), radius[0], radius[-1]))
        return np.interp(r, radius, np.asarray(getattr(self, name), dtype=float))


@dataclass(frozen=True)
class TipClearance:
    """Clearance gap ``gap`` (m) at the ``shroud`` (rotors) or ``hub`` (unshrouded stators)."""

    gap: float
    wall: str = "shroud"


@dataclass(frozen=True)
class ShroudSeal:
    """Labyrinth seal under a stator's shroud band (Aungier section 6.10), lengths in metres."""

    radius: float
    clearance: float
    fin_count: int
    fin_pitch: float
    fin_thickness: float
    wall: str = "hub"


def smooth_loss(dp):
    """Aungier's spanwise smoothing of the total-pressure loss (9-9 to 9-11), stream surfaces hub to shroud.

    The book prints the shroud end point (9-11) with index N - 3; the
    symmetric form with N - 2, used here, is the one that keeps the
    trapezoidal integral over the two wall stream sheets unchanged, the
    property the book states for both end points.
    """
    dp = np.asarray(dp, dtype=float)
    if dp.size < 3:
        return dp.copy()
    out = dp.copy()
    out[1:-1] = (dp[:-2] + 2.0 * dp[1:-1] + dp[2:]) / 4.0  # (9-9)
    out[0] = 2.0 * out[1] - out[2]  # (9-10)
    out[-1] = 2.0 * out[-2] - out[-3]  # (9-11), N - 2
    return out


class AungierCompressorRow:
    """Exit flow angle, loss and wake blockage of a compressor blade row (a ``RowModel``).

    ``omega`` must equal the speed of the ``BladeRow`` that carries the model;
    ``blade_row`` builds that row. ``profile`` sets the thickness distribution
    (K_sh and the W_max incidence coefficient); ``camberline`` the deviation
    model: Lieblein's for ``naca65`` and ``circular_arc``, Howell's for
    ``parabolic_arc`` and for every inlet guide vane. ``row_number`` counts
    rows from 1 at the compressor inlet (6-87).
    """

    def __init__(
        self,
        sections: BladeSections,
        blade_count: int,
        omega: float,
        gas: PerfectGas = PerfectGas(),
        profile: str = "naca65",
        camberline: Optional[str] = None,
        a_c: float = 0.5,
        row_number: int = 1,
        inlet_guide_vane: bool = False,
        clearance: Optional[TipClearance] = None,
        seal: Optional[ShroudSeal] = None,
        throat_over_pitch: Optional[Sequence[float]] = None,
        expansion_angle: Optional[Sequence[float]] = None,
        section_shape: Optional[dict] = None,
        viscosity: Optional[Union[float, Callable]] = None,
        K1: float = 0.0073,
        max_loss: float = 0.5,
        smoothing: bool = True,
        shock_mean: str = "arithmetic",
        shock_surface_angles: Optional[dict] = None,
    ):
        if profile not in PROFILES:
            raise ValueError("profile must be one of {}".format(PROFILES))
        camberline = _DEFAULT_CAMBERLINE[profile] if camberline is None else camberline
        if camberline not in CAMBERLINES:
            raise ValueError("camberline must be one of {}".format(CAMBERLINES))
        if camberline == "naca65" and a_c != 0.5:
            raise ValueError("the NACA-65 camberline has a/c = 0.5")
        if (camberline == "multiple_circular_arc") != (section_shape is not None):
            raise ValueError("the multiple_circular_arc camberline needs its section_shape, and only it")
        if clearance is not None and seal is not None:
            raise ValueError("a row has a clearance gap or a shroud seal, not both")
        turning = np.mean(np.asarray(sections.kappa_in, dtype=float) - np.asarray(sections.kappa_out, dtype=float))
        if turning == 0.0:
            raise ValueError("the blade has no camber")
        self.sections = sections
        self.blade_count = int(blade_count)
        self.omega = float(omega)
        self.gas = gas
        self.profile = profile
        self.camberline = camberline
        self.a_c = float(a_c)
        self.row_number = int(row_number)
        self.inlet_guide_vane = bool(inlet_guide_vane)
        self.clearance = clearance
        self.seal = seal
        self.throat_over_pitch = throat_over_pitch
        self.expansion_angle = expansion_angle
        if shock_surface_angles is not None:
            leading = np.asarray(shock_surface_angles["leading"], dtype=float)
            foot = np.asarray(shock_surface_angles["foot"], dtype=float)
            if leading.ndim != 1 or len(leading) < 2 or foot.shape != leading.shape or not np.all(np.isfinite([leading, foot])):
                raise ValueError("shock surface angles need matching finite span arrays")
        self.shock_surface_angles = shock_surface_angles
        self.shock_surfaces = None
        if shock_surface_angles is not None and "surfaces" in shock_surface_angles:
            surfaces = np.asarray(shock_surface_angles["surfaces"], dtype=float)
            if (surfaces.ndim != 3 or surfaces.shape[0] != len(leading) or surfaces.shape[1] < 3
                    or surfaces.shape[2] != 2 or not np.all(np.isfinite(surfaces))
                    or np.any(np.sum(np.diff(surfaces, axis=1)**2, axis=2) <= 0)):
                raise ValueError("shock surfaces need matching finite span curves with distinct points")
            self.shock_surfaces = surfaces.copy()
        self.section_shape = section_shape
        self.viscosity = viscosity
        self.K1 = float(K1)
        self.max_loss = float(max_loss)
        self.smoothing = bool(smoothing)
        self.shock_mean = shock_mean
        # The cascade frame (correlations/__init__.py) has camber >= 0.
        self.sign = 1.0 if turning > 0.0 else -1.0
        self.k_sh = A.PROFILE_SHAPE_FACTOR[profile]
        self.incidence_coefficient = A.MAX_VELOCITY_INCIDENCE_COEFFICIENT.get(profile, A.MAX_VELOCITY_INCIDENCE_COEFFICIENT["c4"])
        self._cached = None  # (inlet, exit geometry, results) of the last call

    def blade_row(self, name: str, inlet: int) -> BladeRow:
        return BladeRow(name=name, inlet=inlet, omega=self.omega, model=self)

    # -------------------------------------------------------------- geometry
    def _geometry(self, inlet: StationFlow, exit_geometry: ExitGeometry):
        r1, r2 = inlet.r, exit_geometry.r
        sec = self.sections
        # Where the sections are read: radius, or span fraction on each quasi-normal.
        at1, at2 = (r1, r2) if sec.coordinate == "radius" else (inlet.t, exit_geometry.t)
        at_mean = 0.5 * (at1 + at2)
        phi = np.arctan2(r2 - r1, exit_geometry.z - inlet.z)  # (9-1)
        cos_phi = np.cos(phi)
        k1 = np.degrees(np.arctan(cos_phi * np.tan(np.radians(sec.at("kappa_in", at1)))))  # (9-4)
        k2 = np.degrees(np.arctan(cos_phi * np.tan(np.radians(sec.at("kappa_out", at2)))))  # (9-5)
        chord = sec.at("chord", at_mean) / cos_phi  # (9-2)
        t_c = sec.at("t_c", at_mean) * cos_phi  # (9-3)
        pitch = np.pi * (r1 + r2) / self.blade_count  # (9-6)
        k1, k2 = self.sign * k1, self.sign * k2
        theta = k1 - k2
        if self.section_shape is None:
            a_c = self.a_c
            chi1, _ = A.camberline_angles(theta, a_c)
        else:
            # Multiple circular arc: chi1/theta and the position of maximum camber of the constructed
            # meanline at the design sections, read at each stream surface's span fraction.
            radius = np.asarray(sec.radius, dtype=float)
            where = (at_mean - radius[0]) / (radius[-1] - radius[0])
            grid = np.linspace(0.0, 1.0, len(self.section_shape["a_c"]))
            a_c = np.interp(where, grid, np.asarray(self.section_shape["a_c"], dtype=float))
            chi1 = theta * np.interp(where, grid, np.asarray(self.section_shape["chi1_over_camber"], dtype=float))
        stagger = k1 - chi1  # (4-32)
        height = 0.5 * (inlet.y[-1] + exit_geometry.y[-1])
        return dict(k1=k1, k2=k2, theta=theta, stagger=stagger, chord=chord, t_c=t_c, pitch=pitch, sigma=chord / pitch, height=height, a_c=a_c)

    # ------------------------------------------------------- design condition
    def _zero_camber_deviation(self, beta1, sigma):
        # (6-20) is fitted for beta1 >= 0; a symmetric section at -beta1 deviates by the opposite amount.
        return np.sign(beta1) * A.lieblein_zero_camber_deviation(np.abs(beta1), sigma)

    def _design_deviation(self, g, beta1_star):
        theta, sigma, t_c = g["theta"], g["sigma"], g["t_c"]
        thickness = self.k_sh * A.thickness_deviation_factor(t_c)
        delta0 = self._zero_camber_deviation(beta1_star, sigma)
        if self.inlet_guide_vane or self.camberline == "parabolic_arc":
            root = np.sqrt(sigma)
            howell = (0.92 * g["a_c"] ** 2 + 0.002 * g["k2"]) / (1.0 - 0.002 * theta / root) * theta / root
            return howell + (thickness - 1.0) * delta0  # (6-26)
        if self.camberline == "multiple_circular_arc":
            # The NASA Lewis design code's rule for the sections it designed (correlations.nasa_lewis).
            return L.carter_deviation(theta, g["stagger"], g["a_c"], sigma)
        camberline = "naca65" if self.camberline == "naca65" else "circular_arc"
        return thickness * delta0 + A.lieblein_deviation_slope(np.abs(beta1_star), sigma, camberline) * theta  # (6-19)

    # ---------------------------------------------------------------- model
    def _inlet_part(self, inlet: StationFlow, exit_geometry: ExitGeometry):
        """Everything that depends on the blade and the inlet flow only, not on the exit flow."""
        gas, omega, sign = self.gas, self.omega, self.sign
        g = self._geometry(inlet, exit_geometry)
        k1, theta, stagger, sigma, t_c = g["k1"], g["theta"], g["stagger"], g["sigma"], g["t_c"]
        r1 = inlet.r
        wm1 = inlet.Wm
        w_theta1 = inlet.C_theta - omega * r1
        beta1 = sign * np.degrees(np.arctan2(w_theta1, wm1))
        w1 = np.hypot(wm1, w_theta1)
        mach1 = w1 / inlet.a
        h_rel1 = inlet.h + 0.5 * w1 ** 2
        pt1 = gas.pressure(h_rel1, inlet.s)
        h_sonic = 2.0 / (gas.gamma + 1.0) * h_rel1  # perfect gas: T* = 2 T't / (gamma + 1)
        w_sonic = gas.sound_speed(h_sonic)
        rho_w_sonic = gas.density(h_sonic, inlet.s) * w_sonic

        # Design incidence and deviation (6-8), (6-18), (6-19)/(6-26).
        alpha_star = A.design_angle_of_attack(theta, sigma, t_c, g["a_c"], self.k_sh)
        i_star = A.incidence_from_angle_of_attack(alpha_star, stagger, k1)
        delta_star = self._design_deviation(g, k1 + i_star)

        # Low-loss incidence range, Mach number and choke: (6-47) to (6-55).
        alpha_c, alpha_s = A.stall_angles_for_blade(alpha_star, theta, stagger)
        R_c = i_star - A.incidence_from_angle_of_attack(alpha_c, stagger, k1)  # (6-49)
        R_s = A.incidence_from_angle_of_attack(alpha_s, stagger, k1) - i_star  # (6-50)
        i_c, i_s = A.stall_incidence(i_star, R_c, R_s, mach1, self.k_sh)
        if self.throat_over_pitch is None:
            o_s = A.throat_opening_ratio(stagger, A.lift_coefficient_from_camber(theta, g["a_c"]), t_c, sigma)  # (4-30), (4-31)
        else:
            o_s = np.interp(exit_geometry.t, np.linspace(0.0, 1.0, len(self.throat_over_pitch)), np.asarray(self.throat_over_pitch, dtype=float))
        beta1_choke = A.choke_inlet_angle(o_s, rho_w_sonic, inlet.rho * w1)
        i_c = np.fmax(i_c, beta1_choke - k1 + 1.0)  # (6-54); NaN where the passage cannot choke
        i_m = A.minimum_loss_incidence(i_c, i_s, R_c, R_s)

        # NACA RM E57A30 appendix B: nu_s = nu_1 + beta_1 - surface_angle_at_foot.
        # The geometric surface turning used through v12 implicitly imposed
        # tangent incidence. Preserve that low-level approximation only when
        # no constructed foot is available (NACA65/C4 analytic approximation).
        if self.shock_surface_angles is not None:
            cp = np.cos(np.arctan2(exit_geometry.r - inlet.r, exit_geometry.z - inlet.z))
            def projected(key):
                values = self.shock_surface_angles[key]
                angle = np.interp(inlet.t, np.linspace(0., 1., len(values)), values)
                return np.degrees(np.arctan(cp * np.tan(np.radians(angle))))
            if self.shock_surfaces is None:
                leading, foot = projected("leading"), projected("foot")
            else:
                from ..correlations.blade_geometry import projected_surface_shock_angles
                coordinate = np.clip(inlet.t, 0., 1.)*(len(self.shock_surfaces)-1)
                lower = np.minimum(coordinate.astype(int), len(self.shock_surfaces)-2)
                weight = (coordinate-lower)[:, None, None]
                surfaces = (1.-weight)*self.shock_surfaces[lower]+weight*self.shock_surfaces[lower+1]
                leading, foot = projected_surface_shock_angles(surfaces, cp)
            expansion = beta1 - foot
            suction_incidence = beta1 - leading
        elif self.expansion_angle is None:
            expansion = A.suction_surface_expansion_angle(k1, theta, t_c, sigma)  # (6-65) to (6-69)
            suction_incidence = np.full_like(beta1, np.nan)
        else:
            expansion = np.interp(inlet.t, np.linspace(0.0, 1.0, len(self.expansion_angle)), np.asarray(self.expansion_angle, dtype=float))
            suction_incidence = np.full_like(beta1, np.nan)
        from .shock_integration import integrated_shock_loss
        pointwise_shock = A.shock_loss(mach1, expansion, gas.gamma, self.shock_mean)
        omega_shock = integrated_shock_loss(mach1, expansion, pt1-inlet.P, inlet.tube_mass_flows, gas.gamma, self.shock_mean)
        return dict(g=g, wm1=wm1, beta1=beta1, w1=w1, mach1=mach1, pt1=pt1, w_sonic=w_sonic, i_star=i_star, delta_star=delta_star,
                    throat_capacity_margin=o_s * rho_w_sonic / (inlet.rho * wm1) - 1.0,
                    R_s=R_s, i_c=i_c, i_s=i_s, i_m=i_m, omega_shock=omega_shock,
                    pointwise_shock=pointwise_shock,
                    shock_flow_turning=expansion, suction_surface_incidence=suction_incidence,
                    shock_compression_clipped=(mach1 > 1.) & (expansion < 0.))

    def __call__(self, inlet: StationFlow, exit: Optional[StationFlow], exit_geometry: ExitGeometry) -> RowPerformance:
        gas, omega, sign = self.gas, self.omega, self.sign
        cached = self._cached
        if cached is not None and cached[0] is inlet and cached[1] is exit_geometry:
            part = cached[2]
        else:
            part = self._inlet_part(inlet, exit_geometry)
            self._cached = (inlet, exit_geometry, part)
        g = part["g"]
        k1, k2, theta, stagger, sigma, t_c = g["k1"], g["k2"], g["theta"], g["stagger"], g["sigma"], g["t_c"]
        r1, r2 = inlet.r, exit_geometry.r
        wm1, beta1, w1, mach1, pt1, w_sonic = part["wm1"], part["beta1"], part["w1"], part["mach1"], part["pt1"], part["w_sonic"]
        i_star, delta_star, R_s, i_c, i_s, i_m = part["i_star"], part["delta_star"], part["R_s"], part["i_c"], part["i_s"], part["i_m"]
        omega_shock = part["omega_shock"]
        head1 = pt1 - inlet.P
        incidence = beta1 - k1

        # Exit meridional state: the current estimate, or the inlet's on the first pass.
        if exit is None:
            wm2, rho2, p2, h2_static = wm1, inlet.rho, inlet.P, inlet.h
        else:
            wm2, rho2, p2, h2_static = exit.Wm, exit.rho, exit.P, exit.h

        # NASA TN D-7345's equivalent-camber rule depends on the EXIT state;
        # it must not be stored in the inlet-only cache. Use it consistently
        # in both the reference loss triangle and the outgoing flow triangle.
        equivalent_carter = self.camberline == "multiple_circular_arc" and not self.inlet_guide_vane
        if equivalent_carter:
            try:
                delta_star = L.annular_carter_deviation(k1, k2, stagger, g["a_c"], sigma,
                                                       wm1, wm2, r1, r2, sign*omega)
            except ValueError as exc:
                raise SolverError(str(exc), kind="outside_model_scope", component="mca_deviation") from exc

        # Design loss at the design incidence and deviation, with the actual meridional velocities (6-39), (6-46).
        beta1_star, beta2_star = k1 + i_star, k2 + delta_star
        b1s, b2s = np.radians(beta1_star), np.radians(beta2_star)
        c_theta1_star = wm1 * np.tan(b1s) + sign * omega * r1  # absolute swirl, cascade frame
        c_theta2_star = wm2 * np.tan(b2s) + sign * omega * r2
        ratio_star = A.max_velocity_ratio_annular(beta1_star, sigma, r1, c_theta1_star, r2, c_theta2_star, wm1)
        w1_star, w2_star = wm1 / np.cos(b1s), wm2 / np.cos(b2s)
        D_eq_star = A.equivalent_diffusion_factor(ratio_star, w1_star, w2_star)
        reynolds = np.full_like(w1, np.nan)
        k_re = np.zeros_like(w1)
        if self.viscosity is not None:
            mu = np.asarray(self.viscosity(inlet.T) if callable(self.viscosity) else self.viscosity, dtype=float)
            if not np.all(np.isfinite(mu)) or np.any(mu <= 0.0):
                raise PhysicalStateError("blade-row viscosity must be finite and positive", component="row_model")
            reynolds = inlet.rho * w1 * g["chord"] / mu
            k_re = A.reynolds_loss_factor(reynolds)
        K2 = A.endwall_loss_constant(g["pitch"] / g["height"], beta2_star, k_re, self.K1)  # (6-99), (6-100)
        omega_star = A.design_loss_from_equivalent_diffusion(D_eq_star, beta2_star, w1_star / w2_star, sigma, self.K1, K2)
        critical_mach = mach1 * w_sonic / (ratio_star * w1_star)  # (6-59), W_max from (6-39) at i*, delta*
        omega_m = A.minimum_loss(omega_star, i_m, i_star, R_s, mach1, critical_mach, w_sonic / w1, self.k_sh)  # (6-58), (6-60)

        # Off-design loss and deviation (6-76 to 6-82).
        omega_profile = A.off_design_loss(incidence, i_m, i_c, i_s, omega_m, omega_shock)
        slope = A.deviation_slope(np.abs(beta1_star), sigma)
        if equivalent_carter:
            # Hybrid off-design extension: retain Aungier's incidence slope.
            # Radius/velocity effects are already in the implicit reference;
            # adding 10*(1-wm2/wm1) would count them a second time.
            delta = delta_star + slope*(incidence-i_star)
        else:
            delta = A.off_design_deviation(delta_star, slope, incidence, i_star, wm2 / wm1, self.inlet_guide_vane)
        beta2 = k2 + delta
        b2 = np.radians(beta2)

        # Exit kinematics in the solver frame and wake blockage (6-83, 6-84) at the actual incidence.
        w_theta2 = sign * wm2 * np.tan(b2)
        c_theta2 = w_theta2 + omega * r2
        w2 = np.hypot(wm2, w_theta2)
        excess = np.maximum(incidence - i_star, 0.0)
        ratio = A.max_velocity_ratio_annular(beta1, sigma, r1, sign * inlet.C_theta, r2, sign * c_theta2, wm1, excess, self.incidence_coefficient)
        D_eq = A.equivalent_diffusion_factor(ratio, w1, w2)
        wake = A.wake_blockage(D_eq)

        # Leakage losses (sections 6.9, 6.10), as total-pressure losses spread over the span.
        mass_fraction = np.linspace(0.0, 1.0, r1.size)
        dp_clearance = np.zeros_like(r1)
        dp_seal = np.zeros_like(r1)
        seal_leak = 0.0
        if self.clearance is not None:
            j = -1 if self.clearance.wall == "shroud" else 0
            rho_mean = 0.5 * (inlet.rho[j] + rho2[j])
            dp_blade = A.blade_pressure_difference(
                r1[j], inlet.rho[j], wm1[j], r2[j], rho2[j], wm2[j], r1[j] * inlet.C_theta[j], r2[j] * c_theta2[j],
                self.blade_count, 0.5 * (r1[j] + r2[j]), g["chord"][j], stagger[j])
            dp_row = A.tip_clearance_loss(dp_blade, rho_mean, self.clearance.gap, self.blade_count, g["chord"][j], stagger[j], inlet.mass_flow, self.row_number)
            dp_clearance = dp_row * A.leakage_loss_distribution(mass_fraction, gap_at_hub=self.clearance.wall == "hub")
        if self.seal is not None:
            seal = self.seal
            j = 0 if seal.wall == "hub" else -1
            p_in, p_out = inlet.P[j], p2[j]
            high_is_exit = p_out >= p_in
            rho_high = rho2[j] if high_is_exit else inlet.rho[j]
            t_high = gas.temperature(h2_static[j] if high_is_exit else inlet.h[j])
            ratio_p = min(p_in, p_out) / max(p_in, p_out)
            leak = A.seal_leakage_mass_flow(seal.radius, seal.clearance, seal.fin_thickness, seal.fin_pitch, seal.fin_count, ratio_p, rho_high, t_high, gas.R)
            dp_row = A.seal_leakage_loss(abs(p_out - p_in), leak, inlet.mass_flow)
            seal_leak = float(leak) if high_is_exit else -float(leak)  # positive from discharge to inlet (section 8.6)
            dp_seal = dp_row * A.leakage_loss_distribution(mass_fraction, gap_at_hub=seal.wall == "hub")

        # Limit (9-7) and spanwise smoothing (9-8 to 9-11).
        unlimited_loss = omega_profile + (dp_clearance + dp_seal) / head1
        loss = np.minimum(unlimited_loss, self.max_loss)
        if self.smoothing:
            loss = smooth_loss(loss * head1) / head1

        if not np.all(np.isfinite(loss)) or np.any(loss < 0.0):
            raise PhysicalStateError("row loss is negative or non-finite after smoothing", component="row_model")

        diagnostics = dict(
            throat_capacity_margin=part["throat_capacity_margin"],
            reynolds_number=reynolds, reynolds_loss_factor=k_re,
            loss_limit_active=(unlimited_loss > self.max_loss), unsmoothed_loss=np.minimum(unlimited_loss, self.max_loss),
            incidence=incidence, design_incidence=i_star, negative_stall_incidence=i_c, positive_stall_incidence=i_s,
            minimum_loss_incidence=i_m, deviation=delta, design_deviation=delta_star, relative_inlet_mach=mach1,
            equivalent_carter_active=equivalent_carter,
            annular_design_deviation_correction=delta_star-part["delta_star"],
            critical_mach=critical_mach, equivalent_diffusion=D_eq, design_equivalent_diffusion=D_eq_star,
            design_loss=omega_star, minimum_loss=omega_m, shock_loss=omega_shock, profile_loss=omega_profile,
            pointwise_shock_loss=part["pointwise_shock"],
            shock_flow_turning=part["shock_flow_turning"], suction_surface_incidence=part["suction_surface_incidence"],
            shock_compression_clipped=part["shock_compression_clipped"],
            clearance_loss=dp_clearance / head1, seal_loss=dp_seal / head1, loss=loss, wake_blockage=wake,
            solidity=sigma, stagger=stagger, camber=theta, pitch=g["pitch"], seal_leakage_mass_flow=seal_leak,
        )
        if exit is not None:
            # Blade-row stall criterion (9-16 to 9-19), from the current exit flow.
            w2_exit = np.hypot(exit.Wm, exit.W_theta)
            pt2 = gas.pressure(exit.h + 0.5 * w2_exit ** 2, exit.s)
            diagnostics["equivalent_velocity_ratio"] = A.equivalent_velocity_ratio(pt2, exit.P, pt1, inlet.P)
            diagnostics["stall_velocity_ratio"] = A.stall_velocity_ratio(theta, sigma, stagger, t_c, D_eq)
        return RowPerformance(exit_angle=np.radians(sign * beta2), loss=loss, basis="inlet", wake_blockage=wake, diagnostics=diagnostics)
