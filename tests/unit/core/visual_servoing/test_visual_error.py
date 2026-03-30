from __future__ import annotations

import numpy as np

from manipulator_framework.core.visual_servoing import compute_pose_error
from manipulator_framework.core.types import Pose3D


def test_compute_pose_error_returns_nonzero_position_error() -> None:
    current = Pose3D(
        position=np.array([1.0, 0.0, 0.0]),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
    )
    desired = Pose3D(
        position=np.array([0.0, 0.0, 0.0]),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
    )

    error = compute_pose_error(current, desired)

    assert np.allclose(error.position_error, np.array([-1.0, 0.0, 0.0]))
    assert np.allclose(error.orientation_error, np.zeros(4))
