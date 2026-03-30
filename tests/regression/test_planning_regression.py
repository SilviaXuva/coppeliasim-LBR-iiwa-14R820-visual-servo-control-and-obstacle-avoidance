from __future__ import annotations

import numpy as np

from manipulator_framework.core.metrics import compute_joint_position_rmse
from manipulator_framework.core.planning import QuinticJointTrajectoryPlanner
from manipulator_framework.core.types import JointState


def _joint_state(positions: list[float], timestamp: float = 0.0) -> JointState:
    arr = np.asarray(positions, dtype=float)
    return JointState(
        positions=arr,
        velocities=np.zeros_like(arr),
        accelerations=np.zeros_like(arr),
        joint_names=("j1", "j2"),
        timestamp=timestamp,
    )


def test_quintic_joint_trajectory_regression_baseline() -> None:
    planner = QuinticJointTrajectoryPlanner()

    start = _joint_state([0.0, 0.0], timestamp=0.0)
    goal = _joint_state([1.0, -1.0], timestamp=0.0)

    trajectory = planner.plan(
        start=start,
        goal=goal,
        duration=2.0,
        time_step=1.0,
    )

    assert len(trajectory.samples) == 3

    sample_0 = trajectory.samples[0].joint_state
    sample_1 = trajectory.samples[1].joint_state
    sample_2 = trajectory.samples[2].joint_state

    assert np.allclose(sample_0.positions, [0.0, 0.0], atol=1e-12)
    assert np.allclose(sample_1.positions, [0.5, -0.5], atol=1e-12)
    assert np.allclose(sample_2.positions, [1.0, -1.0], atol=1e-12)

    assert np.allclose(sample_1.velocities, [0.9375, -0.9375], atol=1e-12)
    assert np.allclose(sample_2.velocities, [0.0, 0.0], atol=1e-12)
    assert np.allclose(sample_2.accelerations, [0.0, 0.0], atol=1e-10)


def test_joint_position_rmse_regression_baseline() -> None:
    reference = [
        _joint_state([0.0, 0.0], timestamp=0.0),
        _joint_state([0.5, -0.5], timestamp=1.0),
        _joint_state([1.0, -1.0], timestamp=2.0),
    ]
    measured = [
        _joint_state([0.0, 0.0], timestamp=0.0),
        _joint_state([0.4, -0.6], timestamp=1.0),
        _joint_state([1.1, -0.9], timestamp=2.0),
    ]

    metric = compute_joint_position_rmse(reference, measured)

    assert metric.name == "joint_position_rmse"
    assert metric.unit == "rad"
    assert np.isclose(metric.value, 0.08164965809277261, atol=1e-12)
