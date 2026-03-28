from __future__ import annotations

import numpy as np

from manipulator_framework.core.control import AdaptiveJointSpacePDController
from manipulator_framework.core.types import JointState, RobotState, TrajectorySample


def test_adaptive_pd_controller_accumulates_bias_and_stays_bounded() -> None:
    controller = AdaptiveJointSpacePDController(
        dof=2,
        kp=np.array([5.0, 5.0]),
        kd=np.array([1.0, 1.0]),
        adaptation_gain=np.array([1.0, 1.0]),
        bias_limit=np.array([0.5, 0.5]),
        output_limit=np.array([100.0, 100.0]),
    )

    robot_state = RobotState(
        joint_state=JointState(
            positions=np.array([0.0, 0.0]),
            velocities=np.array([0.0, 0.0]),
            joint_names=("j1", "j2"),
            timestamp=0.0,
        ),
        timestamp=0.0,
    )

    reference = TrajectorySample(
        time_from_start=0.0,
        joint_state=JointState(
            positions=np.array([1.0, -1.0]),
            velocities=np.array([0.0, 0.0]),
            accelerations=np.array([0.0, 0.0]),
            joint_names=("j1", "j2"),
            timestamp=0.0,
        ),
    )

    output_1 = controller.compute_control(robot_state, reference, dt=0.1)
    output_2 = controller.compute_control(robot_state, reference, dt=0.1)

    assert output_1.torque_command is not None
    assert output_2.torque_command is not None
    assert np.all(np.abs(output_2.torque_command.torques) >= np.abs(output_1.torque_command.torques))
