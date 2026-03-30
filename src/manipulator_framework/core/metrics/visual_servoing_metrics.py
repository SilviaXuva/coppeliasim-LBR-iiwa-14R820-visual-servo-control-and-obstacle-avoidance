from __future__ import annotations

import numpy as np

from manipulator_framework.core.types.metrics import ScalarMetric
from manipulator_framework.core.types import Pose3D


def compute_final_visual_position_error(
    current_pose: Pose3D,
    desired_pose: Pose3D,
) -> ScalarMetric:
    error = np.asarray(desired_pose.position, dtype=float) - np.asarray(current_pose.position, dtype=float)
    return ScalarMetric(
        name="final_visual_position_error",
        value=float(np.linalg.norm(error)),
        unit="m",
        description="Final Euclidean position error in visual servoing.",
    )
