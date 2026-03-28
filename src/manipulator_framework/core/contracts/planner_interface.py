from __future__ import annotations

from abc import ABC, abstractmethod

from manipulator_framework.core.types import RobotState, Trajectory, TrackedTarget


class PlannerInterface(ABC):
    """
    Abstract interface for motion/reference planners.
    """

    @abstractmethod
    def plan(
        self,
        robot_state: RobotState,
        tracked_targets: list[TrackedTarget],
    ) -> Trajectory:
        raise NotImplementedError
