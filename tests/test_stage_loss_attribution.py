import numpy as np
import pytest

from validation.audit_stage_loss_attribution import (
    core_average,
    efficiency_budget,
    maximum_shock_scale_difference,
    shock_scale_curve,
)


def test_rotor_and_downstream_budget_preserve_stage_work_basis():
    values = dict(rotor_pr=1.21, stage_pr=1.1025, rotor_tr=1.12, rotor_eta=.83, stage_eta=.42)
    budget = efficiency_budget(values, .5)
    assert budget["rotor_eta"] == pytest.approx(.10 / .12)
    assert budget["downstream_penalty"] == pytest.approx(.05 / .12)
    assert budget["stage_eta"] == pytest.approx(budget["rotor_eta"] - budget["downstream_penalty"])
    assert budget["reported_stage_eta"] == pytest.approx(budget["stage_eta"] + budget["stage_reporting_residual"])


def test_core_average_excludes_tubes_touching_extrapolated_samples():
    values = np.array([np.nan, 2., 4., 8., np.nan])
    masses = np.array([100., 1., 3., 100.])
    assert core_average(values, masses, np.isfinite(values)) == pytest.approx(5.25)


def test_shock_scale_maximum_checks_clipping_breakpoints_and_saturated_tail():
    head = np.ones(4)
    weights = np.ones(3)
    core = np.array([False, True, True, False])
    lower = shock_scale_curve(np.full(4, .10), np.full(4, .10), head, .5, True, weights, core)
    higher = shock_scale_curve(np.full(4, .05), np.full(4, .30), head, .5, True, weights, core)
    result = maximum_shock_scale_difference(lower, higher)
    assert result == pytest.approx(dict(loss_delta=.25, scale=1.5, zero_scale_delta=-.05))
    assert (lower["means"][-1], higher["means"][-1]) == pytest.approx((.5, .5))
