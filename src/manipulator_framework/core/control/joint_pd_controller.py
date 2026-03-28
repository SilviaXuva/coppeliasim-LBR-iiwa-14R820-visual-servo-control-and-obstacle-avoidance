from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np

from manipulator_framework.core.types import ControlOutput, RobotState, TorqueCommand, TrajectorySample
from .base import BaseJointController
from .control_laws import compute_pd_control
from .errors import compute_joint_tracking_error
from .interfaces import JointControllerInterface
from .saturation import symmetric_clip


@dataclass
class JointSpacePDController(BaseJointController, JointControllerInterface):
    """
    Pure joint-space PD controller.

    Output convention:
        Returns a TorqueCommand.
    """
    kp: np.ndarray = field(default_factory=lambda: np.ones(7, dtype=float))
    kd: np.ndarray = field(default_factory=lambda: np.ones(7, dtype=float))

    def __post_init__(self) -> None:
        self.kp = np.asarray(self.kp, dtype=float).reshape(self.dof)
        self.kd = np.asarray(self.kd, dtype=float).reshape(self.dof)

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

        tau = compute_pd_control(
            position_error=error.position_error,
            velocity_error=error.velocity_error,
            kp=self.kp,
            kd=self.kd,
        )

        if self.output_limit is not None:
            tau = symmetric_clip(tau, self.output_limit)

        command = TorqueCommand(
            torques=tau,
            joint_names=robot_state.joint_state.joint_names,
            timestamp=reference.time_from_start,
        )

        return ControlOutput(
            torque_command=command,
            status="ok",
            message="PD joint control output computed.",
            timestamp=reference.time_from_start,
        )
