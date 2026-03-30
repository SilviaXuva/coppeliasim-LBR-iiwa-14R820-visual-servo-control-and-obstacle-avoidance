from __future__ import annotations

import numpy as np

from manipulator_framework.adapters.ros2.converters.from_ros_msgs import (
    joint_command_from_ros_dict,
    torque_command_from_ros_dict,
)
from manipulator_framework.adapters.ros2.converters.to_ros_msgs import (
    camera_frame_to_ros_dict,
    person_detection_to_ros_dict,
    robot_state_to_ros_dict,
)
from manipulator_framework.core.types import (
    CameraFrame,
    Detection2D,
    JointState,
    PersonDetection,
    Pose3D,
    RobotState,
)


def test_joint_command_from_ros_dict_converts_positions_payload() -> None:
    payload = {
        "values": [0.1, 0.2, 0.3],
        "joint_names": ["j1", "j2", "j3"],
        "timestamp": 1.5,
        "mode": "position",
    }

    command = joint_command_from_ros_dict(payload)

    assert command.joint_names == ("j1", "j2", "j3")
    assert np.allclose(command.values, [0.1, 0.2, 0.3])
    assert command.timestamp == 1.5


def test_torque_command_from_ros_dict_converts_torque_payload() -> None:
    payload = {
        "torques": [1.0, 2.0],
        "joint_names": ["j1", "j2"],
        "timestamp": 0.5,
    }

    command = torque_command_from_ros_dict(payload)

    assert command.joint_names == ("j1", "j2")
    assert np.allclose(command.torques, [1.0, 2.0])
    assert command.timestamp == 0.5


def test_robot_state_to_ros_dict_serializes_internal_state() -> None:
    state = RobotState(
        joint_state=JointState(
            positions=np.array([0.1, 0.2], dtype=float),
            velocities=np.array([0.01, 0.02], dtype=float),
            joint_names=("j1", "j2"),
            timestamp=2.0,
        ),
        end_effector_pose=Pose3D(
            position=np.array([0.4, 0.5, 0.6], dtype=float),
            orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0], dtype=float),
            timestamp=2.0,
        ),
        timestamp=2.0,
    )

    payload = robot_state_to_ros_dict(state)

    assert payload["joint_state"]["positions"] == [0.1, 0.2]
    assert payload["joint_state"]["velocities"] == [0.01, 0.02]
    assert payload["end_effector_pose"]["position"] == [0.4, 0.5, 0.6]
    assert payload["timestamp"] == 2.0


def test_camera_frame_to_ros_dict_serializes_image_and_calibration() -> None:
    frame = CameraFrame(
        image=np.zeros((4, 5, 3), dtype=np.uint8),
        camera_id="cam_01",
        frame_id="camera",
        timestamp=3.0,
        intrinsics=np.eye(3, dtype=float),
    )

    payload = camera_frame_to_ros_dict(frame)

    assert payload["camera_id"] == "cam_01"
    assert payload["frame_id"] == "camera"
    assert payload["timestamp"] == 3.0
    assert payload["encoding"] == "rgb8"
    assert payload["shape"] == [4, 5, 3]


def test_person_detection_to_ros_dict_serializes_detection() -> None:
    detection = PersonDetection(
        detection=Detection2D(
            bbox_xyxy=(10.0, 20.0, 30.0, 40.0),
            confidence=0.9,
            class_id=0,
            class_name="person",
            image_size_wh=(640, 480),
            timestamp=4.0,
        ),
        keypoints_uv=((11.0, 21.0), (12.0, 22.0)),
        person_id_hint="track_01",
        timestamp=4.0,
    )

    payload = person_detection_to_ros_dict(detection)

    assert payload["detection"]["class_name"] == "person"
    assert payload["detection"]["bbox_xyxy"] == [10.0, 20.0, 30.0, 40.0]
    assert payload["person_id_hint"] == "track_01"
    assert payload["keypoints_uv"] == [[11.0, 21.0], [12.0, 22.0]]
