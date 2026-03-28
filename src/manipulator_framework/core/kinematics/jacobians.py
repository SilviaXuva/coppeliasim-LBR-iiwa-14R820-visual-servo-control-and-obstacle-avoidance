from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from manipulator_framework.core.robot_model.iiwa14r820_model import Iiwa14R820Model
from .rtb_backend import RoboticsToolboxIiwaBackend


@dataclass
class JacobianSolver:
    """Compute the geometric Jacobian in the base frame."""

    model: Iiwa14R820Model

    def compute_geometric(self, q: np.ndarray) -> np.ndarray:
        self.model.validate_configuration(q)
        backend = RoboticsToolboxIiwaBackend(self.model)
        robot = backend.build_robot()
        jac = robot.jacob0(q)
        return np.asarray(jac, dtype=float)
