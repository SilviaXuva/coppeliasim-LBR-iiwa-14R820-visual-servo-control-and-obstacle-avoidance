from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from ..models.robot_state import RobotState


class RobotPort(Protocol):
    """Robot actuation + state access boundary."""

    def get_state(self) -> RobotState:
        """Return the latest full robot state."""

    def get_joints_positions(self) -> tuple[float, ...]:
        """Return current joint position vector."""

    def command_joints_positions(self, joints_positions: Sequence[float]) -> None:
        """Send a position target to robot joints."""

    def command_joints_velocities(self, joints_velocities: Sequence[float]) -> None:
        """Send a velocity target to robot joints."""

    def step(self, reference_xyz: Sequence[float] | None = None) -> None:
        """Advance one simulation/control step."""
