from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from manipulator_framework.core.types import JointState, Trajectory, TrajectorySample
from .obstacle_models import AvoidanceResult


@dataclass
class TrajectoryReferenceAdapter:
    """
    Apply avoidance output to the final sample of a reference trajectory.
    """

    def adapt(self, reference: Trajectory, result: AvoidanceResult) -> Trajectory:
        samples = list(reference.samples)
        last = samples[-1]
        q = np.asarray(last.joint_state.positions, dtype=float)
        adapted_q = q + result.best_delta_q

        samples[-1] = TrajectorySample(
            time_from_start=last.time_from_start,
            joint_state=JointState(
                positions=adapted_q,
                velocities=last.joint_state.velocities,
                accelerations=last.joint_state.accelerations,
                efforts=last.joint_state.efforts,
                joint_names=last.joint_state.joint_names,
                timestamp=last.joint_state.timestamp,
            ),
        )

        return Trajectory(
            samples=tuple(samples),
            name=f"{reference.name}_avoidance_adapted",
            timestamp=reference.timestamp,
        )
