from __future__ import annotations

import numpy as np

from manipulator_framework.core.types import (
    CameraFrame,
    Detection2D,
    MarkerDetection,
    PersonDetection,
    Pose3D,
)


def main() -> None:
    image = np.zeros((480, 640, 3), dtype=np.uint8)

    frame = CameraFrame(
        image=image,
        camera_id="sim_camera_front",
        frame_id="camera_front",
        timestamp=2.0,
        intrinsics=np.array(
            [
                [600.0, 0.0, 320.0],
                [0.0, 600.0, 240.0],
                [0.0, 0.0, 1.0],
            ]
        ),
    )

    bbox = Detection2D(
        bbox_xyxy=(120.0, 80.0, 240.0, 300.0),
        confidence=0.92,
        class_id=0,
        class_name="person",
        image_size_wh=(640, 480),
        timestamp=2.0,
    )

    marker_pose = Pose3D(
        position=np.array([0.1, -0.2, 0.8]),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
        frame_id="camera_front",
        child_frame_id="aruco_23",
        timestamp=2.0,
    )

    marker_detection = MarkerDetection(
        marker_id=23,
        detection=bbox,
        pose_camera_frame=marker_pose,
        corners_uv=((100.0, 100.0), (140.0, 100.0), (140.0, 140.0), (100.0, 140.0)),
        dictionary_name="DICT_4X4_50",
        timestamp=2.0,
    )

    person_detection = PersonDetection(
        detection=bbox,
        keypoints_uv=((150.0, 100.0), (155.0, 130.0), (145.0, 130.0)),
        person_id_hint="candidate_1",
        timestamp=2.0,
    )

    print("Frame shape:", frame.image.shape)
    print(marker_detection.to_dict())
    print(person_detection.to_dict())


if __name__ == "__main__":
    main()
