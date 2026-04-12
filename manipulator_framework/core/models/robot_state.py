from __future__ import annotations

from dataclasses import dataclass, field

from .pose import Pose


@dataclass(slots=True)
class RobotState:
    """Robot measurements used by control and planning use-cases."""

    joints_positions: tuple[float, ...]
    joints_velocities: tuple[float, ...] = field(default_factory=tuple)
    joints_accelerations: tuple[float, ...] = field(default_factory=tuple)
    tool_pose: Pose | None = None
    timestamp_s: float | None = None

    @property
    def joints_count(self) -> int:
        return len(self.joints_positions)
