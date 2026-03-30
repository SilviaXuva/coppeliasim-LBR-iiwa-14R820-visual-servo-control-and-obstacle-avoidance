from __future__ import annotations

import tomllib
from pathlib import Path


def test_pyproject_declares_required_runtime_dependencies() -> None:
    pyproject_path = Path("pyproject.toml")
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    dependencies = data["project"]["dependencies"]
    optional = data["project"]["optional-dependencies"]

    assert any(dep.startswith("numpy") for dep in dependencies)
    assert any(dep.startswith("PyYAML") for dep in dependencies)

    assert any(dep.startswith("roboticstoolbox-python") for dep in optional["robotics"])
    assert any(dep.startswith("spatialmath-python") for dep in optional["robotics"])

    assert any(dep.startswith("opencv-contrib-python") for dep in optional["vision"])
    assert any(dep.startswith("ultralytics") for dep in optional["yolo"])

    assert "dev" in optional
    assert "test" in optional
    assert "full" in optional
