from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from manipulator_framework.core.contracts import RobotInterface
from manipulator_framework.core.types import (
    JointCommand,
    JointState,
    Pose3D,
    RobotState,
    TorqueCommand,
)


@dataclass
class PyPlotRobotAdapter(RobotInterface):
    backend: Any
    joint_names: tuple[str, ...]

    def get_robot_state(self) -> RobotState:
        positions = np.asarray(self.backend.current_joint_positions(), dtype=float)
        velocities = np.asarray(self.backend.current_joint_velocities(), dtype=float)

        joint_state = JointState(
            positions=positions,
            velocities=velocities,
            joint_names=self.joint_names,
            timestamp=self.backend.current_time(),
        )
        return RobotState(
            joint_state=joint_state,
            timestamp=joint_state.timestamp,
        )

    def send_joint_command(self, command: JointCommand) -> None:
        self.backend.apply_joint_command(np.asarray(command.values, dtype=float))

    def send_torque_command(self, command: TorqueCommand) -> None:
        self.backend.apply_torque_command(np.asarray(command.values, dtype=float))

    def get_end_effector_pose(self) -> Pose3D:
        position, quat = self.backend.current_end_effector_pose()
        return Pose3D(
            position=np.asarray(position, dtype=float),
            orientation_quat_xyzw=np.asarray(quat, dtype=float),
            frame_id="world",
            child_frame_id="tool0",
            timestamp=self.backend.current_time(),
        )
