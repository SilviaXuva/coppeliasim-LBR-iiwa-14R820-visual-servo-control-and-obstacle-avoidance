from __future__ import annotations

from manipulator_framework.adapters.simulation.pyplot.robot_adapter import PyPlotRobotAdapter
from manipulator_framework.core.contracts import RobotInterface


class FakeBackend:
    def current_joint_positions(self):
        return [0.0] * 7

    def current_joint_velocities(self):
        return [0.0] * 7

    def current_time(self):
        return 0.0

    def current_end_effector_pose(self):
        return [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0]

    def apply_joint_command(self, command):
        return None

    def apply_torque_command(self, command):
        return None


def test_pyplot_robot_adapter_implements_robot_interface() -> None:
    adapter = PyPlotRobotAdapter(
        backend=FakeBackend(),
        joint_names=tuple(f"joint_{i+1}" for i in range(7)),
    )

    assert isinstance(adapter, RobotInterface)
