from __future__ import annotations

from manipulator_framework.adapters.ros2.converters.to_ros_msgs import robot_state_to_ros_dict
from manipulator_framework.core.contracts.robot_interface import RobotInterface


class ROS2RobotBridge:
    """Bridge between RobotInterface and ROS transport."""

    def __init__(self, robot: RobotInterface) -> None:
        self._robot = robot

    def read_robot_state_message(self) -> dict:
        """Read internal robot state and convert it to a ROS-facing DTO."""
        state = self._robot.read_state()
        return robot_state_to_ros_dict(state)
