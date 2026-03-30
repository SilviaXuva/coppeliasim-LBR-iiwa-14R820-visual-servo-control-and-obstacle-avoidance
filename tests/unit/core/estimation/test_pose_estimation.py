from __future__ import annotations

import numpy as np

from manipulator_framework.core.perception import normalize_marker_detection
from manipulator_framework.core.estimation import MarkerPoseEstimator
from manipulator_framework.core.types import Detection2D, MarkerDetection, Pose3D


def test_marker_pose_estimator_uses_pose_hint() -> None:
    detection_2d = Detection2D(
        bbox_xyxy=(0.0, 0.0, 10.0, 10.0),
        confidence=0.9,
        class_id=10,
        class_name="marker",
        image_size_wh=(640, 480),
        timestamp=1.0,
    )

    marker_detection = MarkerDetection(
        marker_id=10,
        detection=detection_2d,
        pose_camera_frame=Pose3D(
            position=np.array([0.1, 0.2, 0.3]),
            orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
            frame_id="camera",
            child_frame_id="marker_10",
            timestamp=1.0,
        ),
        timestamp=1.0,
    )

    observation = normalize_marker_detection(marker_detection)
    estimator = MarkerPoseEstimator()
    estimate = estimator.estimate(observation)

    assert estimate is not None
    assert estimate.pose.position.shape == (3,)
    assert estimate.confidence == 0.9
