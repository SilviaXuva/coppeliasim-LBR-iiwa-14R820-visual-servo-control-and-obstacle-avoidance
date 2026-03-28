from __future__ import annotations

import numpy as np
from spatialmath import SE3
from spatialmath.base import r2q

from manipulator_framework.core.types import Pose3D


def se3_to_pose3d(transform: SE3, frame_id: str, child_frame_id: str, timestamp: float = 0.0) -> Pose3D:
    """
    Convert a SpatialMath SE3 transform into the internal Pose3D type.
    Quaternion convention is XYZW.
    """
    t = np.asarray(transform.t, dtype=float).reshape(3)
    q_wxyz = np.asarray(r2q(transform.R), dtype=float).reshape(4)
    q_xyzw = np.array([q_wxyz[1], q_wxyz[2], q_wxyz[3], q_wxyz[0]], dtype=float)

    return Pose3D(
        position=t,
        orientation_quat_xyzw=q_xyzw,
        frame_id=frame_id,
        child_frame_id=child_frame_id,
        timestamp=timestamp,
    )


def matrix_to_se3(matrix: np.ndarray) -> SE3:
    mat = np.asarray(matrix, dtype=float)
    if mat.shape != (4, 4):
        raise ValueError("Homogeneous transform must have shape (4, 4).")
    return SE3(mat)
