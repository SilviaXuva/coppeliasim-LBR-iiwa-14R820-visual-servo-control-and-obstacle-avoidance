from __future__ import annotations

import numpy as np

from manipulator_framework.core.visual_servoing import PBVSController, PBVSReferenceGenerator
from manipulator_framework.core.types import JointState, Pose3D, RobotState


def test_pbvs_controller_generates_reference() -> None:
    controller = PBVSController(reference_generator=PBVSReferenceGenerator(gain=0.5))

    robot_state = RobotState(
        joint_state=JointState(
            positions=np.zeros(7),
            velocities=np.zeros(7),
            joint_names=tuple(f"joint_{i+1}" for i in range(7)),
            timestamp=0.0,
        ),
        timestamp=0.0,
    )

    current_pose = Pose3D(
        position=np.array([0.5, 0.0, 0.5]),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
    )
    desired_pose = Pose3D(
        position=np.array([0.4, 0.0, 0.5]),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
    )

    visual_error, reference = controller.compute_reference(
        robot_state=robot_state,
        current_target_pose=current_pose,
        desired_target_pose=desired_pose,
        dt=0.1,
    )

    assert visual_error.norm > 0.0
    assert len(reference.samples) == 2
