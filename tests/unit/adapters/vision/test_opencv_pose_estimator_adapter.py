from __future__ import annotations

import numpy as np

from manipulator_framework.adapters.vision.aruco.opencv_pose_estimator_adapter import (
    OpenCVPoseEstimatorAdapter,
)
from manipulator_framework.core.types import Detection2D, MarkerDetection


class FakeCV2:
    SOLVEPNP_IPPE_SQUARE = 7

    @staticmethod
    def solvePnP(object_points, image_points, camera_matrix, distortion_coeffs, flags):
        rvec = np.array([[0.0], [0.0], [0.0]], dtype=float)
        tvec = np.array([[0.1], [0.2], [0.3]], dtype=float)
        return True, rvec, tvec

    @staticmethod
    def Rodrigues(rvec):
        return np.eye(3, dtype=float), None


def test_pose_estimator_adapter_returns_pose3d() -> None:
    adapter = OpenCVPoseEstimatorAdapter(
        camera_matrix=np.eye(3, dtype=float),
        distortion_coeffs=np.zeros((5,), dtype=float),
        marker_length_m=0.05,
        cv2_module=FakeCV2(),
    )

    observation = MarkerDetection(
        marker_id=12,
        detection=Detection2D(
            bbox_xyxy=(10.0, 20.0, 30.0, 40.0),
            confidence=1.0,
            class_id=12,
            class_name="aruco_marker",
            image_size_wh=(80, 60),
            timestamp=2.0,
        ),
        corners_uv=(
            (10.0, 20.0),
            (30.0, 20.0),
            (30.0, 40.0),
            (10.0, 40.0),
        ),
        dictionary_name="DICT_4X4_50",
        timestamp=2.0,
    )

    pose = adapter.estimate_pose(observation)

    assert np.allclose(pose.position, [0.1, 0.2, 0.3])
    assert np.allclose(pose.orientation_quat_xyzw, [0.0, 0.0, 0.0, 1.0])
    assert pose.frame_id == "camera"
    assert pose.child_frame_id == "marker_12"
    assert pose.timestamp == 2.0
