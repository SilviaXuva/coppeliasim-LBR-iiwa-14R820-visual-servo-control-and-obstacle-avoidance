from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from spatialmath import SE3

from manipulator_framework.core.robot_model.iiwa14r820_model import Iiwa14R820Model
from .rtb_backend import RoboticsToolboxIiwaBackend


@dataclass(frozen=True)
class IKResult:
    q: np.ndarray
    success: bool
    iterations: int | None = None
    residual: float | None = None
    message: str = ""


@dataclass
class InverseKinematicsSolver:
    """
    Numerical IK service.

    Placeholder policy:
        This uses the Robotics Toolbox numerical IK backend for now.
        The solver strategy can be replaced later without changing callers.
    """

    model: Iiwa14R820Model

    def compute(self, target_transform: SE3, q0: np.ndarray | None = None) -> IKResult:
        backend = RoboticsToolboxIiwaBackend(self.model)
        robot = backend.build_robot()

        q_seed = self.model.qr if q0 is None else np.asarray(q0, dtype=float).reshape(-1)
        solution = robot.ikine_LM(target_transform, q0=q_seed)

        return IKResult(
            q=np.asarray(solution.q, dtype=float),
            success=bool(solution.success),
            iterations=getattr(solution, "iterations", None),
            residual=getattr(solution, "residual", None),
            message="" if solution.success else "Numerical IK did not converge.",
        )
