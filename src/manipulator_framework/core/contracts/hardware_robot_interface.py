from __future__ import annotations

from abc import abstractmethod

from .robot_interface import RobotInterface


class HardwareRobotInterface(RobotInterface):
    """Specialized robot boundary for real hardware."""

    @abstractmethod
    def enable(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def disable(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def emergency_stop(self) -> None:
        raise NotImplementedError
