from __future__ import annotations

import numpy as np

from manipulator_framework.core.obstacle_avoidance import CuckooSearchAvoidance, TrajectoryReferenceAdapter
from manipulator_framework.core.visual_servoing import PBVSAvoidanceComposer, PBVSController, PBVSReferenceGenerator
from manipulator_framework.core.types import JointState, ObstacleState, Pose3D, RobotState


def main() -> None:
    robot_state = RobotState(
        joint_state=JointState(
            positions=np.zeros(7),
            velocities=np.zeros(7),
            joint_names=tuple(f"joint_{i+1}" for i in range(7)),
            timestamp=0.0,
        ),
        end_effector_pose=Pose3D(
            position=np.array([0.45, 0.0, 0.75]),
            orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
            frame_id="world",
            child_frame_id="tool0",
            timestamp=0.0,
        ),
        timestamp=0.0,
    )

    current_target_pose = Pose3D(
        position=np.array([0.7, -0.1, 0.8]),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
        frame_id="world",
        child_frame_id="target",
        timestamp=0.0,
    )

    desired_target_pose = Pose3D(
        position=np.array([0.5, 0.0, 0.7]),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
        frame_id="world",
        child_frame_id="target_desired",
        timestamp=0.0,
    )

    obstacles = [
        ObstacleState(
            obstacle_id="obs_001",
            pose=Pose3D(
                position=np.array([0.5, 0.02, 0.72]),
                orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
                frame_id="world",
                child_frame_id="obs_001",
                timestamp=0.0,
            ),
            radius=0.2,
            source="synthetic",
            confidence=1.0,
            timestamp=0.0,
        )
    ]

    composer = PBVSAvoidanceComposer(
        pbvs_controller=PBVSController(reference_generator=PBVSReferenceGenerator(gain=0.7)),
        avoidance=CuckooSearchAvoidance(safe_distance=0.4, candidate_scale=0.03),
        trajectory_adapter=TrajectoryReferenceAdapter(),
    )

    visual_error, trajectory = composer.compute_reference(
        robot_state=robot_state,
        current_target_pose=current_target_pose,
        desired_target_pose=desired_target_pose,
        obstacles=obstacles,
        dt=0.1,
    )

    print("Visual error norm:", visual_error.norm)
    print("Final trajectory:", trajectory.to_dict())


if __name__ == "__main__":
    main()
