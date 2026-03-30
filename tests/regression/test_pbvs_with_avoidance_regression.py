from __future__ import annotations

import numpy as np

from manipulator_framework.core.metrics import compute_minimum_clearance
from manipulator_framework.core.obstacle_avoidance import CuckooSearchAvoidance, TrajectoryReferenceAdapter
from manipulator_framework.core.types import JointState, ObstacleState, Pose3D, RobotState
from manipulator_framework.core.visual_servoing import PBVSAvoidanceComposer, PBVSController, PBVSReferenceGenerator


def _robot_state() -> RobotState:
    return RobotState(
        joint_state=JointState(
            positions=np.zeros(2, dtype=float),
            velocities=np.zeros(2, dtype=float),
            joint_names=("j1", "j2"),
            timestamp=0.0,
        ),
        end_effector_pose=Pose3D(
            position=np.array([0.3, 0.0, 0.5], dtype=float),
            orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0], dtype=float),
        ),
        timestamp=0.0,
    )


def test_pbvs_with_avoidance_regression() -> None:
    composer = PBVSAvoidanceComposer(
        pbvs_controller=PBVSController(reference_generator=PBVSReferenceGenerator(gain=0.5)),
        avoidance=CuckooSearchAvoidance(safe_distance=0.2, candidate_scale=0.05),
        trajectory_adapter=TrajectoryReferenceAdapter(),
    )

    robot_state = _robot_state()
    current_pose = Pose3D(
        position=np.array([0.5, 0.0, 0.5], dtype=float),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0], dtype=float),
    )
    desired_pose = Pose3D(
        position=np.array([0.4, 0.0, 0.5], dtype=float),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0], dtype=float),
    )
    obstacles = [
        ObstacleState(
            obstacle_id="obs_far",
            pose=Pose3D(
                position=np.array([1.5, 1.5, 1.5], dtype=float),
                orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0], dtype=float),
            ),
            radius=0.1,
            confidence=1.0,
            timestamp=0.0,
        )
    ]

    visual_error, trajectory = composer.compute_reference(
        robot_state=robot_state,
        current_target_pose=current_pose,
        desired_target_pose=desired_pose,
        obstacles=obstacles,
        dt=0.1,
    )

    clearance = compute_minimum_clearance(
        end_effector_poses=[robot_state.end_effector_pose],
        obstacles=obstacles,
    )

    assert visual_error.norm > 0.0
    assert len(trajectory.samples) >= 2
    assert clearance.value > 1.5
