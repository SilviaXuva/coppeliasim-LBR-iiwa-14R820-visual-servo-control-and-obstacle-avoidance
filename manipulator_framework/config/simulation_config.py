from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ._parsing import parse_optional_string, parse_string_sequence, resolve_optional_path
from .robot_config import (
    DEFAULT_JOINTS_COUNT,
    DEFAULT_JOINTS_PREFIX,
    DEFAULT_ROBOT_PATH,
    DEFAULT_TIP_PATH,
    parse_robot_config,
)
from .vision_config import (
    DEFAULT_CAMERA_SENSOR_PATH,
    default_camera_frame_rotation,
    parse_vision_config,
)


def default_scene_path() -> str | None:
    repo_root = Path(__file__).resolve().parents[2]
    candidates = (
        repo_root / "scenes" / "4.Vision-based.ttt",
        repo_root.parent / "scenes" / "4.Vision-based.ttt",
    )
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


@dataclass(slots=True)
class CoppeliaConfig:
    host: str = "localhost"
    port: int = 23000
    scene_path: str | None = field(default_factory=default_scene_path)
    robot_path: str = DEFAULT_ROBOT_PATH
    joints_count: int = DEFAULT_JOINTS_COUNT
    joints_prefix: str = DEFAULT_JOINTS_PREFIX
    tip_path: str = DEFAULT_TIP_PATH
    gripper_joints_paths: tuple[str, ...] = ("./active1", "./active2")
    gripper_proximity_sensor_path: str | None = "./attachProxSensor"
    gripper_attach_path: str | None = "./attachPoint"
    grasp_object_path: str | None = None
    tracked_object_path: str | None = None
    camera_sensor_path: str = DEFAULT_CAMERA_SENSOR_PATH
    camera_distortion_coefficients: tuple[float, ...] = ()
    camera_frame_rotation: tuple[tuple[float, ...], ...] | None = field(
        default_factory=default_camera_frame_rotation
    )


def parse_coppelia_config(
    coppelia_data: Mapping[str, Any],
    *,
    base_dir: Path | None = None,
) -> CoppeliaConfig:
    robot = parse_robot_config(coppelia_data)
    vision = parse_vision_config(coppelia_data)
    return CoppeliaConfig(
        host=str(coppelia_data.get("host", "localhost")),
        port=int(coppelia_data.get("port", 23000)),
        scene_path=resolve_optional_path(
            coppelia_data.get("scene_path", default_scene_path()),
            base_dir=base_dir,
        ),
        robot_path=robot.robot_path,
        joints_count=robot.joints_count,
        joints_prefix=robot.joints_prefix,
        tip_path=robot.tip_path,
        gripper_joints_paths=parse_string_sequence(
            coppelia_data.get("gripper_joints_paths", ("./active1", "./active2")),
            "gripper_joints_paths",
        ),
        gripper_proximity_sensor_path=parse_optional_string(
            coppelia_data.get("gripper_proximity_sensor_path", "./attachProxSensor")
        ),
        gripper_attach_path=parse_optional_string(
            coppelia_data.get("gripper_attach_path", "./attachPoint")
        ),
        grasp_object_path=parse_optional_string(
            coppelia_data.get("grasp_object_path")
        ),
        tracked_object_path=parse_optional_string(
            coppelia_data.get("tracked_object_path")
        ),
        camera_sensor_path=vision.camera_sensor_path,
        camera_distortion_coefficients=vision.camera_distortion_coefficients,
        camera_frame_rotation=vision.camera_frame_rotation,
    )
