from __future__ import annotations

from manipulator_framework.adapters.ros2.nodes.robot_state_node import RobotStateNode


class FakeBridge:
    def read_robot_state_message(self) -> dict:
        return {"kind": "robot_state", "timestamp": 1.0}


def test_robot_state_node_only_delegates_to_bridge() -> None:
    node = RobotStateNode(bridge=FakeBridge())

    payload = node.publish_once()

    assert payload == {"kind": "robot_state", "timestamp": 1.0}
