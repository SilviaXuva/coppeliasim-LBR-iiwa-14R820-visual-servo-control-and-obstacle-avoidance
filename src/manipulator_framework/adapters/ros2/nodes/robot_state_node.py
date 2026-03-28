from __future__ import annotations

from manipulator_framework.adapters.ros2.bridges.robot_bridge import ROS2RobotBridge


class RobotStateNode:
    """
    Thin ROS 2 node placeholder.

    Real rclpy integration must remain here, not in core/application.
    """

    def __init__(self, bridge: ROS2RobotBridge) -> None:
        self._bridge = bridge

    def publish_once(self) -> dict:
        """Placeholder method for publishing one robot state sample."""
        return self._bridge.read_robot_state_message()
