from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from manipulator_framework.adapters.ros2.bridges import (
    ROS2CameraBridge,
    ROS2CommandBridge,
    ROS2DetectionBridge,
    ROS2RobotBridge,
)
from manipulator_framework.adapters.ros2.nodes import CommandNode, PerceptionNode, RobotStateNode
from manipulator_framework.adapters.ros2.runtime import ROS2Runtime
from manipulator_framework.core.types import (
    CameraFrame,
    Detection2D,
    JointState,
    PersonDetection,
    Pose3D,
    RobotState,
)


class _NullRobot:
    def get_robot_state(self) -> RobotState:
        return RobotState(
            joint_state=JointState(
                positions=np.zeros(7, dtype=float),
                velocities=np.zeros(7, dtype=float),
                joint_names=tuple(f"joint_{index + 1}" for index in range(7)),
                timestamp=0.0,
            ),
            end_effector_pose=Pose3D(
                position=np.zeros(3, dtype=float),
                orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0], dtype=float),
                timestamp=0.0,
            ),
            timestamp=0.0,
        )

    def send_joint_command(self, command) -> None:
        return None

    def send_torque_command(self, command) -> None:
        return None

    def get_end_effector_pose(self) -> Pose3D:
        return Pose3D(
            position=np.zeros(3, dtype=float),
            orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0], dtype=float),
            timestamp=0.0,
        )


class _NullCamera:
    def get_frame(self) -> CameraFrame:
        return CameraFrame(
            image=np.zeros((32, 32, 3), dtype=np.uint8),
            camera_id="ros2_stub_camera",
            frame_id="camera",
            timestamp=0.0,
            intrinsics=np.eye(3, dtype=float),
        )

    def get_intrinsics(self):
        return np.eye(3, dtype=float)

    def get_extrinsics(self):
        return None


class _NullPersonDetector:
    def detect_people(self, frame: CameraFrame) -> list[PersonDetection]:
        return [
            PersonDetection(
                detection=Detection2D(
                    bbox_xyxy=(8.0, 8.0, 24.0, 24.0),
                    confidence=1.0,
                    class_id=0,
                    class_name="person",
                    image_size_wh=(int(frame.image.shape[1]), int(frame.image.shape[0])),
                    timestamp=frame.timestamp,
                ),
                keypoints_uv=(),
                person_id_hint="stub_person",
                timestamp=frame.timestamp,
            )
        ]


@dataclass
class ROS2Composer:
    """
    Minimal ROS 2 composition root.

    This stage only closes the ROS 2 boundary with thin nodes and converters.
    Full deployment/runtime integration with rclpy remains future work.
    """
    config: dict
    robot: object | None = None
    camera: object | None = None
    person_detector: object | None = None

    def build_ros2_runtime(self) -> ROS2Runtime:
        robot = self.robot or _NullRobot()
        camera = self.camera or _NullCamera()
        person_detector = self.person_detector or _NullPersonDetector()

        robot_state_node = RobotStateNode(
            bridge=ROS2RobotBridge(robot),
        )
        command_node = CommandNode(
            bridge=ROS2CommandBridge(robot),
        )
        perception_node = PerceptionNode(
            camera_bridge=ROS2CameraBridge(camera),
            detection_bridge=ROS2DetectionBridge(
                camera=camera,
                person_detector=person_detector,
            ),
        )

        max_cycles = int(self.config.get("runtime", {}).get("max_steps", 1))
        return ROS2Runtime(
            robot_state_node=robot_state_node,
            perception_node=perception_node,
            command_node=command_node,
            max_cycles=max_cycles,
        )
