"""Two-way interaction on specified attached parts of a periodic blade.

The transpiration condition uses the derivative of signed Ue delta*,
following Fidkowski (2021), DOI 10.2514/1.J061341, eq. 23. A compact
window isolates each perturbation from the nose, trailing edge and wake.
The window is a research boundary condition, not a model of those regions.
"""
from dataclasses import dataclass

import numpy as np
from scipy.interpolate import PchipInterpolator

from validation.blade_layer_reference import BladeLayer, march
from validation.periodic_cascade_reference import Cascade, CascadeSystem


@dataclass(frozen=True)
class AttachedPatch:
    vertices: np.ndarray
    start: float
    end: float
    theta0: float
    hk0: float


@dataclass(frozen=True)
class PatchResult:
    cascade: Cascade
    layers: tuple[BladeLayer, ...]
    flux: np.ndarray
    initial_residual: float
    residual: float
    iterations: int


class PatchFailure(RuntimeError):
    def __init__(self, reason, iteration, message):
        super().__init__(message)
        self.reason = reason
        self.iteration = iteration


def solve_patches(system: CascadeSystem, patches, *, total_temperature, total_pressure,
                  tolerance=1e-7, max_iterations=80):
    """Iterate attached-layer defect and potential pressure to a fixed point.

    The active intervals are measured by arc length along the supplied
    vertex paths in local flow direction. Normal speed is prescribed only
    through the derivative of the compact perturbation. The convergence
    check compares the implied normal speeds, not just nodal defect values.
    """
    if (not np.isfinite(tolerance) or tolerance <= 0
            or not isinstance(max_iterations, int) or max_iterations < 1):
        raise ValueError("positive tolerance and iteration budget required")
    prepared = []
    used = set()
    for patch in patches:
        nodes = np.asarray(patch.vertices)
        if (nodes.ndim != 1 or nodes.size < 3 or not np.issubdtype(nodes.dtype, np.integer)
                or np.any(nodes < 0) or np.any(nodes > system.length.size)):
            raise ValueError("a wall patch requires at least three valid vertices")
        direction = int(nodes[1] - nodes[0])
        if abs(direction) != 1 or np.any(np.diff(nodes) != direction):
            raise ValueError("wall vertices must be consecutive in the flow direction")
        panels = np.minimum(nodes[:-1], nodes[1:])
        arc = np.r_[0., np.cumsum(system.length[panels])]
        centres = (arc[:-1] + arc[1:]) / 2
        if not centres[0] <= patch.start < patch.end <= centres[-1]:
            raise ValueError("active interval must lie inside the supplied wall edge samples")
        active = (arc > patch.start) & (arc < patch.end)
        if not np.any(active):
            raise ValueError("patch contains no interior vertices")
        vertices = nodes[active]
        if used.intersection(vertices):
            raise ValueError("patches overlap")
        used.update(vertices)
        samples = np.r_[patch.start, arc[active], patch.end]
        window = np.sin(np.pi * (samples[1:-1] - patch.start) / (patch.end - patch.start))**2
        prepared.append((patch, direction, panels, centres, vertices, samples, window))
    if not prepared:
        raise ValueError("at least one attached patch is required")

    flux = np.zeros(system.length.size + 1)
    for iteration in range(1, max_iterations + 1):
        cascade = system.solve(flux)
        updated = np.zeros_like(flux)
        layers = []
        for patch, direction, panels, centres, vertices, samples, window in prepared:
            speed = direction * cascade.tangential_speed[panels]
            # The direct solver needs positive edge speeds. Trim unused
            # portions of the wall, retaining both bracketing edge knots.
            first = np.searchsorted(centres, samples[0], side="right") - 1
            stop = np.searchsorted(centres, samples[-1], side="left") + 1
            edge_arc, edge_speed = centres[first:stop], speed[first:stop]
            if np.any(edge_speed <= 0):
                raise PatchFailure("reverse_edge_flow", iteration,
                                   "trial potential edge reverses inside the active patch")
            try:
                layer = march(
                    edge_arc, edge_speed, theta0=patch.theta0, hk0=patch.hk0,
                    total_temperature=total_temperature, total_pressure=total_pressure,
                    sample_at=samples, rtol=min(1e-10, tolerance / 100),
                )
            except RuntimeError as exc:
                raise PatchFailure("layer_numerical_failure", iteration, str(exc)) from exc
            if layer.separated:
                raise PatchFailure("attached_patch_limit", iteration,
                                   "trial layer reaches zero shear before the patch ends")
            speed_on_vertices = PchipInterpolator(edge_arc, edge_speed)(samples[1:-1])
            updated[vertices] = direction * window * speed_on_vertices * layer.displacement_thickness[1:-1]
            layers.append(layer)
        residual = float(np.max(abs(np.diff(updated - flux) / system.length)) / system.inlet_speed)
        if iteration == 1:
            initial_residual = residual
        if residual <= tolerance:
            return PatchResult(cascade, tuple(layers), flux, initial_residual, residual, iteration)
        flux = 0.5 * (flux + updated)
    raise PatchFailure("interaction_numerical_failure", max_iterations,
                       "prescribed normal speed and layer defect did not reach a common state")
