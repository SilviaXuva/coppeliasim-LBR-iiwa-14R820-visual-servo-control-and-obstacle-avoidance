from __future__ import annotations

from manipulator_framework.adapters.ros2.nodes.perception_node import PerceptionNode


class FakeBridge:
    def read_camera_frame_message(self) -> dict:
        return {"kind": "camera_frame", "timestamp": 3.0}


def test_perception_node_only_delegates_to_bridge() -> None:
    node = PerceptionNode(bridge=FakeBridge())

    payload = node.publish_once()

    assert payload == {"kind": "camera_frame", "timestamp": 3.0}
