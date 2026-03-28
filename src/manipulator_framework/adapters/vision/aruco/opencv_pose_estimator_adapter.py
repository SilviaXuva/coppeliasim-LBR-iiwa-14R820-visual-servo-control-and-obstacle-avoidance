from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from manipulator_framework.core.contracts import PoseEstimatorInterface
from manipulator_framework.core.types import MarkerDetection, Pose3D


@dataclass
class OpenCVPoseEstimatorAdapter(PoseEstimatorInterface):
    """
    Adapter for pose estimation from marker observations.
    """
    camera_matrix: np.ndarray
    distortion_coeffs: np.ndarray
    marker_length_m: float

    def estimate_pose(self, observation: MarkerDetection) -> Pose3D:
        rvec, tvec = self._estimate_raw_pose(observation)
        quat = self._rvec_to_quaternion(rvec)

        return Pose3D(
            position=np.asarray(tvec, dtype=float).reshape(3),
            orientation_quat_xyzw=np.asarray(quat, dtype=float).reshape(4),
            frame_id="camera",
            child_frame_id=f"marker_{observation.marker_id}",
            timestamp=observation.timestamp,
        )

    def _estimate_raw_pose(self, observation: MarkerDetection) -> tuple[np.ndarray, np.ndarray]:
        raise NotImplementedError("Bind cv2.solvePnP or ArUco pose API here.")

    def _rvec_to_quaternion(self, rvec: np.ndarray) -> np.ndarray:
        raise NotImplementedError("Implement Rodrigues-to-quaternion conversion here.")
