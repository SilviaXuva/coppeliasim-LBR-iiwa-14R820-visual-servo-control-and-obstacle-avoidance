from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

DEFAULT_ROBOT_PATH = "./LBRiiwa14R820"
DEFAULT_JOINTS_COUNT = 7
DEFAULT_JOINTS_PREFIX = "./joint"
DEFAULT_TIP_PATH = "./tip"


@dataclass(slots=True)
class RobotConfig:
    robot_path: str = DEFAULT_ROBOT_PATH
    joints_count: int = DEFAULT_JOINTS_COUNT
    joints_prefix: str = DEFAULT_JOINTS_PREFIX
    tip_path: str = DEFAULT_TIP_PATH


def parse_robot_config(coppelia_data: Mapping[str, Any]) -> RobotConfig:
    nested_data = coppelia_data.get("robot", {})
    if not isinstance(nested_data, Mapping):
        nested_data = {}
    return RobotConfig(
        robot_path=str(
            coppelia_data.get(
                "robot_path",
                nested_data.get("robot_path", nested_data.get("path", DEFAULT_ROBOT_PATH)),
            )
        ),
        joints_count=int(
            coppelia_data.get(
                "joints_count",
                nested_data.get("joints_count", DEFAULT_JOINTS_COUNT),
            )
        ),
        joints_prefix=str(
            coppelia_data.get(
                "joints_prefix",
                nested_data.get("joints_prefix", DEFAULT_JOINTS_PREFIX),
            )
        ),
        tip_path=str(
            coppelia_data.get(
                "tip_path",
                nested_data.get("tip_path", DEFAULT_TIP_PATH),
            )
        ),
    )
