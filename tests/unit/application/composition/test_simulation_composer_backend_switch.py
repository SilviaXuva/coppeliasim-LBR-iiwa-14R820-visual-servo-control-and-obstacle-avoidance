from __future__ import annotations

from manipulator_framework.adapters.simulation.coppeliasim.camera_adapter import (
    CoppeliaSimCameraAdapter,
)
from manipulator_framework.adapters.simulation.coppeliasim.obstacle_source import (
    CoppeliaSimObstacleSource,
)
from manipulator_framework.adapters.simulation.coppeliasim.robot_adapter import (
    CoppeliaSimRobotAdapter,
)
from manipulator_framework.adapters.simulation.coppeliasim.simulator_adapter import (
    CoppeliaSimSimulatorAdapter,
)
from manipulator_framework.adapters.simulation.pyplot.camera_adapter import PyPlotCameraAdapter
from manipulator_framework.adapters.simulation.pyplot.obstacle_source import PyPlotObstacleSource
from manipulator_framework.adapters.simulation.pyplot.robot_adapter import PyPlotRobotAdapter
from manipulator_framework.adapters.simulation.pyplot.simulator_adapter import (
    PyPlotSimulatorAdapter,
)
from manipulator_framework.application.composition.simulation_composer import SimulationComposer


def test_simulation_composer_uses_pyplot_adapters_when_configured() -> None:
    composer = SimulationComposer(
        config={
            "simulation": {
                "backend": "pyplot",
                "joint_names": ["j1", "j2", "j3"],
            },
            "runtime": {"dt": 0.02},
        }
    )

    assert isinstance(composer.build_robot(), PyPlotRobotAdapter)
    assert isinstance(composer.build_camera(), PyPlotCameraAdapter)
    assert isinstance(composer.build_simulator(), PyPlotSimulatorAdapter)
    assert isinstance(composer.build_obstacle_source(), PyPlotObstacleSource)


def test_simulation_composer_uses_coppeliasim_adapters_by_default() -> None:
    composer = SimulationComposer(
        config={
            "simulation": {
                "robot_handle": "robot",
                "camera_handle": "camera",
                "joint_names": ["j1", "j2", "j3"],
                "obstacle_handles": ["obs1"],
            }
        },
        sim_client=object(),
    )

    assert isinstance(composer.build_robot(), CoppeliaSimRobotAdapter)
    assert isinstance(composer.build_camera(), CoppeliaSimCameraAdapter)
    assert isinstance(composer.build_simulator(), CoppeliaSimSimulatorAdapter)
    assert isinstance(composer.build_obstacle_source(), CoppeliaSimObstacleSource)

