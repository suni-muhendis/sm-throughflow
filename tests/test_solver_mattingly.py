"""Mattingly example 9.1 on the streamline-curvature solver.

Inputs as in NASA turbo-design's examples/mattingly-axial-compressor/example9.1.py:
a single stage with 40 deg inlet swirl, rotor exit relative angle -23.87 deg,
stator exit angle 40 deg, no loss. The pressure ratios pinned here are
characterization goldens of this solver, not measurements.
"""
import math

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
    averaged_total_state,
    polytropic_efficiency,
)

GAS = PerfectGas()


def mattingly_9_1(curvature="full", surfaces=11):
    T0, P0 = 518.7 / 1.8, 14.7 * 6894.76
    mass_flow, omega, mean_radius, axial_chord = 50 * 0.453592, 1000.0, 12 * 0.0254, 0.0254
    areas = [207.2 / 39.3701**2, 179.1 / 39.3701**2, 165.3 / 39.3701**2]
    half_heights = [area / (math.pi * 4 * mean_radius) for area in areas]
    z = [0.0, axial_chord, 2 * axial_chord]
    annulus = Annulus.from_points(
        [(zz, mean_radius - h) for zz, h in zip(z, half_heights)],
        [(zz, mean_radius + h) for zz, h in zip(z, half_heights)],
    )
    rows = [
        BladeRow("rotor", 0, omega, PrescribedRow(-23.87)),
        BladeRow("stator", 1, 0.0, PrescribedRow(40.0)),
    ]
    problem = Throughflow(
        annulus, QuasiNormals.on(annulus, z), InletCondition(P0=P0, T0=T0, alpha_deg=40.0),
        mass_flow, rows, GAS, stream_surfaces=surfaces, curvature=curvature,
    )
    return problem.solve()


@pytest.mark.parametrize("curvature", CURVATURE_MODELS)
def test_the_lossless_stage_has_a_polytropic_efficiency_of_exactly_one(curvature):
    solution = mattingly_9_1(curvature)
    assert solution.convergence.converged
    inlet, _, exit = solution.stations
    assert polytropic_efficiency(GAS, inlet, exit) == pytest.approx(1.0, abs=1e-10)


GOLDEN_PRESSURE_RATIO = {"full": 1.294938240, "linear": 1.296278576, "none": 1.309476453}


@pytest.mark.parametrize("curvature", CURVATURE_MODELS)
def test_pressure_ratio_characterization(curvature):
    inlet, _, exit = mattingly_9_1(curvature).stations
    ratio = averaged_total_state(GAS, exit)[1] / averaged_total_state(GAS, inlet)[1]
    assert ratio == pytest.approx(GOLDEN_PRESSURE_RATIO[curvature], abs=1e-8)


def test_the_solution_is_deterministic():
    first, second = mattingly_9_1(), mattingly_9_1()
    for a, b in zip(first.stations, second.stations):
        assert np.array_equal(a.Wm, b.Wm)
        assert np.array_equal(a.P0, b.P0)
        assert np.array_equal(a.T0, b.T0)
