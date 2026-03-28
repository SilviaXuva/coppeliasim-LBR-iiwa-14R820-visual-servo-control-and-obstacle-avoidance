from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.adapters.simulation.coppeliasim.camera_adapter import CoppeliaSimCameraAdapter
from manipulator_framework.adapters.simulation.coppeliasim.robot_adapter import CoppeliaSimRobotAdapter
from manipulator_framework.adapters.simulation.coppeliasim.simulator_adapter import CoppeliaSimSimulatorAdapter


@dataclass
class SimulationComposer:
    """
    Composition root for simulation adapters.
    """
    sim_client: object

    def build_coppeliasim_robot(self, robot_handle: object, joint_names: tuple[str, ...]) -> CoppeliaSimRobotAdapter:
        return CoppeliaSimRobotAdapter(
            sim_client=self.sim_client,
            robot_handle=robot_handle,
            joint_names=joint_names,
        )

    def build_coppeliasim_camera(self, camera_handle: object) -> CoppeliaSimCameraAdapter:
        return CoppeliaSimCameraAdapter(
            sim_client=self.sim_client,
            camera_handle=camera_handle,
        )

    def build_coppeliasim_simulator(self) -> CoppeliaSimSimulatorAdapter:
        return CoppeliaSimSimulatorAdapter(sim_client=self.sim_client)
