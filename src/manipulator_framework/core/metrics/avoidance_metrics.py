from __future__ import annotations

import numpy as np

from manipulator_framework.core.metrics.metric_models import ScalarMetric
from manipulator_framework.core.types import ObstacleState, Pose3D


def compute_minimum_clearance(
    end_effector_poses: list[Pose3D],
    obstacles: list[ObstacleState],
) -> ScalarMetric:
    if not end_effector_poses or not obstacles:
        return ScalarMetric(
            name="minimum_clearance",
            value=float("inf"),
            unit="m",
            description="Minimum clearance between end-effector path and obstacles.",
        )

    min_clearance = float("inf")

    for ee_pose in end_effector_poses:
        ee = np.asarray(ee_pose.position, dtype=float)
        for obstacle in obstacles:
            obs = np.asarray(obstacle.pose.position, dtype=float)
            radius = 0.0 if obstacle.radius is None else float(obstacle.radius)
            clearance = float(np.linalg.norm(ee - obs)) - radius
            min_clearance = min(min_clearance, clearance)

    return ScalarMetric(
        name="minimum_clearance",
        value=min_clearance,
        unit="m",
        description="Minimum clearance between end-effector path and obstacles.",
    )
