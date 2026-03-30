from __future__ import annotations

import numpy as np

from manipulator_framework.core.metrics import (
    compute_joint_error,
    compute_success_from_visual_error,
    compute_visual_servo_error,
)
from manipulator_framework.core.types import JointState, Pose3D


def test_compute_visual_servo_error_returns_l2_distance_between_target_and_ee() -> None:
    metric = compute_visual_servo_error(
        target_pose=Pose3D(position=np.array([1.0, 2.0, 3.0])),
        ee_pose=Pose3D(position=np.array([1.0, 2.0, 1.0])),
    )
    assert metric.name == "visual_error"
    assert metric.unit == "m"
    assert np.isclose(metric.value, 2.0)


def test_compute_joint_error_returns_l2_norm_of_joint_difference() -> None:
    metric = compute_joint_error(
        q_desired=JointState(positions=np.array([1.0, 2.0, 3.0])),
        q_actual=JointState(positions=np.array([1.0, 1.0, 1.0])),
    )
    assert metric.name == "joint_error"
    assert metric.unit == "rad"
    assert np.isclose(metric.value, np.sqrt(5.0))


def test_compute_success_from_visual_error_uses_threshold() -> None:
    ok_metric = compute_success_from_visual_error(visual_error=0.01, threshold=0.02)
    fail_metric = compute_success_from_visual_error(visual_error=0.05, threshold=0.02)

    assert ok_metric.name == "success"
    assert ok_metric.unit == "ratio"
    assert ok_metric.value == 1.0
    assert fail_metric.value == 0.0
