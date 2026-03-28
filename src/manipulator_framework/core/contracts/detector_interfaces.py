from __future__ import annotations

from abc import ABC, abstractmethod

from manipulator_framework.core.types import CameraFrame, MarkerDetection, PersonDetection, Detection2D


class MarkerDetectorInterface(ABC):
    """Detect fiducial markers from a frame."""

    @abstractmethod
    def detect_markers(self, frame: CameraFrame) -> list[MarkerDetection]:
        raise NotImplementedError


class PersonDetectorInterface(ABC):
    """Detect people from a frame."""

    @abstractmethod
    def detect_people(self, frame: CameraFrame) -> list[PersonDetection]:
        raise NotImplementedError


class ObjectDetectorInterface(ABC):
    """Detect generic objects from a frame."""

    @abstractmethod
    def detect_objects(self, frame: CameraFrame) -> list[Detection2D]:
        raise NotImplementedError
