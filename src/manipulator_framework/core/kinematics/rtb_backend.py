from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from roboticstoolbox import DHRobot, RevoluteDH
from spatialmath import SE3

from manipulator_framework.core.robot_model.iiwa14r820_model import Iiwa14R820Model


@dataclass
class RoboticsToolboxIiwaBackend:
    """
    Encapsulated Robotics Toolbox backend for iiwa kinematics.

    This is the only place in this level where roboticstoolbox is imported directly.
    """

    model: Iiwa14R820Model

    def build_robot(self) -> DHRobot:
        links = [
            RevoluteDH(
                d=row.d,
                a=row.a,
                alpha=row.alpha_rad,
                qlim=[lower, upper],
            )
            for row, lower, upper in zip(
                self.model.dh_parameters,
                self.model.joint_limits.lower,
                self.model.joint_limits.upper,
            )
        ]
        robot = DHRobot(links, name=self.model.name, manufacturer="KUKA")
        return robot

    def solve_inverse_kinematics(self, *, target_matrix: np.ndarray, q0: np.ndarray):
        matrix = np.asarray(target_matrix, dtype=float)
        if matrix.shape != (4, 4):
            raise ValueError("target_matrix must have shape (4, 4).")
        robot = self.build_robot()
        return robot.ikine_LM(SE3(matrix), q0=np.asarray(q0, dtype=float).reshape(-1))
