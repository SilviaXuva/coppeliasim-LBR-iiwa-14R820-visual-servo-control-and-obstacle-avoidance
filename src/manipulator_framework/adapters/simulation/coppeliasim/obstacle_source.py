from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import numpy as np

from manipulator_framework.core.contracts import ObstacleSourceInterface
from manipulator_framework.core.types import ObstacleState, Pose3D


@dataclass
class CoppeliaSimObstacleSource(ObstacleSourceInterface):
    """
    CoppeliaSim-specific obstacle provider.
    Fulfills the 'ObstacleSourceInterface' contract by polling the simulator.
    """
    sim_client: Any
    obstacle_handles: tuple[str, ...] = field(default_factory=tuple)

    def get_obstacles(self) -> list[ObstacleState]:
        obstacles = []
        for handle_name in self.obstacle_handles:
            position = self._read_obstacle_position(handle_name)
            orientation = self._read_obstacle_quaternion(handle_name)

            obstacles.append(
                ObstacleState(
                    obstacle_id=handle_name,
                    pose=Pose3D(
                        position=np.asarray(position, dtype=float),
                        orientation_quat_xyzw=np.asarray(orientation, dtype=float),
                    ),
                    radius=0.1,
                    source="coppeliasim",
                    timestamp=self._read_time(),
                )
            )
        return obstacles

    def _read_obstacle_position(self, obstacle_handle: str) -> list[float]:
        reader = getattr(self.sim_client, "get_object_position", None)
        if callable(reader):
            return list(
                reader(
                    handle=obstacle_handle,
                    reference_frame="world",
                )
            )
        return [0.7, 0.2, 0.5]

    def _read_obstacle_quaternion(self, obstacle_handle: str) -> list[float]:
        reader = getattr(self.sim_client, "get_object_quaternion", None)
        if callable(reader):
            return list(
                reader(
                    handle=obstacle_handle,
                    reference_frame="world",
                )
            )
        return [0.0, 0.0, 0.0, 1.0]

    def _read_time(self) -> float:
        reader = getattr(self.sim_client, "get_sim_time", None)
        if callable(reader):
            return float(reader())
        return 0.0
