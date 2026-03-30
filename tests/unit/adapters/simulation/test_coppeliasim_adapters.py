from __future__ import annotations

import numpy as np

from manipulator_framework.adapters.simulation.coppeliasim.camera_adapter import (
    CoppeliaSimCameraAdapter,
)
from manipulator_framework.adapters.simulation.coppeliasim.robot_adapter import (
    CoppeliaSimRobotAdapter,
)
from manipulator_framework.adapters.simulation.coppeliasim.simulator_adapter import (
    CoppeliaSimSimulatorAdapter,
)
from manipulator_framework.core.types import JointCommand, TorqueCommand
from manipulator_framework.core.types.enums import CommandMode


class FakeCoppeliaSimClient:
    def __init__(self) -> None:
        self.started = False
        self.stepped = False
        self.stopped = False
        self.targets: list[tuple[str, float]] = []
        self.torques: list[tuple[str, float]] = []

    def get_joint_position(self, robot_handle, joint_name: str) -> float:
        return {
            "joint_1": 0.1,
            "joint_2": 0.2,
            "joint_3": 0.3,
        }[joint_name]

    def get_joint_velocity(self, robot_handle, joint_name: str) -> float:
        return {
            "joint_1": 0.01,
            "joint_2": 0.02,
            "joint_3": 0.03,
        }[joint_name]

    def set_joint_target_position(self, robot_handle, joint_name: str, value: float) -> None:
        self.targets.append((joint_name, value))

    def set_joint_torque(self, robot_handle, joint_name: str, value: float) -> None:
        self.torques.append((joint_name, value))

    def get_object_position(self, handle, reference_frame: str = "world") -> list[float]:
        return [0.5, 0.1, 0.2]

    def get_object_quaternion(self, handle, reference_frame: str = "world") -> list[float]:
        return [0.0, 0.0, 0.0, 1.0]

    def get_sim_time(self) -> float:
        return 1.25

    def get_camera_rgb(self, camera_handle):
        return np.zeros((16, 16, 3), dtype=np.uint8)

    def get_camera_depth(self, camera_handle):
        return np.ones((16, 16), dtype=float)

    def get_camera_intrinsics(self, camera_handle):
        return np.eye(3, dtype=float)

    def get_camera_extrinsics(self, camera_handle):
        return {
            "position": [0.0, 0.0, 1.0],
            "orientation_quat_xyzw": [0.0, 0.0, 0.0, 1.0],
            "frame_id": "world",
            "child_frame_id": "camera",
            "timestamp": 1.25,
        }

    def start_simulation(self) -> None:
        self.started = True

    def step_simulation(self) -> None:
        self.stepped = True

    def stop_simulation(self) -> None:
        self.stopped = True


def test_coppeliasim_robot_adapter_reads_state_and_commands() -> None:
    client = FakeCoppeliaSimClient()
    adapter = CoppeliaSimRobotAdapter(
        sim_client=client,
        robot_handle="robot",
        joint_names=("joint_1", "joint_2", "joint_3"),
    )

    state = adapter.get_robot_state()

    assert np.allclose(state.joint_state.positions, [0.1, 0.2, 0.3])
    assert np.allclose(state.joint_state.velocities, [0.01, 0.02, 0.03])
    assert state.timestamp == 1.25

    adapter.send_joint_command(
        JointCommand(
            values=np.array([1.0, 1.1, 1.2], dtype=float),
            mode=CommandMode.POSITION,
            joint_names=("joint_1", "joint_2", "joint_3"),
        )
    )
    adapter.send_torque_command(
        TorqueCommand(
            torques=np.array([0.5, 0.6, 0.7], dtype=float),
            joint_names=("joint_1", "joint_2", "joint_3"),
        )
    )

    assert client.targets == [
        ("joint_1", 1.0),
        ("joint_2", 1.1),
        ("joint_3", 1.2),
    ]
    assert client.torques == [
        ("joint_1", 0.5),
        ("joint_2", 0.6),
        ("joint_3", 0.7),
    ]


def test_coppeliasim_camera_adapter_reads_frame() -> None:
    client = FakeCoppeliaSimClient()
    adapter = CoppeliaSimCameraAdapter(
        sim_client=client,
        camera_handle="camera",
        camera_id="sim_camera",
        frame_id="camera",
    )

    frame = adapter.get_frame()

    assert frame.image.shape == (16, 16, 3)
    assert frame.camera_id == "sim_camera"
    assert frame.frame_id == "camera"
    assert frame.timestamp == 1.25
    assert frame.intrinsics.shape == (3, 3)
    assert frame.extrinsics is not None
    assert np.allclose(frame.extrinsics.position, [0.0, 0.0, 1.0])


def test_coppeliasim_simulator_adapter_controls_lifecycle() -> None:
    client = FakeCoppeliaSimClient()
    adapter = CoppeliaSimSimulatorAdapter(sim_client=client)

    adapter.start()
    adapter.step()
    adapter.stop()

    assert client.started is True
    assert client.stepped is True
    assert client.stopped is True
