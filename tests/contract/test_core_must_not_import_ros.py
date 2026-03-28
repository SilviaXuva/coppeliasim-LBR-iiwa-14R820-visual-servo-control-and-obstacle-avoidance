from __future__ import annotations

from pathlib import Path


FORBIDDEN_IMPORT_SNIPPETS = (
    "import rclpy",
    "from rclpy",
    "import sensor_msgs",
    "from sensor_msgs",
    "import geometry_msgs",
    "from geometry_msgs",
    "import tf2",
    "from tf2",
)


def test_core_has_no_ros_imports() -> None:
    core_path = Path("src/manipulator_framework/core")

    for py_file in core_path.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_IMPORT_SNIPPETS:
            assert forbidden not in content, f"{py_file} contains forbidden import: {forbidden}"
