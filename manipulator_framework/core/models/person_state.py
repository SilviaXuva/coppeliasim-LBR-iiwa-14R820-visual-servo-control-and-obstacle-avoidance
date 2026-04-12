from __future__ import annotations

from dataclasses import dataclass

from .pose import Pose


@dataclass(slots=True)
class PersonState:
    """Minimal human/obstacle state for avoidance and monitoring."""

    person_id: str
    pose_world: Pose | None = None
    velocity_xyz: tuple[float, float, float] = (0.0, 0.0, 0.0)
    confidence: float | None = None
    tracked: bool = True
    timestamp_s: float | None = None
