from __future__ import annotations

import numpy as np

from manipulator_framework.core.control import (
    AdaptiveJointSpacePDController,
    JointSpacePDController,
    JointSpacePIController,
)
from manipulator_framework.core.metrics import compute_mean_command_effort
from manipulator_framework.core.types import (
    CommandMode,
    JointState,
    RobotState,
    TrajectorySample,
)


def _robot_state(
    positions: list[float],
    velocities: list[float],
    timestamp: float = 0.0,
) -> RobotState:
    return RobotState(
        joint_state=JointState(
            positions=np.asarray(positions, dtype=float),
            velocities=np.asarray(velocities, dtype=float),
            joint_names=("j1", "j2"),
            timestamp=timestamp,
        ),
        timestamp=timestamp,
    )


def _reference_sample(
    positions: list[float],
    velocities: list[float],
    accelerations: list[float] | None = None,
    time_from_start: float = 0.0,
) -> TrajectorySample:
    if accelerations is None:
        accelerations = [0.0, 0.0]

    return TrajectorySample(
        time_from_start=time_from_start,
        joint_state=JointState(
            positions=np.asarray(positions, dtype=float),
            velocities=np.asarray(velocities, dtype=float),
            accelerations=np.asarray(accelerations, dtype=float),
            joint_names=("j1", "j2"),
            timestamp=time_from_start,
        ),
    )


def test_joint_pi_controller_regression_baseline() -> None:
    controller = JointSpacePIController(
        dof=2,
        kp=np.array([2.0, 3.0], dtype=float),
        ki=np.array([1.0, 0.5], dtype=float),
        integral_limit=np.array([10.0, 10.0], dtype=float),
        command_mode=CommandMode.VELOCITY,
        output_limit=np.array([100.0, 100.0], dtype=float),
    )

    robot_state = _robot_state(
        positions=[0.0, 0.5],
        velocities=[0.0, 0.0],
        timestamp=0.0,
    )
    reference = _reference_sample(
        positions=[1.0, -0.5],
        velocities=[0.0, 0.0],
        time_from_start=0.1,
    )

    output = controller.compute_control(robot_state, reference, dt=0.1)

    assert output.joint_command is not None
    assert output.joint_command.mode == CommandMode.VELOCITY
    assert np.allclose(output.joint_command.values, [2.1, -3.05], atol=1e-12)


def test_joint_pd_controller_regression_baseline() -> None:
    controller = JointSpacePDController(
        dof=2,
        kp=np.array([10.0, 20.0], dtype=float),
        kd=np.array([2.0, 3.0], dtype=float),
        output_limit=np.array([100.0, 100.0], dtype=float),
    )

    robot_state = _robot_state(
        positions=[0.5, -0.2],
        velocities=[0.1, -0.1],
        timestamp=0.0,
    )
    reference = _reference_sample(
        positions=[1.0, 0.0],
        velocities=[0.0, 0.2],
        time_from_start=0.1,
    )

    output = controller.compute_control(robot_state, reference, dt=0.1)

    assert output.torque_command is not None
    assert np.allclose(output.torque_command.torques, [4.8, 4.9], atol=1e-12)


def test_adaptive_joint_pd_controller_regression_baseline() -> None:
    controller = AdaptiveJointSpacePDController(
        dof=2,
        kp=np.array([5.0, 5.0], dtype=float),
        kd=np.array([1.0, 1.0], dtype=float),
        adaptation_gain=np.array([1.0, 2.0], dtype=float),
        bias_limit=np.array([10.0, 10.0], dtype=float),
        output_limit=np.array([100.0, 100.0], dtype=float),
    )

    robot_state = _robot_state(
        positions=[0.0, 0.0],
        velocities=[0.0, 0.0],
        timestamp=0.0,
    )
    reference = _reference_sample(
        positions=[1.0, -1.0],
        velocities=[0.0, 0.0],
        time_from_start=0.1,
    )

    output_1 = controller.compute_control(robot_state, reference, dt=0.1)
    output_2 = controller.compute_control(robot_state, reference, dt=0.1)

    assert output_1.torque_command is not None
    assert output_2.torque_command is not None

    assert np.allclose(output_1.torque_command.torques, [5.1, -5.2], atol=1e-12)
    assert np.allclose(output_2.torque_command.torques, [5.2, -5.4], atol=1e-12)


def test_mean_command_effort_regression_baseline() -> None:
    commands = [
        np.array([3.0, 4.0], dtype=float),
        np.array([0.0, 0.0], dtype=float),
        np.array([6.0, 8.0], dtype=float),
    ]

    metric = compute_mean_command_effort(commands)

    assert metric.name == "mean_command_effort"
    assert metric.unit == "arb"
    assert np.isclose(metric.value, 5.0, atol=1e-12)
