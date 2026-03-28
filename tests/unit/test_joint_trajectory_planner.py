from __future__ import annotations

import numpy as np

from manipulator_framework.core.planning import QuinticJointTrajectoryPlanner
from manipulator_framework.core.types import JointState


def test_joint_trajectory_planner_generates_expected_endpoints() -> None:
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

    trajectory = planner.plan(start=start, goal=goal, duration=2.0, time_step=0.25)

    assert np.allclose(trajectory.samples[0].joint_state.positions, start.positions)
    assert np.allclose(trajectory.samples[-1].joint_state.positions, goal.positions)
    assert trajectory.dof == 7
