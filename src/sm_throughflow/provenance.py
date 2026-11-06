"""Deterministic identities of the code, dependencies, and effective inputs."""
import hashlib
import json
import platform
import sys
from importlib.metadata import version
from pathlib import Path


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _source_files():
    root = Path(__file__).parent
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*.py"))}


_SOURCE_AT_IMPORT = _source_files()


def runtime_identity():
    files = _source_files()
    if files != _SOURCE_AT_IMPORT:
        raise RuntimeError("package source changed after import; start a fresh process before evaluating")
    return dict(source_sha256=digest(files), source_files=files, python=sys.version,
                platform=platform.platform(), dependencies={name: version(name) for name in
                ("sm-throughflow", "sm-core", "numpy", "scipy", "pydantic")})


def evaluation_identity(design, task, profile, mixing_model):
    effective = dict(design=design.model_dump(mode="json"), task=task.model_dump(mode="json"),
                     physics_profile=profile, mixing_model=mixing_model)
    return dict(runtime=runtime_identity(), effective_inputs=effective, input_sha256=digest(effective))
