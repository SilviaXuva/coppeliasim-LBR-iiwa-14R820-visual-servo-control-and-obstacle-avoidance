from __future__ import annotations

import numpy as np

from manipulator_framework.core.types import ObstacleState, Pose3D


def compute_clearance_cost(
    end_effector_pose: Pose3D,
    obstacles: list[ObstacleState],
    safe_distance: float,
) -> float:
    ee = np.asarray(end_effector_pose.position, dtype=float)

    if not obstacles:
        return 0.0

    penalties: list[float] = []
    for obstacle in obstacles:
        obs = np.asarray(obstacle.pose.position, dtype=float)
        radius = 0.0 if obstacle.radius is None else float(obstacle.radius)
        distance = float(np.linalg.norm(ee - obs)) - radius

        if distance >= safe_distance:
            penalties.append(0.0)
        else:
            penalties.append((safe_distance - distance) ** 2)

    return float(sum(penalties))
