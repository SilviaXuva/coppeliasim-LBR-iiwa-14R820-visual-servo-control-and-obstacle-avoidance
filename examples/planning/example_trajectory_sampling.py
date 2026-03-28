from __future__ import annotations

import numpy as np

from manipulator_framework.core.planning import NearestSampleInterpolator, QuinticJointTrajectoryPlanner
from manipulator_framework.core.types import JointState


def main() -> None:
    planner = QuinticJointTrajectoryPlanner()

    start = JointState(
        positions=np.zeros(7),
        velocities=np.zeros(7),
        accelerations=np.zeros(7),
        joint_names=tuple(f"joint_{i+1}" for i in range(7)),
        timestamp=0.0,
    )

    goal = JointState(
        positions=np.array([0.5, 0.3, -0.2, 0.1, 0.0, -0.1, 0.2]),
        velocities=np.zeros(7),
        accelerations=np.zeros(7),
        joint_names=start.joint_names,
        timestamp=0.0,
    )

    trajectory = planner.plan(start=start, goal=goal, duration=3.0, time_step=0.5)
    interpolator = NearestSampleInterpolator(trajectory)

    sample = interpolator.sample(1.1)

    print("Requested time:", 1.1)
    print("Returned sample time:", sample.time_from_start)
    print(sample.to_dict())


if __name__ == "__main__":
    main()
