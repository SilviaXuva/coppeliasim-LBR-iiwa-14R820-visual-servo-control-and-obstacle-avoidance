from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from manipulator_framework.core.robot_model.iiwa14r820_model import Iiwa14R820Model
from manipulator_framework.core.kinematics.pose_conversions import se3_to_pose3d
from .rtb_backend import RoboticsToolboxIiwaBackend


@dataclass
class ForwardKinematicsSolver:
    """Pure FK service backed by an encapsulated robotics backend."""

    model: Iiwa14R820Model

    def compute(self, q: np.ndarray, timestamp: float = 0.0):
        self.model.validate_configuration(q)
        backend = RoboticsToolboxIiwaBackend(self.model)
        robot = backend.build_robot()
        transform = robot.fkine(q)

        return se3_to_pose3d(
            transform=transform,
            frame_id=self.model.base_frame,
            child_frame_id=self.model.tool_frame,
            timestamp=timestamp,
        )
