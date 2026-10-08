"""Install the built wheel into a clean venv and solve a reference compressor there.

The wheel's sm-core dependency resolves from its pinned git tag, so this also
checks that the published pieces work together.

Usage: python scripts/check_wheel.py dist
"""
import json
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.run_throughflow import build_case  # noqa: E402
from sm_throughflow.simulator import SlcAungierSimulator  # noqa: E402

SMOKE = """
import json, sys
from pathlib import Path
import sm_throughflow
from sm_core import make_env, list_environments
assert Path(sm_throughflow.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
assert "turbomachinery_throughflow" in list_environments(), list_environments()
payload = json.loads(sys.stdin.read())
result = make_env("turbomachinery_throughflow").evaluate("wheel-smoke", payload["task"], "one-stage", payload["design"])
assert result.status == "success", result
assert (result.environment, result.simulator_version) == ("turbomachinery_throughflow", payload["simulator_version"]), result
print("sm_throughflow", sm_throughflow.__version__, "pressure ratio", result.metrics["pressure_ratio_total"])
"""


def main() -> None:
    wheels = sorted(Path(sys.argv[1]).glob("sm_throughflow-*.whl"))
    if len(wheels) != 1:
        raise SystemExit("expected exactly one sm_throughflow wheel, found {}".format(wheels))
    design, task = build_case(1)
    payload = json.dumps({"design": design, "task": task, "simulator_version": SlcAungierSimulator.VERSION})
    with tempfile.TemporaryDirectory(prefix="sm-tf-wheel-") as temp:
        env_dir = Path(temp) / "venv"
        venv.EnvBuilder(with_pip=True).create(env_dir)
        python = env_dir / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        subprocess.run([str(python), "-m", "pip", "install", "-q", str(wheels[0].resolve())], check=True)
        subprocess.run([str(python), "-c", SMOKE], input=payload, text=True, check=True, cwd=temp)


if __name__ == "__main__":
    main()
