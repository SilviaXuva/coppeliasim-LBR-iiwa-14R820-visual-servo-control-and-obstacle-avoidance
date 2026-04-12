from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from ..models.marker_state import MarkerState
from ..models.person_state import PersonState


class PerceptionPort(Protocol):
    """Perception boundary for marker and person/human estimation."""

    def detect_markers(self, frame: object) -> Sequence[MarkerState]:
        """Detect and estimate markers in the given frame."""

    def detect_people(self, frame: object) -> Sequence[PersonState]:
        """Detect and estimate people in the given frame."""
