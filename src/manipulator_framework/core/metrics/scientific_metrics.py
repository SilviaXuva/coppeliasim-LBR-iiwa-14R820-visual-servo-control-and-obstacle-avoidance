from __future__ import annotations

import numpy as np

from manipulator_framework.core.types import JointState, Pose3D
from manipulator_framework.core.types.metrics import ScalarMetric


def compute_visual_servo_error(
    *,
    target_pose: Pose3D,
    ee_pose: Pose3D,
) -> ScalarMetric:
    delta = np.asarray(target_pose.position, dtype=float) - np.asarray(ee_pose.position, dtype=float)
    return ScalarMetric(
        name="visual_error",
        value=float(np.linalg.norm(delta)),
        unit="m",
        description="Euclidean norm of target pose minus end-effector pose.",
    )


def compute_joint_error(
    *,
    q_desired: JointState,
    q_actual: JointState,
) -> ScalarMetric:
    delta = np.asarray(q_desired.positions, dtype=float) - np.asarray(q_actual.positions, dtype=float)
    return ScalarMetric(
        name="joint_error",
        value=float(np.linalg.norm(delta)),
        unit="rad",
        description="Euclidean norm of desired minus actual joint positions.",
    )


def compute_success_from_visual_error(
    *,
    visual_error: float,
    threshold: float,
) -> ScalarMetric:
    if threshold <= 0.0:
        raise ValueError("threshold must be greater than zero.")

    return ScalarMetric(
        name="success",
        value=1.0 if float(visual_error) < float(threshold) else 0.0,
        unit="ratio",
        description="Success flag derived from visual_error < threshold.",
    )
