from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from manipulator_framework.core.contracts import ObstacleSourceInterface
from manipulator_framework.core.types import ObstacleState, Pose3D


@dataclass
class PyPlotObstacleSource(ObstacleSourceInterface):
    """
    Minimal obstacle source adapter for PyPlot-like backends.

    Expected backend API by convention:
    - current_obstacles() -> iterable of ObstacleState | dict
    - current_time() optional
    """

    backend: Any

    def get_obstacles(self) -> list[ObstacleState]:
        reader = getattr(self.backend, "current_obstacles", None)
        if not callable(reader):
            return []

        obstacles: list[ObstacleState] = []
        for index, payload in enumerate(reader()):
            if isinstance(payload, ObstacleState):
                obstacles.append(payload)
                continue
            if isinstance(payload, dict):
                timestamp = float(payload.get("timestamp", self._time()))
                obstacles.append(
                    ObstacleState(
                        obstacle_id=str(payload.get("obstacle_id", f"pyplot_obstacle_{index}")),
                        pose=Pose3D(
                            position=np.asarray(payload.get("position", [0.0, 0.0, 0.0]), dtype=float),
                            orientation_quat_xyzw=np.asarray(
                                payload.get("orientation_quat_xyzw", [0.0, 0.0, 0.0, 1.0]),
                                dtype=float,
                            ),
                            timestamp=timestamp,
                        ),
                        radius=float(payload.get("radius", 0.1)),
                        source="pyplot",
                        timestamp=timestamp,
                    )
                )
                continue
            raise TypeError("PyPlot obstacle payload must be ObstacleState or dict.")
        return obstacles

    def _time(self) -> float:
        reader = getattr(self.backend, "current_time", None)
        if callable(reader):
            return float(reader())
        return 0.0

