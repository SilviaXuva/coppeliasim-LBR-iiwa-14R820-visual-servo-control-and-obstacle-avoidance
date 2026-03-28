from __future__ import annotations

from abc import ABC, abstractmethod

from manipulator_framework.core.types import ControlOutput, RobotState, TrajectorySample


class JointControllerInterface(ABC):
    """Abstract contract for pure joint-space controllers."""

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
