from __future__ import annotations

from abc import ABC, abstractmethod

from manipulator_framework.core.types import JointState, Trajectory


class JointTrajectoryPlannerInterface(ABC):
    """Abstract contract for pure joint-space trajectory planners."""

    @abstractmethod
    def plan(
        self,
        start: JointState,
        goal: JointState,
        duration: float,
        time_step: float,
    ) -> Trajectory:
        """Generate a joint-space trajectory."""
        raise NotImplementedError
