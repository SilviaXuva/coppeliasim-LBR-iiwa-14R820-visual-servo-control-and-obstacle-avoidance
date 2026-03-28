from __future__ import annotations

import numpy as np

from manipulator_framework.core.planning import QuinticJointTrajectoryPlanner
from manipulator_framework.core.types import JointState


def main() -> None:
    planner = QuinticJointTrajectoryPlanner()

    start = JointState(
        positions=np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        velocities=np.zeros(7),
        accelerations=np.zeros(7),
        joint_names=tuple(f"joint_{i+1}" for i in range(7)),
        timestamp=0.0,
    )

    goal = JointState(
        positions=np.array([0.2, -0.1, 0.15, 0.3, -0.2, 0.1, 0.05]),
        velocities=np.zeros(7),
        accelerations=np.zeros(7),
        joint_names=start.joint_names,
        timestamp=0.0,
    )

    trajectory = planner.plan(
        start=start,
        goal=goal,
        duration=2.0,
        time_step=0.2,
    )

    print("Trajectory name:", trajectory.name)
    print("Duration:", trajectory.duration)
    print("Number of samples:", len(trajectory.samples))
    print("First sample:", trajectory.samples[0].to_dict())
    print("Last sample:", trajectory.samples[-1].to_dict())


if __name__ == "__main__":
    main()
