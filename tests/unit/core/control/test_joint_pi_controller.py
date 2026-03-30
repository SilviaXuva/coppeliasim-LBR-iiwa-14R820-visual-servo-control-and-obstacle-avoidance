from __future__ import annotations

import numpy as np

from manipulator_framework.core.control import JointSpacePIController
from manipulator_framework.core.types import JointState, RobotState, TrajectorySample


def test_joint_pi_controller_produces_joint_command() -> None:
    controller = JointSpacePIController(
        dof=2,
        kp=np.array([2.0, 2.0]),
        ki=np.array([1.0, 1.0]),
        output_limit=np.array([10.0, 10.0]),
        integral_limit=np.array([1.0, 1.0]),
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

    output = controller.compute_control(robot_state, reference, dt=0.1)

    assert output.joint_command is not None
    assert output.torque_command is None
    assert output.joint_command.values.shape == (2,)
