from __future__ import annotations

import numpy as np

from manipulator_framework.core.types import JointState, Trajectory, TrajectorySample


def make_trajectory_sample(
    positions: np.ndarray,
    velocities: np.ndarray,
    accelerations: np.ndarray,
    time_from_start: float,
    joint_names: tuple[str, ...] = (),
) -> TrajectorySample:
    state = JointState(
        positions=np.asarray(positions, dtype=float),
        velocities=np.asarray(velocities, dtype=float),
        accelerations=np.asarray(accelerations, dtype=float),
        joint_names=joint_names,
        timestamp=time_from_start,
    )
    return TrajectorySample(time_from_start=time_from_start, joint_state=state)


def make_trajectory(
    samples: list[TrajectorySample],
    name: str,
    timestamp: float = 0.0,
) -> Trajectory:
    return Trajectory(samples=tuple(samples), name=name, timestamp=timestamp)
