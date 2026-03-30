from __future__ import annotations

import numpy as np

from manipulator_framework.adapters.simulation.pyplot.robot_adapter import (
    PyPlotRobotAdapter,
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
