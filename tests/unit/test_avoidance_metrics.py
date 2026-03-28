from __future__ import annotations

import numpy as np

from manipulator_framework.core.metrics import compute_minimum_clearance
from manipulator_framework.core.types import ObstacleState, Pose3D


def make_pose(x: float, y: float, z: float) -> Pose3D:
    return Pose3D(
        position=np.array([x, y, z], dtype=float),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0], dtype=float),
        frame_id="world",
        child_frame_id="tool0",
        timestamp=0.0,
    )


def test_compute_minimum_clearance_returns_smallest_clearance() -> None:
    ee_poses = [
        make_pose(0.0, 0.0, 0.0),
        make_pose(1.0, 0.0, 0.0),
    ]

    obstacle = ObstacleState(
        obstacle_id="obs_001",
        pose=make_pose(0.5, 0.0, 0.0),
        radius=0.1,
        source="synthetic",
        confidence=1.0,
        timestamp=0.0,
    )

    metric = compute_minimum_clearance(ee_poses, [obstacle])

    assert metric.name == "minimum_clearance"
    assert metric.unit == "m"
    assert np.isclose(metric.value, 0.4)
