from __future__ import annotations

import numpy as np

from manipulator_framework.core.kinematics.pose_conversions import (
    matrix_to_pose3d,
    pose3d_to_matrix,
    transform_to_matrix,
)
from manipulator_framework.core.types import Pose3D


def test_pose3d_to_matrix_and_back_is_consistent() -> None:
    pose = Pose3D(
        position=np.array([0.4, -0.2, 0.8], dtype=float),
        orientation_quat_xyzw=np.array([0.0, 0.0, np.sqrt(0.5), np.sqrt(0.5)], dtype=float),
        frame_id="world",
        child_frame_id="tool0",
        timestamp=1.5,
    )

    matrix = pose3d_to_matrix(pose)
    recovered = matrix_to_pose3d(matrix, frame_id=pose.frame_id, child_frame_id=pose.child_frame_id, timestamp=pose.timestamp)

    assert np.allclose(recovered.position, pose.position, atol=1e-9)
    assert np.allclose(recovered.orientation_quat_xyzw, pose.orientation_quat_xyzw, atol=1e-9)
    assert recovered.frame_id == pose.frame_id
    assert recovered.child_frame_id == pose.child_frame_id


def test_transform_to_matrix_supports_object_with_A_attribute() -> None:
    class _Transform:
        def __init__(self) -> None:
            self.A = np.eye(4, dtype=float)

    matrix = transform_to_matrix(_Transform())
    assert matrix.shape == (4, 4)
    assert np.allclose(matrix, np.eye(4))

