import numpy as np
import pytest

from sm_throughflow.correlations.aungier import normal_shock_total_pressure_ratio
from validation.backpressure_passage_reference import PassageDomain, exit_wake, mass_flux, solve
from validation.passage_shock_candidate import area_mach, area_ratio, static_ratio
from validation.probe_backpressure_passage import sample_pressure


def _case(shock_mach, *, capacity=(1.06, 1.11, 1.21, 1.46), displaced=0.):
    x = np.array([0., .25, .55, 1.])
    t0 = np.array([300., 304., 306., 309.])
    p0 = 175000 * (t0 / t0[0])**3.5
    ratio = normal_shock_total_pressure_ratio(shock_mach)
    exit_mach = area_mach(capacity[-1] * ratio)
    back_pressure = float(p0[-1] * ratio * static_ratio(exit_mach))
    area = np.asarray(capacity) / mass_flux(1., t0, p0, 1.4, 287.05)
    return x, area + displaced, t0, dict(mass=1., inlet_total_pressure=p0[0], exit_pressure=back_pressure,
                                         displacement_area=np.full_like(x, displaced))


def test_rotating_temperature_path_matches_mass_backpressure_and_normal_shock_momentum():
    x, area, t0, kwargs = _case(1.4, displaced=.00005)
    solution = solve(x, area, t0, **kwargs)
    assert solution.shock_station == pytest.approx(np.interp(area_ratio(1.4), [1.06, 1.11, 1.21, 1.46], x))
    assert solution.shock_mach_before == pytest.approx(1.4)
    assert solution.relative_mass_error < 1e-12
    assert solution.relative_exit_pressure_error < 1e-12
    assert solution.exit_blockage == pytest.approx(.00005 / area[-1])
    p1, p2 = solution.shock_pressure_before, solution.shock_pressure_after
    m1, m2 = solution.shock_mach_before, solution.shock_mach_after
    assert p1 * (1 + 1.4 * m1**2) == pytest.approx(p2 * (1 + 1.4 * m2**2))
    position = solution.shock_station
    assert sample_pressure(solution, [position - 1e-10, position]) == pytest.approx([p1, p2])


def test_lower_backpressure_moves_shock_downstream_in_diverging_reference():
    upstream, downstream = (solve(*args[:3], **args[3]) for args in (_case(1.35), _case(1.55)))
    assert downstream.pressure[-1] < upstream.pressure[-1]
    assert downstream.shock_station > upstream.shock_station
    assert downstream.shock_total_ratio < upstream.shock_total_ratio


def test_fixed_capacity_and_ambiguous_roots_are_separate_failures():
    x, area, t0, kwargs = _case(1.4, capacity=(1.06, .96, 1.21, 1.46))
    with pytest.raises(PassageDomain, match="insufficient_isentropic_capacity"):
        solve(x, area, t0, **kwargs)
    x, area, t0, kwargs = _case(1.4, capacity=(1.14, 1.08, 1.26, 1.46))
    with pytest.raises(PassageDomain, match="multiple_internal_shocks") as err:
        solve(x, area, t0, **kwargs)
    assert len(err.value.evidence["shock_candidates"]) == 2


def test_wake_preserves_prescribed_mass_defect_and_loses_total_pressure():
    uniform, wake = (exit_wake(.6, 130000., 310., blockage) for blockage in (0., .025))
    assert uniform.pressure == pytest.approx(130000.)
    assert wake.blockage == pytest.approx(.025, abs=1e-13)
    assert wake.total_pressure < wake.mass_average_total_pressure < uniform.total_pressure
    assert wake.mixing_entropy_over_R > 0
