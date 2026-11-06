"""Low-speed periodic Hess–Smith cascade reference.

Constant source panels, one circulation density and trailing-edge
tangency follow Hess and Smith (1967), DOI 10.1016/0376-0421(67)90003-6.
The periodic point-source kernel follows by summing 1/(z-i n pitch)
in symmetric pairs. Its value is pi/pitch times coth(pi z/pitch).
"""
from dataclasses import dataclass
from functools import cached_property

import numpy as np
from scipy.linalg import lu_factor, lu_solve
from scipy.linalg import solve as solve_linear
from scipy.special import roots_legendre


@dataclass(frozen=True)
class Cascade:
    centres: np.ndarray
    tangential_speed: np.ndarray
    pressure_coefficient: np.ndarray
    circulation: float
    exit_angle_deg: float
    normal_residual: float
    net_source: float


@dataclass(frozen=True)
class CascadeSystem:
    centres: np.ndarray
    length: np.ndarray
    tangent: np.ndarray
    source: np.ndarray
    vortex: np.ndarray
    matrix: np.ndarray
    rhs: np.ndarray
    inlet: complex
    inlet_speed: float
    pitch: float
    kutta_pair: tuple

    @cached_property
    def _factorization(self):
        return lu_factor(self.matrix)

    def solve(self, defect_flux=None):
        """Apply the outward derivative of signed Ue delta* around the contour.

        The supplied perturbation has one value per contour vertex,
        including the duplicate closing vertex. A periodic flux makes
        the integrated wall-normal forcing exactly zero in the discrete
        balance. The Kutta panels require zero prescribed normal speed.
        """
        n = self.length.size
        if defect_flux is None:
            normal = np.zeros(n)
            density = solve_linear(self.matrix, self.rhs)
        else:
            flux = np.asarray(defect_flux, dtype=float)
            if flux.shape != (n + 1,) or not np.all(np.isfinite(flux)) or flux[0] != flux[-1]:
                raise ValueError("finite, periodic signed displacement flux required on contour vertices")
            normal = np.diff(flux) / self.length
            if np.any(normal[list(self.kutta_pair)] != 0):
                raise ValueError("the prescribed displacement flux must be constant across Kutta panels")
            rhs = self.rhs.copy()
            rhs[:n] += normal
            density = lu_solve(self._factorization, rhs)
        velocity = self.inlet + self.source @ density[:n] + self.vortex * density[n]
        local = velocity * self.tangent
        circulation = float(density[n] * self.length.sum())
        outlet = self.inlet - 1j * circulation / self.pitch
        speed = self.inlet_speed
        return Cascade(
            np.c_[self.centres.real, self.centres.imag], local.real, 1 - abs(local / speed)**2,
            circulation, float(-np.degrees(np.angle(outlet))),
            float(np.max(abs(local.imag - normal)) / speed), float(self.length @ density[:n]),
        )


def _source_influence(z, start, end, pitch):
    delta = end - start
    length = abs(delta)
    left, right = z[:, None] - start, z[:, None] - end
    # Exterior limit on the diagonal of a counterclockwise contour.
    ratio = left / right
    np.fill_diagonal(ratio, -1 + 0j)
    isolated = np.log(ratio) * length / delta
    # Integrate the regular contribution from the periodic images. Subtract
    # the upstream limit to make the supplied inlet the actual far field.
    nodes, weights = roots_legendre(12)
    correction = np.zeros_like(isolated)
    for node, weight in zip(nodes, weights):
        q = (left - (node + 1) / 2 * delta) * np.pi / pitch
        correction += weight * (1 / np.tanh(q) - 1 / q + 1)
    return isolated / (2 * np.pi) + correction * length / (4 * pitch)


def prepare(contour, pitch, inlet_speed, inlet_angle_deg, kutta_pair):
    """Assemble a closed CCW contour in axial/pitch coordinates.

    The two Kutta indices designate panels at opposite sides of the
    trailing edge with oppositely directed tangents. For a rounded edge
    they are an explicit modelling choice. Angles are measured from axial.
    """
    xy = np.asarray(contour, dtype=float)
    if (xy.ndim != 2 or xy.shape[1] != 2 or len(xy) < 5 or not np.all(np.isfinite(xy))
            or not np.array_equal(xy[0], xy[-1])):
        raise ValueError("a finite closed blade contour is required")
    if not (np.isfinite(pitch) and pitch > 0 and np.isfinite(inlet_speed) and inlet_speed > 0
            and np.isfinite(inlet_angle_deg) and abs(inlet_angle_deg) < 90):
        raise ValueError("positive pitch and positive axial inlet flow required")
    z = xy[:, 0] + 1j * xy[:, 1]
    start, end = z[:-1], z[1:]
    length = abs(end - start)
    if np.any(length == 0) or np.imag(np.vdot(start, end)) <= 0:
        raise ValueError("panels must be distinct and counterclockwise")
    first, last = kutta_pair
    if first == last or not all(0 <= i < len(length) for i in (first, last)):
        raise ValueError("two distinct trailing-edge panels are required")
    tangent = (end - start) / length
    centres = (start + end) / 2
    source = _source_influence(centres, start, end, pitch)
    vortex = -1j * source.sum(axis=1)
    tangent_influence = np.real(source * tangent[:, None])
    normal_influence = np.imag(source * tangent[:, None])
    vortex_local = vortex * tangent
    inlet = inlet_speed * np.exp(-1j * np.deg2rad(inlet_angle_deg))
    inlet_local = inlet * tangent
    n = len(length)
    matrix = np.zeros((n + 2, n + 2))
    matrix[:n, :n] = normal_influence
    matrix[:n, n] = vortex_local.imag
    # A uniform residual allows exact zero net source and therefore axial
    # mass closure. Its magnitude is reported as a discretization residual.
    matrix[:n, n + 1] = -1.
    matrix[n, :n] = length / length.sum()
    matrix[n + 1, :n] = tangent_influence[first] + tangent_influence[last]
    matrix[n + 1, n] = vortex_local[first].real + vortex_local[last].real
    rhs = np.r_[-inlet_local.imag, 0., -inlet_local[first].real - inlet_local[last].real]
    return CascadeSystem(centres, length, tangent, source, vortex, matrix, rhs,
                         inlet, inlet_speed, pitch, kutta_pair)


def solve(contour, pitch, inlet_speed, inlet_angle_deg, kutta_pair):
    """Solve the impermeable-wall periodic reference."""
    return prepare(contour, pitch, inlet_speed, inlet_angle_deg, kutta_pair).solve()
