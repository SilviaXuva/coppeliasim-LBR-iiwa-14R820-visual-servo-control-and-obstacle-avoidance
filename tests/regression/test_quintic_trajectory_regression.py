from __future__ import annotations

import numpy as np

from manipulator_framework.core.planning import QuinticJointTrajectoryPlanner
from manipulator_framework.core.types import JointState


def _joint_state(values: list[float], timestamp: float = 0.0) -> JointState:
    arr = np.asarray(values, dtype=float)
    return JointState(
        positions=arr,
        velocities=np.zeros_like(arr),
        accelerations=np.zeros_like(arr),
        joint_names=("j1", "j2"),
        timestamp=timestamp,
    )


def test_quintic_trajectory_regression() -> None:
    planner = QuinticJointTrajectoryPlanner()
    start = _joint_state([0.0, 0.0])
    goal = _joint_state([1.0, 0.5])

    trajectory = planner.plan(start=start, goal=goal, duration=1.0, time_step=0.1)

    assert len(trajectory.samples) == 11

    positions = np.asarray([sample.joint_state.positions for sample in trajectory.samples], dtype=float)
    assert np.all(np.diff(positions[:, 0]) >= -1e-9)
    assert np.all(np.diff(positions[:, 1]) >= -1e-9)

    final_error = np.linalg.norm(positions[-1] - goal.positions)
    assert final_error < 1e-6
