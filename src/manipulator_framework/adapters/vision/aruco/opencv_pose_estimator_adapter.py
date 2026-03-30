from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from manipulator_framework.core.contracts import PoseEstimatorInterface
from manipulator_framework.core.types import MarkerDetection, PersonDetection, Pose3D, TrackedTarget
from manipulator_framework.core.types.enums import TargetType, TrackingStatus


@dataclass
class OpenCVPoseEstimatorAdapter(PoseEstimatorInterface):
    """
    OpenCV-based pose estimation adapter for marker observations.

    This adapter is intentionally specialized for ArUco marker pose estimation.
    Person target estimation is not handled here; the method is implemented only
    to satisfy the shared interface contract.
    """
    camera_matrix: np.ndarray
    distortion_coeffs: np.ndarray
    marker_length_m: float
    cv2_module: Any | None = None

    def estimate_marker_pose(self, detection: MarkerDetection) -> Pose3D | None:
        rvec, tvec = self._estimate_raw_pose(detection)
        quat = self._rvec_to_quaternion(rvec)

        return Pose3D(
            position=np.asarray(tvec, dtype=float).reshape(3),
            orientation_quat_xyzw=np.asarray(quat, dtype=float).reshape(4),
            frame_id="camera",
            child_frame_id=f"marker_{detection.marker_id}",
            timestamp=detection.timestamp,
        )

    def estimate_person_target(self, detection: PersonDetection) -> TrackedTarget | None:
        """
        This adapter does not estimate full person target state from 2D detections.
        Return a minimal tracked target placeholder to keep the contract explicit.
        """
        return TrackedTarget(
            target_id=detection.person_id_hint or "person_unknown",
            target_type=TargetType.PERSON,
            status=TrackingStatus.DETECTED,
            latest_detection=detection.detection,
            estimated_pose=None,
            estimated_twist=None,
            confidence=detection.detection.confidence,
            age_steps=0,
            missed_steps=0,
            timestamp=detection.timestamp,
        )

    def estimate_pose(self, observation: MarkerDetection) -> Pose3D | None:
        """
        Backward-compatible alias for older tests/callers.
        Prefer estimate_marker_pose(...).
        """
        return self.estimate_marker_pose(observation)

    def _estimate_raw_pose(self, observation: MarkerDetection) -> tuple[np.ndarray, np.ndarray]:
        if len(observation.corners_uv) != 4:
            raise ValueError(
                "MarkerDetection must contain exactly 4 corners_uv points for pose estimation."
            )

        cv2 = self._resolve_cv2()

        half = float(self.marker_length_m) / 2.0
        object_points = np.asarray(
            [
                [-half, half, 0.0],
                [half, half, 0.0],
                [half, -half, 0.0],
                [-half, -half, 0.0],
            ],
            dtype=float,
        )
        image_points = np.asarray(observation.corners_uv, dtype=float).reshape(4, 2)

        ok, rvec, tvec = cv2.solvePnP(
            object_points,
            image_points,
            np.asarray(self.camera_matrix, dtype=float),
            np.asarray(self.distortion_coeffs, dtype=float),
            flags=getattr(cv2, "SOLVEPNP_IPPE_SQUARE", 0),
        )
        if not ok:
            raise RuntimeError("OpenCV pose estimation failed for the provided marker observation.")

        return np.asarray(rvec, dtype=float).reshape(3), np.asarray(tvec, dtype=float).reshape(3)

    def _rvec_to_quaternion(self, rvec: np.ndarray) -> np.ndarray:
        cv2 = self._resolve_cv2()
        rotation_matrix, _ = cv2.Rodrigues(np.asarray(rvec, dtype=float).reshape(3, 1))
        return self._rotation_matrix_to_quaternion(np.asarray(rotation_matrix, dtype=float))

    def _rotation_matrix_to_quaternion(self, rotation_matrix: np.ndarray) -> np.ndarray:
        m = rotation_matrix
        trace = float(m[0, 0] + m[1, 1] + m[2, 2])

        if trace > 0.0:
            s = 0.5 / np.sqrt(trace + 1.0)
            w = 0.25 / s
            x = (m[2, 1] - m[1, 2]) * s
            y = (m[0, 2] - m[2, 0]) * s
            z = (m[1, 0] - m[0, 1]) * s
        elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
            s = 2.0 * np.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2])
            w = (m[2, 1] - m[1, 2]) / s
            x = 0.25 * s
            y = (m[0, 1] + m[1, 0]) / s
            z = (m[0, 2] + m[2, 0]) / s
        elif m[1, 1] > m[2, 2]:
            s = 2.0 * np.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2])
            w = (m[0, 2] - m[2, 0]) / s
            x = (m[0, 1] + m[1, 0]) / s
            y = 0.25 * s
            z = (m[1, 2] + m[2, 1]) / s
        else:
            s = 2.0 * np.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1])
            w = (m[1, 0] - m[0, 1]) / s
            x = (m[0, 2] + m[2, 0]) / s
            y = (m[1, 2] + m[2, 1]) / s
            z = 0.25 * s

        quat = np.asarray([x, y, z, w], dtype=float)
        norm = np.linalg.norm(quat)
        if norm == 0.0:
            raise ValueError("Quaternion normalization failed because the norm is zero.")
        return quat / norm

    def _resolve_cv2(self) -> Any:
        if self.cv2_module is not None:
            return self.cv2_module

        try:
            import cv2  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "OpenCV is required for OpenCVPoseEstimatorAdapter."
            ) from exc

        return cv2
