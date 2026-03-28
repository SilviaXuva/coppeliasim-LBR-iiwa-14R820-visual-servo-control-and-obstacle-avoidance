from __future__ import annotations

from abc import ABC, abstractmethod

from manipulator_framework.core.types import MarkerDetection, PersonDetection, Pose3D, TrackedTarget


class PoseEstimatorInterface(ABC):
    """Convert observations into estimated pose/state."""

    @abstractmethod
    def estimate_marker_pose(self, detection: MarkerDetection) -> Pose3D | None:
        raise NotImplementedError

    @abstractmethod
    def estimate_person_target(self, detection: PersonDetection) -> TrackedTarget | None:
        raise NotImplementedError
