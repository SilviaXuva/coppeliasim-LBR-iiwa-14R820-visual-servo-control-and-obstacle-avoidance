from __future__ import annotations

import numpy as np

from manipulator_framework.core.control import JointSpacePIController
from manipulator_framework.core.types import (
    CommandMode,
    JointState,
    RobotState,
    TrajectorySample,
)


def _robot_state(q: np.ndarray, qd: np.ndarray) -> RobotState:
    return RobotState(
        joint_state=JointState(
            positions=q,
            velocities=qd,
            joint_names=("j1", "j2"),
            timestamp=0.0,
        ),
        timestamp=0.0,
    )


def _reference(goal: np.ndarray) -> TrajectorySample:
    return TrajectorySample(
        time_from_start=0.0,
        joint_state=JointState(
            positions=goal,
            velocities=np.zeros_like(goal),
            accelerations=np.zeros_like(goal),
            joint_names=("j1", "j2"),
            timestamp=0.0,
        ),
    )


def test_joint_controller_regression() -> None:
    controller = JointSpacePIController(
        dof=2,
        kp=np.array([2.0, 2.0], dtype=float),
        ki=np.array([0.6, 0.6], dtype=float),
        command_mode=CommandMode.VELOCITY,
        output_limit=np.array([2.5, 2.5], dtype=float),
    )

    q = np.array([0.0, 0.0], dtype=float)
    qd = np.zeros(2, dtype=float)
    goal = np.array([1.0, -1.0], dtype=float)
    dt = 0.05

    initial_error = float(np.linalg.norm(goal - q))
    history: list[float] = []

    for _ in range(30):
        output = controller.compute_control(_robot_state(q, qd), _reference(goal), dt=dt)
        assert output.joint_command is not None
        qd = np.asarray(output.joint_command.values, dtype=float)
        q = q + qd * dt
        history.append(float(np.linalg.norm(goal - q)))

    assert history[-1] < 0.35
    assert history[-1] < initial_error
    assert np.all(np.isfinite(np.asarray(history)))
