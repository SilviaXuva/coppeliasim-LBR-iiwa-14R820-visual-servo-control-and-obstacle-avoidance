from __future__ import annotations

import numpy as np

from manipulator_framework.core.metrics.metric_models import ScalarMetric
from manipulator_framework.core.types import JointState


def compute_joint_position_rmse(
    reference: list[JointState],
    measured: list[JointState],
) -> ScalarMetric:
    if len(reference) != len(measured):
        raise ValueError("reference and measured must have the same length.")
    if not reference:
        raise ValueError("reference and measured cannot be empty.")

    errors = []
    for ref, meas in zip(reference, measured):
        errors.append(np.asarray(ref.positions, dtype=float) - np.asarray(meas.positions, dtype=float))

    stacked = np.vstack(errors)
    rmse = float(np.sqrt(np.mean(stacked ** 2)))

    return ScalarMetric(
        name="joint_position_rmse",
        value=rmse,
        unit="rad",
        description="Root mean squared joint position tracking error.",
    )


def compute_mean_command_effort(commands: list[np.ndarray]) -> ScalarMetric:
    if not commands:
        raise ValueError("commands cannot be empty.")

    norms = [float(np.linalg.norm(np.asarray(cmd, dtype=float))) for cmd in commands]
    return ScalarMetric(
        name="mean_command_effort",
        value=float(np.mean(norms)),
        unit="arb",
        description="Mean command vector norm.",
    )
