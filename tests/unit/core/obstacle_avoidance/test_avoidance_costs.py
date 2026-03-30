from __future__ import annotations

import numpy as np

from manipulator_framework.core.obstacle_avoidance import compute_clearance_cost
from manipulator_framework.core.types import ObstacleState, Pose3D


def test_clearance_cost_is_positive_when_obstacle_is_close() -> None:
    ee_pose = Pose3D(
        position=np.array([0.5, 0.0, 0.7]),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
    )

    obstacle = ObstacleState(
        obstacle_id="obs_001",
        pose=Pose3D(
            position=np.array([0.55, 0.0, 0.7]),
            orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
        ),
        radius=0.1,
        confidence=1.0,
        timestamp=0.0,
    )

    cost = compute_clearance_cost(ee_pose, [obstacle], safe_distance=0.4)
    assert cost > 0.0
