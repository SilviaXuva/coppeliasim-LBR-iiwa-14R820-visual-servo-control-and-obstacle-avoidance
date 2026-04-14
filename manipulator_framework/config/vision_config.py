from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

DEFAULT_CAMERA_SENSOR_PATH = "./camera1"


def default_camera_frame_rotation() -> tuple[tuple[float, ...], ...]:
    # Legacy-compatible frame correction used for ArUco pose estimation in Coppelia.
    # Equivalent to a +180deg yaw rotation in the camera frame.
    return (
        (-1.0, 0.0, 0.0, 0.0),
        (0.0, -1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )


@dataclass(slots=True)
class VisionConfig:
    camera_sensor_path: str = DEFAULT_CAMERA_SENSOR_PATH
    camera_distortion_coefficients: tuple[float, ...] = ()
    camera_frame_rotation: tuple[tuple[float, ...], ...] | None = field(
        default_factory=default_camera_frame_rotation
    )


def parse_vision_config(coppelia_data: Mapping[str, Any]) -> VisionConfig:
    nested_data = coppelia_data.get("vision", {})
    if not isinstance(nested_data, Mapping):
        nested_data = {}

    distortion_data = coppelia_data.get(
        "camera_distortion_coefficients",
        nested_data.get("camera_distortion_coefficients", ()),
    )
    camera_distortion = tuple(float(value) for value in distortion_data)
    return VisionConfig(
        camera_sensor_path=str(
            coppelia_data.get(
                "camera_sensor_path",
                nested_data.get("camera_sensor_path", DEFAULT_CAMERA_SENSOR_PATH),
            )
        ),
        camera_distortion_coefficients=camera_distortion,
        # Fixed for pick-and-place to preserve legacy camera frame convention.
        camera_frame_rotation=default_camera_frame_rotation(),
    )
