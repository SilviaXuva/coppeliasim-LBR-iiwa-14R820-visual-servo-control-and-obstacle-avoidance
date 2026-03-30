from __future__ import annotations

from abc import ABC, abstractmethod

from manipulator_framework.core.types import ControlOutput, RobotState, TrajectorySample


class ControllerInterface(ABC):
    """Joint-space or torque-space controller contract."""

    @abstractmethod
    def compute_control(
        self,
        robot_state: RobotState,
        reference: TrajectorySample,
        dt: float,
    ) -> ControlOutput:
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError
