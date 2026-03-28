from __future__ import annotations

import numpy as np

from manipulator_framework.core.perception import normalize_marker_detection
from manipulator_framework.core.estimation import MarkerPoseEstimator
from manipulator_framework.core.types import Detection2D, MarkerDetection, Pose3D


def main() -> None:
    detection_2d = Detection2D(
        bbox_xyxy=(100.0, 120.0, 180.0, 200.0),
        confidence=0.95,
        class_id=23,
        class_name="aruco_marker",
        image_size_wh=(640, 480),
        timestamp=1.0,
    )

    marker_detection = MarkerDetection(
        marker_id=23,
        detection=detection_2d,
        pose_camera_frame=Pose3D(
            position=np.array([0.10, -0.05, 0.85]),
            orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
            frame_id="camera_front",
            child_frame_id="aruco_23",
            timestamp=1.0,
        ),
        corners_uv=((100.0, 120.0), (180.0, 120.0), (180.0, 200.0), (100.0, 200.0)),
        dictionary_name="DICT_4X4_50",
        timestamp=1.0,
    )

    observation = normalize_marker_detection(marker_detection)
    estimator = MarkerPoseEstimator()
    estimate = estimator.estimate(observation)

    print(observation)
    print(estimate)
    if estimate is not None:
        print(estimate.pose.to_dict())


if __name__ == "__main__":
    main()
