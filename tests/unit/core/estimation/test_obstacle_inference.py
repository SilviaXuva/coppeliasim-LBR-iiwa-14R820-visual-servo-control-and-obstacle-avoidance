from __future__ import annotations

import numpy as np

from manipulator_framework.core.estimation import PersonAsObstacleInference
from manipulator_framework.core.types import Pose3D, TargetType, TrackedTarget, TrackingStatus


def test_person_target_with_pose_can_become_obstacle() -> None:
    target = TrackedTarget(
        target_id="person_001",
        target_type=TargetType.PERSON,
        status=TrackingStatus.TRACKED,
        estimated_pose=Pose3D(
            position=np.array([1.0, 0.0, 0.0]),
            orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
            frame_id="world",
            child_frame_id="person_001",
            timestamp=0.0,
        ),
        confidence=0.8,
        timestamp=0.0,
    )

    inference = PersonAsObstacleInference(default_radius=0.4)
    obstacle = inference.infer(target)

    assert obstacle is not None
    assert obstacle.radius == 0.4
    assert obstacle.pose.frame_id == "world"
