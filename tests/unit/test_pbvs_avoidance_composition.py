from __future__ import annotations

import numpy as np

from manipulator_framework.core.obstacle_avoidance import CuckooSearchAvoidance, TrajectoryReferenceAdapter
from manipulator_framework.core.visual_servoing import PBVSAvoidanceComposer, PBVSController, PBVSReferenceGenerator
from manipulator_framework.core.types import JointState, ObstacleState, Pose3D, RobotState


def test_pbvs_avoidance_composer_generates_final_reference() -> None:
    composer = PBVSAvoidanceComposer(
        pbvs_controller=PBVSController(reference_generator=PBVSReferenceGenerator(gain=0.5)),
        avoidance=CuckooSearchAvoidance(),
        trajectory_adapter=TrajectoryReferenceAdapter(),
    )

    robot_state = RobotState(
        joint_state=JointState(
            positions=np.zeros(7),
            velocities=np.zeros(7),
            joint_names=tuple(f"joint_{i+1}" for i in range(7)),
            timestamp=0.0,
        ),
        end_effector_pose=Pose3D(
            position=np.array([0.5, 0.0, 0.7]),
            orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
        ),
        timestamp=0.0,
    )

    current_target_pose = Pose3D(
        position=np.array([0.6, 0.0, 0.7]),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
    )
    desired_target_pose = Pose3D(
        position=np.array([0.45, 0.0, 0.7]),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
    )

    obstacles = [
        ObstacleState(
            obstacle_id="obs_001",
            pose=Pose3D(
                position=np.array([0.52, 0.0, 0.7]),
                orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
            ),
            radius=0.1,
            confidence=1.0,
            timestamp=0.0,
        )
    ]

    visual_error, trajectory = composer.compute_reference(
        robot_state=robot_state,
        current_target_pose=current_target_pose,
        desired_target_pose=desired_target_pose,
        obstacles=obstacles,
        dt=0.1,
    )

    assert visual_error.norm > 0.0
    assert len(trajectory.samples) == 2
