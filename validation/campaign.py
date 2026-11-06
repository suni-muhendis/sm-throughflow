"""Immutable campaign directories with source, data and runtime provenance."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import zipfile

from sm_throughflow.provenance import digest, runtime_identity
from sm_throughflow.simulator import SlcAungierSimulator

ROOT = Path(__file__).resolve().parents[1]


def write_json_new(path, value):
    """Exclusive creation: a previous result is never overwritten."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Serialize before opening, so a serialization error cannot leave a partial file.
    text = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)


def create_campaign(path=None, *, purpose, selection):
    if path is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        path = ROOT / "validation" / "campaigns" / (stamp + "_" + SlcAungierSimulator.VERSION)
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT / "validation" / "campaigns"):
        raise ValueError("campaign output must be below this repository's validation/campaigns")
    # Exclude generated artifacts from the identity/archive, including prior campaigns.
    sources = []
    for folder in ("src", "tests", "scripts", "docs", "validation", ".github"):
        for p in (ROOT / folder).rglob("*"):
            if p.is_file() and not any(x in p.relative_to(ROOT).parts for x in ("campaigns", "__pycache__", "results")):
                sources.append(p)
    sources += [ROOT / name for name in ("pyproject.toml", "constraints-validation.txt", "conftest.py", "AGENTS.md")
                if (ROOT / name).exists()]
    contents = {p.relative_to(ROOT).as_posix(): p.read_bytes() for p in sorted(sources)}
    files = {name: hashlib.sha256(data).hexdigest() for name, data in contents.items()}
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
    patch = subprocess.check_output(["git", "diff", "--binary", "HEAD"], cwd=ROOT)
    manifest = dict(format_version=1, purpose=purpose, selection=selection,
                    simulator_version=SlcAungierSimulator.VERSION, mixing_model=SlcAungierSimulator.mixing_model,
                    runtime=runtime_identity(), git_commit=commit, dirty_patch_sha256=hashlib.sha256(patch).hexdigest(),
                    files=files, source_and_data_sha256=digest(files))
    path.mkdir(parents=True, exist_ok=False)
    (path / "working_tree.patch").write_bytes(patch)
    with zipfile.ZipFile(path / "source.zip", "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in contents.items():
            archive.writestr(name, data)
    manifest["archive_sha256"] = hashlib.sha256((path / "source.zip").read_bytes()).hexdigest()
    write_json_new(path / "manifest.json", manifest)
    return path
