from __future__ import annotations

import numpy as np

from manipulator_framework.core.types import Pose3D


def _normalize_quaternion_xyzw(q: np.ndarray) -> np.ndarray:
    quat = np.asarray(q, dtype=float).reshape(4)
    norm = float(np.linalg.norm(quat))
    if norm <= 0.0:
        return np.array([0.0, 0.0, 0.0, 1.0], dtype=float)
    return quat / norm


def _matrix_to_quaternion_xyzw(rotation: np.ndarray) -> np.ndarray:
    r = np.asarray(rotation, dtype=float)
    if r.shape != (3, 3):
        raise ValueError("Rotation matrix must have shape (3, 3).")

    trace = float(np.trace(r))
    if trace > 0.0:
        s = np.sqrt(trace + 1.0) * 2.0
        qw = 0.25 * s
        qx = (r[2, 1] - r[1, 2]) / s
        qy = (r[0, 2] - r[2, 0]) / s
        qz = (r[1, 0] - r[0, 1]) / s
    elif r[0, 0] > r[1, 1] and r[0, 0] > r[2, 2]:
        s = np.sqrt(1.0 + r[0, 0] - r[1, 1] - r[2, 2]) * 2.0
        qw = (r[2, 1] - r[1, 2]) / s
        qx = 0.25 * s
        qy = (r[0, 1] + r[1, 0]) / s
        qz = (r[0, 2] + r[2, 0]) / s
    elif r[1, 1] > r[2, 2]:
        s = np.sqrt(1.0 + r[1, 1] - r[0, 0] - r[2, 2]) * 2.0
        qw = (r[0, 2] - r[2, 0]) / s
        qx = (r[0, 1] + r[1, 0]) / s
        qy = 0.25 * s
        qz = (r[1, 2] + r[2, 1]) / s
    else:
        s = np.sqrt(1.0 + r[2, 2] - r[0, 0] - r[1, 1]) * 2.0
        qw = (r[1, 0] - r[0, 1]) / s
        qx = (r[0, 2] + r[2, 0]) / s
        qy = (r[1, 2] + r[2, 1]) / s
        qz = 0.25 * s

    return _normalize_quaternion_xyzw(np.array([qx, qy, qz, qw], dtype=float))


def _quaternion_xyzw_to_matrix(q_xyzw: np.ndarray) -> np.ndarray:
    qx, qy, qz, qw = _normalize_quaternion_xyzw(q_xyzw)

    xx = qx * qx
    yy = qy * qy
    zz = qz * qz
    xy = qx * qy
    xz = qx * qz
    yz = qy * qz
    wx = qw * qx
    wy = qw * qy
    wz = qw * qz

    return np.array(
        [
            [1.0 - 2.0 * (yy + zz), 2.0 * (xy - wz), 2.0 * (xz + wy)],
            [2.0 * (xy + wz), 1.0 - 2.0 * (xx + zz), 2.0 * (yz - wx)],
            [2.0 * (xz - wy), 2.0 * (yz + wx), 1.0 - 2.0 * (xx + yy)],
        ],
        dtype=float,
    )


def transform_to_matrix(transform: object | np.ndarray) -> np.ndarray:
    """
    Convert any homogeneous transform-like object into a (4, 4) numpy matrix.

    Supported inputs:
    - numpy array with shape (4, 4)
    - objects exposing matrix in `.A` (e.g., robotics backends)
    """
    if isinstance(transform, np.ndarray):
        matrix = np.asarray(transform, dtype=float)
    elif hasattr(transform, "A"):
        matrix = np.asarray(getattr(transform, "A"), dtype=float)
    else:
        raise TypeError("Unsupported transform type. Expected np.ndarray or object with attribute 'A'.")

    if matrix.shape != (4, 4):
        raise ValueError("Homogeneous transform must have shape (4, 4).")
    return matrix


def matrix_to_pose3d(matrix: np.ndarray, frame_id: str, child_frame_id: str, timestamp: float = 0.0) -> Pose3D:
    mat = transform_to_matrix(matrix)
    translation = mat[:3, 3]
    quaternion_xyzw = _matrix_to_quaternion_xyzw(mat[:3, :3])
    return Pose3D(
        position=translation,
        orientation_quat_xyzw=quaternion_xyzw,
        frame_id=frame_id,
        child_frame_id=child_frame_id,
        timestamp=timestamp,
    )


def pose3d_to_matrix(pose: Pose3D) -> np.ndarray:
    rotation = _quaternion_xyzw_to_matrix(pose.orientation_quat_xyzw)
    transform = np.eye(4, dtype=float)
    transform[:3, :3] = rotation
    transform[:3, 3] = np.asarray(pose.position, dtype=float).reshape(3)
    return transform


def se3_to_pose3d(transform: object | np.ndarray, frame_id: str, child_frame_id: str, timestamp: float = 0.0) -> Pose3D:
    """
    Backward-compatible transform converter into Pose3D.

    Despite the historical name, this function no longer depends on SE3 types.
    """
    return matrix_to_pose3d(
        matrix=transform_to_matrix(transform),
        frame_id=frame_id,
        child_frame_id=child_frame_id,
        timestamp=timestamp,
    )


def matrix_to_se3(matrix: np.ndarray) -> np.ndarray:
    """
    Backward-compatible alias returning a validated homogeneous matrix.
    """
    return transform_to_matrix(matrix)
