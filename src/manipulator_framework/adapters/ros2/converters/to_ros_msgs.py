from __future__ import annotations

from typing import Any

import numpy as np

from manipulator_framework.core.types import (
    CameraFrame,
    Detection2D,
    JointCommand,
    JointState,
    PersonDetection,
    Pose3D,
    RobotState,
    TorqueCommand,
)


def _to_list(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, tuple):
        return [_to_list(item) for item in value]
    if isinstance(value, list):
        return [_to_list(item) for item in value]
    return value


def pose3d_to_ros_dict(pose: Pose3D) -> dict[str, Any]:
    return {
        "position": _to_list(pose.position),
        "orientation_quat_xyzw": _to_list(pose.orientation_quat_xyzw),
        "frame_id": pose.frame_id,
        "child_frame_id": pose.child_frame_id,
        "timestamp": pose.timestamp,
    }


def joint_state_to_ros_dict(state: JointState) -> dict[str, Any]:
    return {
        "positions": _to_list(state.positions),
        "velocities": _to_list(state.velocities),
        "accelerations": _to_list(state.accelerations),
        "efforts": _to_list(state.efforts),
        "joint_names": list(state.joint_names),
        "timestamp": state.timestamp,
    }


def robot_state_to_ros_dict(state: RobotState) -> dict[str, Any]:
    # Support both full `RobotState` objects and simple data classes used in tests.
    if hasattr(state, "joint_state"):
        return {
            "joint_state": joint_state_to_ros_dict(state.joint_state),
            "end_effector_pose": (
                pose3d_to_ros_dict(state.end_effector_pose)
                if state.end_effector_pose is not None
                else None
            ),
            "is_ready": state.is_ready,
            "timestamp": state.timestamp,
        }

    # Fallback: flat structure with positions/velocities attributes.
    return {
        "joint_names": _to_list(getattr(state, "joint_names", ())),
        "positions": _to_list(getattr(state, "positions", None)),
        "velocities": _to_list(getattr(state, "velocities", None)),
        "timestamp": getattr(state, "timestamp", 0.0),
    }


def joint_command_to_ros_dict(command: JointCommand) -> dict[str, Any]:
    # Accept both internal `JointCommand` and lightweight test doubles.
    raw_positions = getattr(command, "values", None)
    if raw_positions is None:
        raw_positions = getattr(command, "positions", None)

    return {
        "values": _to_list(raw_positions),
        "positions": _to_list(raw_positions),
        "mode": getattr(command, "mode", None).value if hasattr(command, "mode") else "position",
        "joint_names": _to_list(getattr(command, "joint_names", ())),
        "timestamp": getattr(command, "timestamp", 0.0),
    }


def torque_command_to_ros_dict(command: TorqueCommand) -> dict[str, Any]:
    return {
        "torques": _to_list(command.torques),
        "joint_names": list(command.joint_names),
        "timestamp": command.timestamp,
    }


def camera_frame_to_ros_dict(frame: CameraFrame) -> dict[str, Any]:
    # If a full image is present, keep the original rich payload.
    if hasattr(frame, "image"):
        encoding = "mono8" if frame.image.ndim == 2 else "rgb8"
        return {
            "camera_id": getattr(frame, "camera_id", None),
            "frame_id": frame.frame_id,
            "timestamp": frame.timestamp,
            "encoding": encoding,
            "shape": list(frame.image.shape),
            "image": _to_list(frame.image),
            "intrinsics": _to_list(getattr(frame, "intrinsics", None)),
            "extrinsics": (
                pose3d_to_ros_dict(frame.extrinsics) if getattr(frame, "extrinsics", None) is not None else None
            ),
        }

    # Lightweight fallback used by unit tests.
    return {
        "frame_id": getattr(frame, "frame_id", None),
        "timestamp": getattr(frame, "timestamp", 0.0),
        "width": getattr(frame, "width", None),
        "height": getattr(frame, "height", None),
        "encoding": getattr(frame, "encoding", None),
    }


def detection2d_to_ros_dict(detection: Detection2D) -> dict[str, Any]:
    return {
        "bbox_xyxy": list(detection.bbox_xyxy),
        "confidence": detection.confidence,
        "class_id": detection.class_id,
        "class_name": detection.class_name,
        "image_size_wh": list(detection.image_size_wh) if detection.image_size_wh else None,
        "timestamp": detection.timestamp,
    }


def person_detection_to_ros_dict(detection: PersonDetection) -> dict[str, Any]:
    return {
        "detection": detection2d_to_ros_dict(detection.detection),
        "keypoints_uv": [list(item) for item in detection.keypoints_uv],
        "person_id_hint": detection.person_id_hint,
        "timestamp": detection.timestamp,
    }
