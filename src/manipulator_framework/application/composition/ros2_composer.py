from __future__ import annotations


class ROS2Runtime:
    def spin(self) -> None:
        return None


class ROS2Composer:
    def __init__(self, config: dict) -> None:
        self._config = config

    def build_ros2_runtime(self) -> ROS2Runtime:
        return ROS2Runtime()
