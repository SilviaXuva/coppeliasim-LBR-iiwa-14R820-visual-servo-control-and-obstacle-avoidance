from __future__ import annotations

from abc import ABC, abstractmethod

from manipulator_framework.core.types import ObstacleState, RobotState, Trajectory


class ObstacleSourceInterface(ABC):
    """Provide obstacle state to the pipeline."""

    @abstractmethod
    def get_obstacles(self) -> list[ObstacleState]:
        raise NotImplementedError


class ObstacleAvoidanceInterface(ABC):
    """Adapt a reference trajectory according to obstacle information."""

    @abstractmethod
    def adapt_trajectory(
        self,
        reference: Trajectory,
        obstacles: list[ObstacleState],
        robot_state: RobotState,
    ) -> Trajectory:
        raise NotImplementedError
