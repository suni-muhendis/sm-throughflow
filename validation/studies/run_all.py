"""Run selected studies in a new, immutable validation campaign."""
import os
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDIES = ["admission", "numerics", "conservation", "sweeps", "robustness", "search"]

if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(HERE.parent))
    from campaign import create_campaign
    selected = sys.argv[1:] or STUDIES
    if any(name not in STUDIES for name in selected):
        raise ValueError("unknown study; choose from " + ", ".join(STUDIES))
    path = create_campaign(purpose="internal_consistency", selection=selected)
    os.environ["SM_THROUGHFLOW_STUDY_CAMPAIGN"] = str(path)
    print("campaign", path, flush=True)
    for name in selected:
        print("==", name, flush=True)
        runpy.run_path(str(HERE / (name + ".py")), run_name="__main__")

    sys.argv = ["analyze.py", str(path)]
    runpy.run_path(str(HERE / "analyze.py"), run_name="__main__")
