from __future__ import annotations

import numpy as np

from manipulator_framework.core.types import (
    Detection2D,
    ExperimentResult,
    ObstacleState,
    Pose3D,
    TargetType,
    TrackedTarget,
    TrackingStatus,
    Twist,
)


def main() -> None:
    detection = Detection2D(
        bbox_xyxy=(50.0, 70.0, 180.0, 320.0),
        confidence=0.88,
        class_id=0,
        class_name="person",
        image_size_wh=(640, 480),
        timestamp=3.0,
    )

    tracked = TrackedTarget(
        target_id="person_001",
        target_type=TargetType.PERSON,
        status=TrackingStatus.TRACKED,
        latest_detection=detection,
        estimated_pose=Pose3D(
            position=np.array([0.6, -0.3, 0.0]),
            orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
            frame_id="world",
            child_frame_id="person_001",
            timestamp=3.0,
        ),
        estimated_twist=Twist(
            linear=np.array([0.02, 0.00, 0.00]),
            angular=np.array([0.0, 0.0, 0.1]),
            frame_id="world",
            timestamp=3.0,
        ),
        confidence=0.88,
        age_steps=12,
        missed_steps=0,
        timestamp=3.0,
    )

    obstacle = ObstacleState(
        obstacle_id="dynamic_obstacle_1",
        pose=tracked.estimated_pose,
        velocity=tracked.estimated_twist,
        radius=0.35,
        source="person_tracker",
        confidence=0.88,
        timestamp=3.0,
    )

    result = ExperimentResult(
        experiment_name="pbvs_with_person_avoidance",
        run_id="run_0001",
        success=True,
        metrics={
            "tracking_success_rate": 0.95,
            "minimum_clearance_m": 0.42,
            "final_pose_error_m": 0.03,
        },
        artifacts={
            "metrics_csv": "experiments/runs/run_0001/metrics.csv",
            "summary_json": "experiments/runs/run_0001/summary.json",
        },
        metadata={
            "scenario": "person_in_workspace",
            "backend": "simulation",
        },
        started_at=0.0,
        finished_at=12.5,
    )

    print(tracked.to_dict())
    print(obstacle.to_dict())
    print("Experiment duration:", result.duration)


if __name__ == "__main__":
    main()
