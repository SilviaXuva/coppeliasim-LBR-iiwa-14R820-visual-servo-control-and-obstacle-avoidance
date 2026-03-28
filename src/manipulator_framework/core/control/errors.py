from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from manipulator_framework.core.types import JointState


@dataclass(frozen=True)
class JointTrackingError:
    position_error: np.ndarray
    velocity_error: np.ndarray


def compute_joint_tracking_error(
    current: JointState,
    reference: JointState,
) -> JointTrackingError:
    if current.dof != reference.dof:
        raise ValueError("current and reference must have the same number of joints.")

    q = np.asarray(current.positions, dtype=float)
    q_ref = np.asarray(reference.positions, dtype=float)

    dq = np.zeros_like(q) if current.velocities is None else np.asarray(current.velocities, dtype=float)
    dq_ref = np.zeros_like(q_ref) if reference.velocities is None else np.asarray(reference.velocities, dtype=float)

    return JointTrackingError(
        position_error=q_ref - q,
        velocity_error=dq_ref - dq,
    )
