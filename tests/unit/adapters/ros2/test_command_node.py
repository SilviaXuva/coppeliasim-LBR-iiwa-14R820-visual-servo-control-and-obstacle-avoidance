from __future__ import annotations

from manipulator_framework.adapters.ros2.nodes.command_node import CommandNode


class FakeBridge:
    def __init__(self) -> None:
        self.payload = None

    def handle_command_message(self, payload: dict) -> None:
        self.payload = payload


def test_command_node_only_delegates_to_bridge() -> None:
    bridge = FakeBridge()
    node = CommandNode(bridge=bridge)

    payload = {"positions": [1.0, 2.0]}
    node.receive_once(payload)

    assert bridge.payload == payload
