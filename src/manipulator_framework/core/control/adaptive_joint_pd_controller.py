from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np

from manipulator_framework.core.types import ControlOutput, RobotState, TorqueCommand, TrajectorySample
from .base import BaseJointController
from .control_laws import compute_adaptive_pd_control
from .errors import compute_joint_tracking_error
from .interfaces import JointControllerInterface
from .saturation import symmetric_clip


@dataclass
class AdaptiveJointSpacePDController(BaseJointController, JointControllerInterface):
    """
    Pure adaptive PD controller.

    Placeholder policy:
        The adaptive term is intentionally minimal here. It provides a clean
        stateful contract and a numerically testable structure without assuming
        the final adaptation law from later research iterations.
    """
    kp: np.ndarray = field(default_factory=lambda: np.ones(7, dtype=float))
    kd: np.ndarray = field(default_factory=lambda: np.ones(7, dtype=float))
    adaptation_gain: np.ndarray = field(default_factory=lambda: 0.1 * np.ones(7, dtype=float))
    bias_limit: np.ndarray | float | None = None
    _adaptive_bias: np.ndarray = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.kp = np.asarray(self.kp, dtype=float).reshape(self.dof)
        self.kd = np.asarray(self.kd, dtype=float).reshape(self.dof)
        self.adaptation_gain = np.asarray(self.adaptation_gain, dtype=float).reshape(self.dof)
        self._adaptive_bias = np.zeros(self.dof, dtype=float)

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

        # Explicit placeholder adaptation law:
        # accumulates a bias proportional to position error.
        self._adaptive_bias = self._adaptive_bias + self.adaptation_gain * error.position_error * dt

        if self.bias_limit is not None:
            self._adaptive_bias = symmetric_clip(self._adaptive_bias, self.bias_limit)

        tau = compute_adaptive_pd_control(
            position_error=error.position_error,
            velocity_error=error.velocity_error,
            kp=self.kp,
            kd=self.kd,
            adaptive_bias=self._adaptive_bias,
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
            message="Adaptive PD joint control output computed.",
            timestamp=reference.time_from_start,
        )

    def reset(self) -> None:
        self._adaptive_bias = np.zeros(self.dof, dtype=float)
