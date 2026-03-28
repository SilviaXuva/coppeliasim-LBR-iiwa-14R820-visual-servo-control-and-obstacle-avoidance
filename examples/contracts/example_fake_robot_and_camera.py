from __future__ import annotations

import numpy as np

from manipulator_framework.core.contracts import CameraInterface, RobotInterface
from manipulator_framework.core.types import (
    CameraFrame,
    CommandMode,
    JointCommand,
    JointState,
    Pose3D,
    RobotState,
    TorqueCommand,
)


class FakeRobot(RobotInterface):
    def __init__(self) -> None:
        self._state = RobotState(
            joint_state=JointState(
                positions=np.zeros(7),
                velocities=np.zeros(7),
                efforts=np.zeros(7),
                joint_names=tuple(f"joint_{i+1}" for i in range(7)),
                timestamp=0.0,
            ),
            end_effector_pose=Pose3D(
                position=np.array([0.5, 0.0, 0.7]),
                orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
                frame_id="world",
                child_frame_id="tool0",
                timestamp=0.0,
            ),
            timestamp=0.0,
        )

    def get_robot_state(self) -> RobotState:
        return self._state

    def send_joint_command(self, command: JointCommand) -> None:
        self._state = RobotState(
            joint_state=JointState(
                positions=command.values,
                velocities=np.zeros_like(command.values),
                efforts=np.zeros_like(command.values),
                joint_names=self._state.joint_state.joint_names,
                timestamp=command.timestamp,
            ),
            end_effector_pose=self._state.end_effector_pose,
            timestamp=command.timestamp,
        )

    def send_torque_command(self, command: TorqueCommand) -> None:
        # Explicit placeholder
        pass

    def get_end_effector_pose(self) -> Pose3D:
        if self._state.end_effector_pose is None:
            raise RuntimeError("End-effector pose not available.")
        return self._state.end_effector_pose


class FakeCamera(CameraInterface):
    def get_frame(self) -> CameraFrame:
        return CameraFrame(
            image=np.zeros((480, 640, 3), dtype=np.uint8),
            camera_id="fake_camera",
            frame_id="camera_frame",
            timestamp=1.0,
            intrinsics=self.get_intrinsics(),
            extrinsics=self.get_extrinsics(),
        )

    def get_intrinsics(self) -> np.ndarray:
        return np.array(
            [
                [600.0, 0.0, 320.0],
                [0.0, 600.0, 240.0],
                [0.0, 0.0, 1.0],
            ]
        )

    def get_extrinsics(self) -> Pose3D:
        return Pose3D(
            position=np.array([1.0, 0.0, 1.5]),
            orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
            frame_id="world",
            child_frame_id="camera_frame",
            timestamp=1.0,
        )


def main() -> None:
    robot = FakeRobot()
    camera = FakeCamera()

    print("Initial robot state:", robot.get_robot_state().to_dict())
    print("Camera frame shape:", camera.get_frame().image.shape)

    robot.send_joint_command(
        JointCommand(
            values=np.array([0.1, 0.0, -0.1, 0.2, 0.0, 0.1, 0.0]),
            mode=CommandMode.POSITION,
            timestamp=2.0,
        )
    )

    print("Updated robot state:", robot.get_robot_state().to_dict())


if __name__ == "__main__":
    main()
