from __future__ import annotations

import numpy as np

from manipulator_framework.core.types import (
    CommandMode,
    ControlOutput,
    JointCommand,
    JointState,
    Trajectory,
    TrajectorySample,
)


def make_joint_state(positions: list[float], t: float) -> JointState:
    return JointState(
        positions=np.array(positions, dtype=float),
        velocities=np.zeros(len(positions)),
        timestamp=t,
    )


def main() -> None:
    sample_0 = TrajectorySample(time_from_start=0.0, joint_state=make_joint_state([0, 0, 0, 0, 0, 0, 0], 0.0))
    sample_1 = TrajectorySample(time_from_start=1.0, joint_state=make_joint_state([0.1, 0.2, 0.0, -0.1, 0.0, 0.1, 0.0], 1.0))
    sample_2 = TrajectorySample(time_from_start=2.0, joint_state=make_joint_state([0.2, 0.3, 0.1, -0.2, 0.0, 0.2, 0.1], 2.0))

    trajectory = Trajectory(
        samples=(sample_0, sample_1, sample_2),
        name="joint_reference_demo",
        timestamp=0.0,
    )

    command = JointCommand(
        values=np.array([0.2, 0.3, 0.1, -0.2, 0.0, 0.2, 0.1]),
        mode=CommandMode.POSITION,
        timestamp=2.0,
    )

    output = ControlOutput(
        joint_command=command,
        status="ok",
        message="Reference command generated from trajectory endpoint.",
        timestamp=2.0,
    )

    print("Trajectory duration:", trajectory.duration)
    print(output.to_dict())


if __name__ == "__main__":
    main()
