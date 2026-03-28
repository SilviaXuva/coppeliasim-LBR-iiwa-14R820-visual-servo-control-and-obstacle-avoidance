from __future__ import annotations

import numpy as np

from manipulator_framework.core.metrics import compute_final_visual_position_error
from manipulator_framework.core.types import Pose3D


def make_pose(x: float, y: float, z: float) -> Pose3D:
    return Pose3D(
        position=np.array([x, y, z], dtype=float),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0], dtype=float),
        frame_id="world",
        child_frame_id="target",
        timestamp=0.0,
    )


def test_compute_final_visual_position_error_returns_expected_norm() -> None:
    current = make_pose(1.0, 0.0, 0.0)
    desired = make_pose(0.0, 0.0, 0.0)

    metric = compute_final_visual_position_error(current, desired)

    assert metric.name == "final_visual_position_error"
    assert metric.unit == "m"
    assert np.isclose(metric.value, 1.0)
