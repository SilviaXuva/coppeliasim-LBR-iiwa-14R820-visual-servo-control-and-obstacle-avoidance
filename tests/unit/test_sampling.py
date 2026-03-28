from __future__ import annotations

import numpy as np

from manipulator_framework.core.planning import NearestSampleInterpolator, QuinticJointTrajectoryPlanner
from manipulator_framework.core.types import JointState


def test_nearest_sample_interpolator_returns_existing_sample() -> None:
    planner = QuinticJointTrajectoryPlanner()

    start = JointState(
        positions=np.zeros(7),
        velocities=np.zeros(7),
        accelerations=np.zeros(7),
        joint_names=tuple(f"joint_{i+1}" for i in range(7)),
        timestamp=0.0,
    )

    goal = JointState(
        positions=np.ones(7),
        velocities=np.zeros(7),
        accelerations=np.zeros(7),
        joint_names=start.joint_names,
        timestamp=0.0,
    )

    trajectory = planner.plan(start=start, goal=goal, duration=1.0, time_step=0.2)
    interpolator = NearestSampleInterpolator(trajectory)

    sample = interpolator.sample(0.41)

    assert sample in trajectory.samples
