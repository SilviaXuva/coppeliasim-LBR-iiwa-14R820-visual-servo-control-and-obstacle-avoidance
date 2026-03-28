from __future__ import annotations

import numpy as np

from manipulator_framework.core.estimation import PersonAsObstacleInference
from manipulator_framework.core.types import Detection2D, Pose3D, TargetType, TrackedTarget, TrackingStatus


def main() -> None:
    tracked = TrackedTarget(
        target_id="person_001",
        target_type=TargetType.PERSON,
        status=TrackingStatus.TRACKED,
        latest_detection=Detection2D(
            bbox_xyxy=(120.0, 100.0, 220.0, 300.0),
            confidence=0.9,
            class_id=0,
            class_name="person",
            image_size_wh=(640, 480),
            timestamp=3.0,
        ),
        estimated_pose=Pose3D(
            position=np.array([0.6, -0.2, 0.0]),
            orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
            frame_id="world",
            child_frame_id="person_001",
            timestamp=3.0,
        ),
        estimated_twist=None,
        confidence=0.9,
        age_steps=5,
        missed_steps=0,
        timestamp=3.0,
    )

    inference = PersonAsObstacleInference(default_radius=0.4)
    obstacle = inference.infer(tracked)

    print(tracked.to_dict())
    print(obstacle.to_dict() if obstacle is not None else None)


if __name__ == "__main__":
    main()
