from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.adapters.ros2.bridges.camera_bridge import ROS2CameraBridge


@dataclass
class FakeCameraFrame:
    frame_id: str
    timestamp: float
    width: int
    height: int
    encoding: str


class FakeCamera:
    def capture(self) -> FakeCameraFrame:
        return FakeCameraFrame(
            frame_id="camera_1",
            timestamp=4.2,
            width=640,
            height=480,
            encoding="rgb8",
        )


def test_camera_bridge_reads_camera_and_converts() -> None:
    bridge = ROS2CameraBridge(camera=FakeCamera())

    payload = bridge.read_camera_frame_message()

    assert payload["frame_id"] == "camera_1"
    assert payload["timestamp"] == 4.2
    assert payload["width"] == 640
    assert payload["height"] == 480
    assert payload["encoding"] == "rgb8"
