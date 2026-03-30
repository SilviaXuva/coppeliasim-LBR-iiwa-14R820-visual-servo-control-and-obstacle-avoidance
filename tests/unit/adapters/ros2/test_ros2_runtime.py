from __future__ import annotations

import numpy as np

from manipulator_framework.adapters.ros2.bridges.camera_bridge import ROS2CameraBridge
from manipulator_framework.adapters.ros2.bridges.command_bridge import ROS2CommandBridge
from manipulator_framework.adapters.ros2.bridges.detection_bridge import ROS2DetectionBridge
from manipulator_framework.adapters.ros2.bridges.robot_bridge import ROS2RobotBridge
from manipulator_framework.adapters.ros2.nodes.command_node import CommandNode
from manipulator_framework.adapters.ros2.nodes.perception_node import PerceptionNode
from manipulator_framework.adapters.ros2.nodes.robot_state_node import RobotStateNode
from manipulator_framework.adapters.ros2.runtime import ROS2Runtime
from manipulator_framework.core.types import (
    CameraFrame,
    Detection2D,
    JointState,
    PersonDetection,
    Pose3D,
    RobotState,
)


class FakeRobot:
    def __init__(self) -> None:
        self.last_joint_command = None
        self.last_torque_command = None

    def get_robot_state(self) -> RobotState:
        return RobotState(
            joint_state=JointState(
                positions=np.array([0.1, 0.2], dtype=float),
                velocities=np.array([0.01, 0.02], dtype=float),
                joint_names=("j1", "j2"),
                timestamp=1.0,
            ),
            end_effector_pose=Pose3D(
                position=np.array([0.3, 0.4, 0.5], dtype=float),
                orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0], dtype=float),
                timestamp=1.0,
            ),
            timestamp=1.0,
        )

    def send_joint_command(self, command) -> None:
        self.last_joint_command = command

    def send_torque_command(self, command) -> None:
        self.last_torque_command = command

    def get_end_effector_pose(self) -> Pose3D:
        return Pose3D(
            position=np.array([0.3, 0.4, 0.5], dtype=float),
            orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0], dtype=float),
            timestamp=1.0,
        )


class FakeCamera:
    def get_frame(self) -> CameraFrame:
        return CameraFrame(
            image=np.zeros((8, 8, 3), dtype=np.uint8),
            camera_id="cam_01",
            frame_id="camera",
            timestamp=2.0,
            intrinsics=np.eye(3, dtype=float),
        )

    def get_intrinsics(self):
        return np.eye(3, dtype=float)

    def get_extrinsics(self):
        return None


class FakePersonDetector:
    def detect_people(self, frame: CameraFrame) -> list[PersonDetection]:
        return [
            PersonDetection(
                detection=Detection2D(
                    bbox_xyxy=(1.0, 2.0, 3.0, 4.0),
                    confidence=0.9,
                    class_id=0,
                    class_name="person",
                    image_size_wh=(8, 8),
                    timestamp=frame.timestamp,
                ),
                keypoints_uv=((1.0, 2.0),),
                person_id_hint="track_01",
                timestamp=frame.timestamp,
            )
        ]


def test_ros2_runtime_publishes_state_camera_and_detections_and_receives_commands() -> None:
    robot = FakeRobot()
    camera = FakeCamera()
    detector = FakePersonDetector()

    runtime = ROS2Runtime(
        robot_state_node=RobotStateNode(ROS2RobotBridge(robot)),
        perception_node=PerceptionNode(
            camera_bridge=ROS2CameraBridge(camera),
            detection_bridge=ROS2DetectionBridge(camera=camera, person_detector=detector),
        ),
        command_node=CommandNode(ROS2CommandBridge(robot)),
        max_cycles=1,
    )

    outputs = runtime.spin()

    assert outputs["robot_state"]["joint_state"]["positions"] == [0.1, 0.2]
    assert outputs["camera_frame"]["camera_id"] == "cam_01"
    assert outputs["person_detections"][0]["detection"]["class_name"] == "person"

    runtime.command_node.receive_joint_command_once(
        {
            "values": [0.5, 0.6],
            "joint_names": ["j1", "j2"],
            "timestamp": 3.0,
            "mode": "position",
        }
    )
    runtime.command_node.receive_torque_command_once(
        {
            "torques": [1.5, 1.6],
            "joint_names": ["j1", "j2"],
            "timestamp": 4.0,
        }
    )

    assert np.allclose(robot.last_joint_command.values, [0.5, 0.6])
    assert np.allclose(robot.last_torque_command.torques, [1.5, 1.6])
