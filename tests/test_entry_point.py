"""The package is found through sm-core and stamps its versions on results."""
import contextlib
import io
import sys

import pytest

from sm_core import list_environments, make_env
from sm_throughflow.env import TurbomachineryThroughflowEnv
from sm_throughflow.score import ExperimentalThroughflowScore
from sm_throughflow.simulator import NasaTurboDesignSimulator
from scripts.run_throughflow import build_case


def test_sm_core_finds_the_throughflow_environment():
    # Read from the installed distribution metadata: this fails if the
    # package was not (re)installed after pyproject.toml changed.
    assert "turbomachinery_throughflow" in list_environments()
    env = make_env("turbomachinery_throughflow")
    assert isinstance(env, TurbomachineryThroughflowEnv)
    assert env.name == "turbomachinery_throughflow"


def test_building_the_environment_does_not_import_the_backend():
    make_env("turbomachinery_throughflow")
    if "turbodesign" in sys.modules:
        pytest.skip("another test already imported turbodesign")
    assert "cantera" not in sys.modules


def test_the_task_accepts_only_the_current_simulator_version():
    from sm_throughflow import ThroughflowTaskV1
    assert ThroughflowTaskV1.model_fields["simulator_version"].default == NasaTurboDesignSimulator.VERSION


@pytest.mark.parametrize("stage", ["success", "schema_error"])
def test_every_result_is_stamped_whatever_stage_it_stopped_at(stage):
    design, task = build_case(1, streamtubes=2)
    if stage == "schema_error":
        design = {"machine_type": "turbine"}
    with contextlib.redirect_stdout(io.StringIO()):
        result = make_env("turbomachinery_throughflow").evaluate("t", task, "d", design)
    assert result.status == stage
    assert result.environment == "turbomachinery_throughflow"
    assert result.simulator_version == NasaTurboDesignSimulator.VERSION
    assert result.score_version == ExperimentalThroughflowScore.VERSION
    assert result.score.normalized_total == 0.0
