from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from manipulator_framework.core.types import JointState, Trajectory, TrajectorySample
from .visual_error import VisualError


@dataclass
class PBVSReferenceGenerator:
    """
    Convert visual error into a small synthetic joint-space reference update.

    Placeholder:
        This is intentionally minimal. A more rigorous coupling with the robot
        Jacobian can replace this later.
    """
    gain: float = 0.5

    def generate(
        self,
        current_joint_state: JointState,
        visual_error: VisualError,
        dt: float,
    ) -> Trajectory:
        if dt <= 0.0:
            raise ValueError("dt must be positive.")

        q = np.asarray(current_joint_state.positions, dtype=float)
        dq = np.zeros_like(q) if current_joint_state.velocities is None else np.asarray(current_joint_state.velocities, dtype=float)

        scalar_error = float(np.linalg.norm(visual_error.position_error))
        delta = self.gain * scalar_error * dt * np.ones_like(q)

        next_q = q + delta

        sample_0 = TrajectorySample(
            time_from_start=0.0,
            joint_state=JointState(
                positions=q,
                velocities=dq,
                accelerations=np.zeros_like(q),
                joint_names=current_joint_state.joint_names,
                timestamp=current_joint_state.timestamp,
            ),
        )

        sample_1 = TrajectorySample(
            time_from_start=dt,
            joint_state=JointState(
                positions=next_q,
                velocities=np.zeros_like(q),
                accelerations=np.zeros_like(q),
                joint_names=current_joint_state.joint_names,
                timestamp=current_joint_state.timestamp + dt,
            ),
        )

        return Trajectory(
            samples=(sample_0, sample_1),
            name="pbvs_reference",
            timestamp=current_joint_state.timestamp,
        )
