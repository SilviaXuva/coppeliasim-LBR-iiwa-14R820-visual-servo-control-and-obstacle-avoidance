from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from ..models.pose import Pose


class DrawingPort(Protocol):
    """Boundary for drawing primitives in simulation scenes."""

    def draw_point(self, position: Sequence[float]) -> None:
        """Draw a point in world coordinates."""

    def draw_line(self, start: Sequence[float], end: Sequence[float]) -> None:
        """Draw a line segment between two world coordinates."""

    def draw_path(self, points: Sequence[Sequence[float]]) -> None:
        """Draw a path by connecting consecutive points."""

    def draw_frame(self, pose: Pose) -> None:
        """Draw a 3D coordinate frame at the given pose."""

    def clear(self) -> None:
        """Clear all drawing primitives created by this adapter."""
