from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np

from manipulator_framework.core.types import CommandMode, ControlOutput, JointCommand, RobotState, TrajectorySample
from .base import BaseJointController
from .control_laws import compute_pi_control
from .errors import compute_joint_tracking_error
from .interfaces import JointControllerInterface
from .saturation import symmetric_clip


@dataclass
class JointSpacePIController(BaseJointController, JointControllerInterface):
    """
    Pure joint-space PI controller.

    Output convention:
        Returns a JointCommand in VELOCITY mode by default.
    """
    kp: np.ndarray = field(default_factory=lambda: np.ones(7, dtype=float))
    ki: np.ndarray = field(default_factory=lambda: np.zeros(7, dtype=float))
    integral_limit: np.ndarray | float | None = None
    command_mode: CommandMode = CommandMode.VELOCITY
    _integral_error: np.ndarray = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.kp = np.asarray(self.kp, dtype=float).reshape(self.dof)
        self.ki = np.asarray(self.ki, dtype=float).reshape(self.dof)
        self._integral_error = np.zeros(self.dof, dtype=float)

    def compute_control(
        self,
        robot_state: RobotState,
        reference: TrajectorySample,
        dt: float,
    ) -> ControlOutput:
        if dt <= 0.0:
            raise ValueError("dt must be positive.")

        self._validate_robot_state(robot_state)

        error = compute_joint_tracking_error(robot_state.joint_state, reference.joint_state)
        self._integral_error = self._integral_error + error.position_error * dt

        if self.integral_limit is not None:
            self._integral_error = symmetric_clip(self._integral_error, self.integral_limit)

        u = compute_pi_control(
            position_error=error.position_error,
            integral_error=self._integral_error,
            kp=self.kp,
            ki=self.ki,
        )

        if self.output_limit is not None:
            u = symmetric_clip(u, self.output_limit)

        command = JointCommand(
            values=u,
            mode=self.command_mode,
            joint_names=robot_state.joint_state.joint_names,
            timestamp=reference.time_from_start,
        )

        return ControlOutput(
            joint_command=command,
            status="ok",
            message="PI joint control output computed.",
            timestamp=reference.time_from_start,
        )

    def reset(self) -> None:
        self._integral_error = np.zeros(self.dof, dtype=float)
