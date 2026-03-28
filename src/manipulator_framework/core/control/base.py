from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np

from manipulator_framework.core.types import RobotState


@dataclass
class BaseJointController:
    """
    Common utilities for pure joint-space controllers.
    """

    dof: int
    output_limit: np.ndarray | float | None = None

    def _validate_robot_state(self, robot_state: RobotState) -> None:
        if robot_state.joint_state.dof != self.dof:
            raise ValueError(
                f"Controller expects dof={self.dof}, got {robot_state.joint_state.dof}."
            )

    def reset(self) -> None:
        """Override when controller has state."""
        return None
