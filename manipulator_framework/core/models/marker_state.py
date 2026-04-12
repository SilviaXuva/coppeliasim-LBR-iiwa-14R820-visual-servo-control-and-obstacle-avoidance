from __future__ import annotations

from dataclasses import dataclass, field

from .pose import Pose


@dataclass(slots=True)
class MarkerState:
    """Estimated marker data from perception."""

    marker_id: int
    color: str | None = None
    corners_uv: tuple[tuple[float, float], ...] = field(default_factory=tuple)
    pose_camera: Pose | None = None
    pose_world: Pose | None = None
    mass_kg: float | None = None
    confidence: float | None = None
    timestamp_s: float | None = None
