from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.contracts import PersonDetectorInterface
from manipulator_framework.core.types import CameraFrame, PersonDetection


@dataclass
class StubPersonDetector(PersonDetectorInterface):
    """
    Minimal person detector that returns nothing.
    Used to satisfy the pipeline requirements during simulation-only research.
    """
    def detect_people(self, frame: CameraFrame) -> list[PersonDetection]:
        return []
