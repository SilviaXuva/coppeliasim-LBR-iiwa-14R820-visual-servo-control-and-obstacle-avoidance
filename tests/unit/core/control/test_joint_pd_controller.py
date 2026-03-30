from __future__ import annotations

import numpy as np

from manipulator_framework.core.control import JointSpacePDController
from manipulator_framework.core.types import JointState, RobotState, TrajectorySample


def test_joint_pd_controller_zero_error_produces_zero_torque() -> None:
    controller = JointSpacePDController(
        dof=2,
        kp=np.array([10.0, 10.0]),
        kd=np.array([2.0, 2.0]),
        output_limit=np.array([100.0, 100.0]),
    )

    state = JointState(
        positions=np.array([0.5, -0.3]),
        velocities=np.array([0.0, 0.0]),
        joint_names=("j1", "j2"),
        timestamp=0.0,
    )

    robot_state = RobotState(joint_state=state, timestamp=0.0)
    reference = TrajectorySample(time_from_start=0.0, joint_state=state)

    output = controller.compute_control(robot_state, reference, dt=0.01)

    assert output.torque_command is not None
    assert np.allclose(output.torque_command.torques, np.zeros(2))
