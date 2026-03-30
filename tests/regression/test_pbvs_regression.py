from __future__ import annotations

import numpy as np

from manipulator_framework.core.metrics import compute_final_visual_position_error
from manipulator_framework.core.types import JointState, Pose3D, RobotState
from manipulator_framework.core.visual_servoing import PBVSController, PBVSReferenceGenerator


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
        ),
        timestamp=0.0,
    )


def test_pbvs_regression() -> None:
    controller = PBVSController(reference_generator=PBVSReferenceGenerator(gain=0.6))
    robot_state = _robot_state()

    desired_pose = Pose3D(
        position=np.array([0.40, 0.0, 0.50], dtype=float),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0], dtype=float),
    )
    current_far = Pose3D(
        position=np.array([0.55, 0.0, 0.50], dtype=float),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0], dtype=float),
    )
    current_near = Pose3D(
        position=np.array([0.45, 0.0, 0.50], dtype=float),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0], dtype=float),
    )

    err_far, ref_far = controller.compute_reference(
        robot_state=robot_state,
        current_target_pose=current_far,
        desired_target_pose=desired_pose,
        dt=0.1,
    )
    err_near, ref_near = controller.compute_reference(
        robot_state=robot_state,
        current_target_pose=current_near,
        desired_target_pose=desired_pose,
        dt=0.1,
    )

    delta_far = np.linalg.norm(ref_far.samples[-1].joint_state.positions - ref_far.samples[0].joint_state.positions)
    delta_near = np.linalg.norm(ref_near.samples[-1].joint_state.positions - ref_near.samples[0].joint_state.positions)

    assert err_far.norm > err_near.norm
    assert delta_far > delta_near
    assert err_near.norm < 0.06

    metric = compute_final_visual_position_error(current_pose=current_near, desired_pose=desired_pose)
    assert metric.value < 0.06
