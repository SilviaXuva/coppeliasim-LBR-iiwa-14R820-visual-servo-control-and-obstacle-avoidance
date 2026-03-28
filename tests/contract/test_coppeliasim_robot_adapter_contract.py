from __future__ import annotations

from manipulator_framework.adapters.simulation.coppeliasim.robot_adapter import CoppeliaSimRobotAdapter
from manipulator_framework.core.contracts import RobotInterface


def test_coppeliasim_robot_adapter_implements_robot_interface() -> None:
    adapter = CoppeliaSimRobotAdapter(
        sim_client=object(),
        robot_handle=object(),
        joint_names=tuple(f"joint_{i+1}" for i in range(7)),
    )

    assert isinstance(adapter, RobotInterface)
