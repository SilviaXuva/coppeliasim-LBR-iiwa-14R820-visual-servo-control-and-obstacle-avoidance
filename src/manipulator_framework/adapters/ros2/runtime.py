from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ROS2Runtime:
    """
    Minimal ROS 2-facing runtime coordinator.

    This class intentionally does not depend on rclpy. It coordinates thin nodes
    and keeps ROS-specific transport concerns outside the core/application layers.
    """
    robot_state_node: object | None = None
    perception_node: object | None = None
    command_node: object | None = None
    max_cycles: int = 1

    def spin(self, num_cycles: int | None = None) -> dict:
        cycles = int(num_cycles if num_cycles is not None else self.max_cycles)
        if cycles <= 0:
            raise ValueError("num_cycles must be positive.")

        last_outputs: dict[str, object] = {
            "robot_state": None,
            "camera_frame": None,
            "person_detections": None,
        }

        for _ in range(cycles):
            if self.robot_state_node is not None:
                last_outputs["robot_state"] = self.robot_state_node.publish_once()

            if self.perception_node is not None:
                last_outputs["camera_frame"] = self.perception_node.publish_camera_once()
                last_outputs["person_detections"] = self.perception_node.publish_people_once()

        return last_outputs
