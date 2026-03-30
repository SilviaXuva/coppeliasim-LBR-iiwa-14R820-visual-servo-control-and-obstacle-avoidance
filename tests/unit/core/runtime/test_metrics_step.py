from __future__ import annotations

import numpy as np

from manipulator_framework.core.runtime import MetricsStep, RuntimeContext
from manipulator_framework.core.types import JointState, Pose3D, RobotState, Trajectory, TrajectorySample


def test_metrics_step_records_visual_joint_and_success_metrics() -> None:
    context = RuntimeContext(
        cycle_index=2,
        timestamp=1.5,
        target_pose=Pose3D(position=np.array([1.0, 0.0, 0.0])),
        robot_state=RobotState(
            joint_state=JointState(positions=np.array([0.0, 0.0, 0.0])),
            end_effector_pose=Pose3D(position=np.array([0.0, 0.0, 0.0])),
        ),
        trajectory_reference=Trajectory(
            samples=(
                TrajectorySample(
                    time_from_start=0.0,
                    joint_state=JointState(positions=np.array([0.5, 0.5, 0.5])),
                ),
            )
        ),
    )

    result = MetricsStep(visual_success_threshold=0.2).run(context)

    assert result.success is True
    metrics = context.metadata["cycle_metrics"]
    assert isinstance(metrics, dict)
    assert np.isclose(float(metrics["visual_error"]), 1.0)
    assert np.isclose(float(metrics["joint_error"]), np.sqrt(0.75))
    assert float(metrics["success"]) == 0.0
