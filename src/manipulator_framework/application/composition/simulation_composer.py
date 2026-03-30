from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from manipulator_framework.adapters.simulation.coppeliasim.camera_adapter import (
    CoppeliaSimCameraAdapter,
)
from manipulator_framework.adapters.simulation.coppeliasim.robot_adapter import (
    CoppeliaSimRobotAdapter,
)
from manipulator_framework.adapters.simulation.coppeliasim.simulator_adapter import (
    CoppeliaSimSimulatorAdapter,
)
from manipulator_framework.adapters.simulation.pyplot.robot_adapter import (
    PyPlotRobotAdapter,
)
from manipulator_framework.adapters.simulation.pyplot.simulator_adapter import (
    PyPlotSimulatorAdapter,
)


@dataclass
class SimulationComposer:
    """
    Composition root for simulation adapters.

    This stage only closes adapter construction. Full app/use-case composition
    remains part of D3.
    """

    sim_client: Any | None = None
    pyplot_backend: Any | None = None

    def build_coppeliasim_robot(
        self,
        robot_handle: object,
        joint_names: tuple[str, ...],
    ) -> CoppeliaSimRobotAdapter:
        if self.sim_client is None:
            raise ValueError("sim_client is required to build a CoppeliaSim robot adapter.")
        return CoppeliaSimRobotAdapter(
            sim_client=self.sim_client,
            robot_handle=robot_handle,
            joint_names=joint_names,
        )

    def build_coppeliasim_camera(self, camera_handle: object) -> CoppeliaSimCameraAdapter:
        if self.sim_client is None:
            raise ValueError("sim_client is required to build a CoppeliaSim camera adapter.")
        return CoppeliaSimCameraAdapter(
            sim_client=self.sim_client,
            camera_handle=camera_handle,
        )

    def build_coppeliasim_simulator(self) -> CoppeliaSimSimulatorAdapter:
        if self.sim_client is None:
            raise ValueError("sim_client is required to build a CoppeliaSim simulator adapter.")
        return CoppeliaSimSimulatorAdapter(sim_client=self.sim_client)

    def build_pyplot_robot(self, joint_names: tuple[str, ...]) -> PyPlotRobotAdapter:
        if self.pyplot_backend is None:
            raise ValueError("pyplot_backend is required to build a PyPlot robot adapter.")
        return PyPlotRobotAdapter(
            backend=self.pyplot_backend,
            joint_names=joint_names,
        )

    def build_pyplot_simulator(self) -> PyPlotSimulatorAdapter:
        if self.pyplot_backend is None:
            raise ValueError("pyplot_backend is required to build a PyPlot simulator adapter.")
        return PyPlotSimulatorAdapter(backend=self.pyplot_backend)
