from __future__ import annotations

import numpy as np

from manipulator_framework.adapters.simulation.pyplot.robot_adapter import (
    PyPlotRobotAdapter,
)
from manipulator_framework.adapters.simulation.pyplot.camera_adapter import (
    PyPlotCameraAdapter,
)
from manipulator_framework.adapters.simulation.pyplot.obstacle_source import (
    PyPlotObstacleSource,
)
from manipulator_framework.adapters.simulation.pyplot.simulator_adapter import (
    PyPlotSimulatorAdapter,
)
from manipulator_framework.core.types import JointCommand, TorqueCommand
from manipulator_framework.core.types.enums import CommandMode


class FakePyPlotBackend:
    def __init__(self) -> None:
        self.started = False
        self.stepped = False
        self.stopped = False
        self.reset_called = False
        self.last_joint_command = None
        self.last_torque_command = None

    def current_joint_positions(self):
        return [0.0, 0.1, 0.2]

    def current_joint_velocities(self):
        return [0.01, 0.02, 0.03]

    def current_time(self):
        return 2.5

    def current_end_effector_pose(self):
        return [0.4, 0.0, 0.3], [0.0, 0.0, 0.0, 1.0]

    def apply_joint_command(self, command):
        self.last_joint_command = command

    def apply_torque_command(self, command):
        self.last_torque_command = command

    def start(self):
        self.started = True

    def step(self):
        self.stepped = True

    def stop(self):
        self.stopped = True

    def reset(self):
        self.reset_called = True

    def current_frame(self):
        return np.zeros((16, 16, 3), dtype=np.uint8)

    def current_camera_intrinsics(self):
        return np.eye(3, dtype=float)

    def current_camera_extrinsics(self):
        return {
            "position": [0.0, 0.0, 1.0],
            "orientation_quat_xyzw": [0.0, 0.0, 0.0, 1.0],
            "frame_id": "world",
            "child_frame_id": "camera",
            "timestamp": self.current_time(),
        }

    def current_obstacles(self):
        return [
            {
                "obstacle_id": "obs_1",
                "position": [0.3, 0.0, 0.5],
                "orientation_quat_xyzw": [0.0, 0.0, 0.0, 1.0],
                "radius": 0.2,
                "timestamp": self.current_time(),
            }
        ]


def test_pyplot_robot_adapter_reads_state_and_commands() -> None:
    backend = FakePyPlotBackend()
    adapter = PyPlotRobotAdapter(
        backend=backend,
        joint_names=("joint_1", "joint_2", "joint_3"),
    )

    state = adapter.get_robot_state()

    assert np.allclose(state.joint_state.positions, [0.0, 0.1, 0.2])
    assert np.allclose(state.joint_state.velocities, [0.01, 0.02, 0.03])
    assert state.timestamp == 2.5

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

    assert np.allclose(backend.last_joint_command, [1.0, 1.1, 1.2])
    assert np.allclose(backend.last_torque_command, [0.5, 0.6, 0.7])


def test_pyplot_simulator_adapter_controls_lifecycle() -> None:
    backend = FakePyPlotBackend()
    adapter = PyPlotSimulatorAdapter(backend=backend)

    adapter.start()
    adapter.step()
    adapter.stop()
    adapter.reset()

    assert backend.started is True
    assert backend.stepped is True
    assert backend.stopped is True
    assert backend.reset_called is True


def test_pyplot_camera_adapter_reads_frame() -> None:
    backend = FakePyPlotBackend()
    adapter = PyPlotCameraAdapter(
        backend=backend,
        camera_id="pyplot_cam",
        frame_id="camera",
    )

    frame = adapter.get_frame()

    assert frame.image.shape == (16, 16, 3)
    assert frame.camera_id == "pyplot_cam"
    assert frame.frame_id == "camera"
    assert frame.timestamp == 2.5
    assert frame.intrinsics.shape == (3, 3)
    assert frame.extrinsics is not None


def test_pyplot_obstacle_source_reads_obstacles() -> None:
    backend = FakePyPlotBackend()
    source = PyPlotObstacleSource(backend=backend)

    obstacles = source.get_obstacles()

    assert len(obstacles) == 1
    assert obstacles[0].obstacle_id == "obs_1"
    assert np.allclose(obstacles[0].pose.position, [0.3, 0.0, 0.5])
