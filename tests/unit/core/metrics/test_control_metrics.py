from __future__ import annotations

import numpy as np

from manipulator_framework.core.metrics import (
    compute_joint_position_rmse,
    compute_mean_command_effort,
)
from manipulator_framework.core.types import JointState


def make_joint_state(values: list[float], timestamp: float) -> JointState:
    arr = np.asarray(values, dtype=float)
    return JointState(
        positions=arr,
        velocities=np.zeros_like(arr),
        accelerations=np.zeros_like(arr),
        joint_names=tuple(f"joint_{i+1}" for i in range(arr.size)),
        timestamp=timestamp,
    )


def test_compute_joint_position_rmse_returns_expected_value() -> None:
    reference = [
        make_joint_state([0.0, 0.0], 0.0),
        make_joint_state([1.0, 1.0], 1.0),
    ]
    measured = [
        make_joint_state([0.0, 0.0], 0.0),
        make_joint_state([0.0, 0.0], 1.0),
    ]

    metric = compute_joint_position_rmse(reference, measured)

    assert metric.name == "joint_position_rmse"
    assert metric.unit == "rad"
    assert np.isclose(metric.value, np.sqrt(0.5))


def test_compute_mean_command_effort_returns_mean_norm() -> None:
    commands = [
        np.array([3.0, 4.0], dtype=float),   # norm = 5
        np.array([0.0, 0.0], dtype=float),   # norm = 0
    ]

    metric = compute_mean_command_effort(commands)

    assert metric.name == "mean_command_effort"
    assert metric.unit == "arb"
    assert np.isclose(metric.value, 2.5)
