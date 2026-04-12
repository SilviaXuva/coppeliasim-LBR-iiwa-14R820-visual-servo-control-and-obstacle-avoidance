from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from ..models.pose import Pose


JacobianMatrix = tuple[
    tuple[float, ...],
    tuple[float, ...],
    tuple[float, ...],
    tuple[float, ...],
    tuple[float, ...],
    tuple[float, ...],
]


class KinematicsPort(Protocol):
    """Kinematics and trajectory planning boundary."""

    def forward_kinematics(self, joints_positions: Sequence[float]) -> Pose:
        """Compute end-effector pose from joint positions."""

    def inverse_kinematics(
        self,
        target_pose: Pose,
        seed_joints_positions: Sequence[float] | None = None,
    ) -> tuple[float, ...]:
        """Compute joint positions that reach target pose."""

    def jacobian(self, joints_positions: Sequence[float]) -> JacobianMatrix:
        """Return analytical/geometric Jacobian."""

    def plan_joint_trajectory(
        self,
        start_joints_positions: Sequence[float],
        goal_joints_positions: Sequence[float],
        time_samples_s: Sequence[float],
    ) -> Sequence[tuple[float, ...]]:
        """Plan a joint-space trajectory."""

    def plan_cartesian_trajectory(
        self,
        start_pose: Pose,
        goal_pose: Pose,
        time_samples_s: Sequence[float],
    ) -> Sequence[Pose]:
        """Plan a Cartesian trajectory."""
