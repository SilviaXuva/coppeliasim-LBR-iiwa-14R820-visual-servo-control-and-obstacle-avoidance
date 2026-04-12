from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from ..models.marker_state import MarkerState
from ..models.person_state import PersonState
from ..models.pose import Pose
from ..models.robot_state import RobotState


class VisualizationPort(Protocol):
    """Visualization boundary for simulations, plots, and overlays."""

    def update_robot_state(self, state: RobotState) -> None:
        """Render the latest robot state."""

    def update_reference_path(self, reference_path: Sequence[Pose]) -> None:
        """Render/update reference trajectory path."""

    def update_markers(self, markers: Sequence[MarkerState]) -> None:
        """Render/update detected markers."""

    def update_people(self, people: Sequence[PersonState]) -> None:
        """Render/update detected people."""

    def clear(self) -> None:
        """Clear visual traces/state."""
