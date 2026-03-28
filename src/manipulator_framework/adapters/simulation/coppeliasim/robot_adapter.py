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
class CoppeliaSimRobotAdapter(RobotInterface):
    sim_client: Any
    robot_handle: Any
    joint_names: tuple[str, ...]

    def get_robot_state(self) -> RobotState:
        positions = np.asarray(
            [self._read_joint_position(name) for name in self.joint_names],
            dtype=float,
        )
        velocities = np.asarray(
            [self._read_joint_velocity(name) for name in self.joint_names],
            dtype=float,
        )

        joint_state = JointState(
            positions=positions,
            velocities=velocities,
            joint_names=self.joint_names,
            timestamp=self._read_time(),
        )
        return RobotState(
            joint_state=joint_state,
            timestamp=joint_state.timestamp,
        )

    def send_joint_command(self, command: JointCommand) -> None:
        for joint_name, value in zip(command.joint_names, command.values):
            self._write_joint_target(joint_name, float(value))

    def send_torque_command(self, command: TorqueCommand) -> None:
        for joint_name, value in zip(command.joint_names, command.values):
            self._write_joint_torque(joint_name, float(value))

    def get_end_effector_pose(self) -> Pose3D:
        position = np.asarray(self._read_end_effector_position(), dtype=float)
        orientation = np.asarray(self._read_end_effector_quaternion(), dtype=float)

        return Pose3D(
            position=position,
            orientation_quat_xyzw=orientation,
            frame_id="world",
            child_frame_id="tool0",
            timestamp=self._read_time(),
        )

    def _read_joint_position(self, joint_name: str) -> float:
        raise NotImplementedError

    def _read_joint_velocity(self, joint_name: str) -> float:
        raise NotImplementedError

    def _write_joint_target(self, joint_name: str, value: float) -> None:
        raise NotImplementedError

    def _write_joint_torque(self, joint_name: str, value: float) -> None:
        raise NotImplementedError

    def _read_end_effector_position(self) -> list[float]:
        raise NotImplementedError

    def _read_end_effector_quaternion(self) -> list[float]:
        raise NotImplementedError

    def _read_time(self) -> float:
        raise NotImplementedError
