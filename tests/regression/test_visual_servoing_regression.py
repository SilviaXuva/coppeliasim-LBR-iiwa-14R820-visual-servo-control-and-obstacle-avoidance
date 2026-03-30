from __future__ import annotations

import numpy as np

from manipulator_framework.core.metrics import compute_final_visual_position_error
from manipulator_framework.core.obstacle_avoidance import (
    CuckooSearchAvoidance,
    TrajectoryReferenceAdapter,
)
from manipulator_framework.core.types import JointState, ObstacleState, Pose3D, RobotState
from manipulator_framework.core.visual_servoing import (
    PBVSController,
    PBVSReferenceGenerator,
    PBVSAvoidanceComposer,
    compute_pose_error,
)


def _robot_state() -> RobotState:
    return RobotState(
        joint_state=JointState(
            positions=np.zeros(2, dtype=float),
            velocities=np.zeros(2, dtype=float),
            joint_names=("j1", "j2"),
            timestamp=0.0,
        ),
        end_effector_pose=Pose3D(
            position=np.array([0.0, 0.0, 0.0], dtype=float),
            orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0], dtype=float),
            timestamp=0.0,
        ),
        timestamp=0.0,
    )


def _current_pose() -> Pose3D:
    return Pose3D(
        position=np.array([0.5, 0.0, 0.5], dtype=float),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0], dtype=float),
        timestamp=0.0,
    )


def _desired_pose() -> Pose3D:
    return Pose3D(
        position=np.array([0.4, 0.0, 0.5], dtype=float),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0], dtype=float),
        timestamp=0.0,
    )


def test_pbvs_visual_error_regression_baseline() -> None:
    visual_error = compute_pose_error(_current_pose(), _desired_pose())

    assert np.allclose(visual_error.position_error, [-0.1, 0.0, 0.0], atol=1e-12)
    assert np.allclose(visual_error.orientation_error, [0.0, 0.0, 0.0, 0.0], atol=1e-12)
    assert np.isclose(visual_error.norm, 0.1, atol=1e-12)


def test_pbvs_controller_regression_baseline() -> None:
    controller = PBVSController(
        reference_generator=PBVSReferenceGenerator(gain=0.5),
    )

    visual_error, reference = controller.compute_reference(
        robot_state=_robot_state(),
        current_target_pose=_current_pose(),
        desired_target_pose=_desired_pose(),
        dt=0.1,
    )

    assert np.isclose(visual_error.norm, 0.1, atol=1e-12)
    assert len(reference.samples) == 2
    assert np.allclose(reference.samples[0].joint_state.positions, [0.0, 0.0], atol=1e-12)
    assert np.allclose(reference.samples[1].joint_state.positions, [0.005, 0.005], atol=1e-12)
    assert np.allclose(reference.samples[1].joint_state.velocities, [0.0, 0.0], atol=1e-12)


def test_pbvs_avoidance_composition_regression_baseline() -> None:
    composer = PBVSAvoidanceComposer(
        pbvs_controller=PBVSController(
            reference_generator=PBVSReferenceGenerator(gain=0.5),
        ),
        avoidance=CuckooSearchAvoidance(
            safe_distance=0.2,
            candidate_scale=0.05,
        ),
        trajectory_adapter=TrajectoryReferenceAdapter(),
    )

    obstacles = [
        ObstacleState(
            pose=Pose3D(
                position=np.array([2.0, 2.0, 2.0], dtype=float),
                orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0], dtype=float),
                timestamp=0.0,
            ),
            radius=0.1,
            obstacle_id="obs_far",
            timestamp=0.0,
        )
    ]

    visual_error, final_reference = composer.compute_reference(
        robot_state=_robot_state(),
        current_target_pose=_current_pose(),
        desired_target_pose=_desired_pose(),
        obstacles=obstacles,
        dt=0.1,
    )

    assert np.isclose(visual_error.norm, 0.1, atol=1e-12)
    assert np.allclose(
        final_reference.samples[-1].joint_state.positions,
        [0.005, 0.005],
        atol=1e-12,
    )


def test_final_visual_position_error_regression_baseline() -> None:
    metric = compute_final_visual_position_error(
        current_pose=_current_pose(),
        desired_pose=_desired_pose(),
    )

    assert metric.name == "final_visual_position_error"
    assert metric.unit == "m"
    assert np.isclose(metric.value, 0.1, atol=1e-12)
