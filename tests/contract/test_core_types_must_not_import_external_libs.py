from __future__ import annotations

from pathlib import Path


FORBIDDEN_IMPORT_SNIPPETS = (
    "import cv2",
    "from cv2",
    "import roboticstoolbox",
    "from roboticstoolbox",
    "import spatialmath",
    "from spatialmath",
)


def test_core_types_has_no_external_robotics_or_vision_imports() -> None:
    core_types_path = Path("src/manipulator_framework/core/types")

    for py_file in core_types_path.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_IMPORT_SNIPPETS:
            assert forbidden not in content, f"{py_file} contains forbidden import: {forbidden}"

