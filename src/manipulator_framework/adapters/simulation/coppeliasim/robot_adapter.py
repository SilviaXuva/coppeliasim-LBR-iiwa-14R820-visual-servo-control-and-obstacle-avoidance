from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

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
    """
    Minimal CoppeliaSim robot adapter.

    Expected sim_client API by convention:
    - get_joint_position(robot_handle, joint_name)
    - get_joint_velocity(robot_handle, joint_name)
    - set_joint_target_position(robot_handle, joint_name, value)
    - set_joint_torque(robot_handle, joint_name, value)
    - get_object_position(handle, reference_frame="world")
    - get_object_quaternion(handle, reference_frame="world")
    - get_sim_time()
    """

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
            end_effector_pose=self.get_end_effector_pose(),
            timestamp=joint_state.timestamp,
        )

    def send_joint_command(self, command: JointCommand) -> None:
        for joint_name, value in zip(command.joint_names, command.values):
            self._write_joint_target(joint_name, float(value))

    def send_torque_command(self, command: TorqueCommand) -> None:
        for joint_name, value in zip(command.joint_names, command.torques):
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
        return float(
            self._call_required(
                "get_joint_position",
                robot_handle=self.robot_handle,
                joint_name=joint_name,
            )
        )

    def _read_joint_velocity(self, joint_name: str) -> float:
        return float(
            self._call_required(
                "get_joint_velocity",
                robot_handle=self.robot_handle,
                joint_name=joint_name,
            )
        )

    def _write_joint_target(self, joint_name: str, value: float) -> None:
        self._call_required(
            "set_joint_target_position",
            robot_handle=self.robot_handle,
            joint_name=joint_name,
            value=value,
        )

    def _write_joint_torque(self, joint_name: str, value: float) -> None:
        self._call_required(
            "set_joint_torque",
            robot_handle=self.robot_handle,
            joint_name=joint_name,
            value=value,
        )

    def _read_end_effector_position(self) -> list[float]:
        position = self._call_required(
            "get_object_position",
            handle=self.robot_handle,
            reference_frame="world",
        )
        return list(position)

    def _read_end_effector_quaternion(self) -> list[float]:
        quaternion = self._call_required(
            "get_object_quaternion",
            handle=self.robot_handle,
            reference_frame="world",
        )
        return list(quaternion)

    def _read_time(self) -> float:
        return float(self._call_required("get_sim_time"))

    def _call_required(self, method_name: str, **kwargs: Any) -> Any:
        candidate = getattr(self.sim_client, method_name, None)
        if not callable(candidate):
            raise NotImplementedError(
                f"CoppeliaSim client must implement '{method_name}' for CoppeliaSimRobotAdapter."
            )
        return candidate(**kwargs)
