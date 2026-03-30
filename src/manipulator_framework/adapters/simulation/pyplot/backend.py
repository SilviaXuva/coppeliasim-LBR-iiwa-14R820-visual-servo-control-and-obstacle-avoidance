from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class DefaultPyPlotBackend:
    """
    Lightweight in-process backend used when no external PyPlot runtime is injected.
    """

    dof: int = 7
    dt: float = 0.01
    image_size_hw: tuple[int, int] = (64, 64)
    _time: float = field(default=0.0, init=False, repr=False)
    _positions: np.ndarray = field(default_factory=lambda: np.zeros(7, dtype=float), init=False, repr=False)
    _velocities: np.ndarray = field(default_factory=lambda: np.zeros(7, dtype=float), init=False, repr=False)
    _obstacles: list[dict[str, object]] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        self._positions = np.zeros(self.dof, dtype=float)
        self._velocities = np.zeros(self.dof, dtype=float)

    def start(self) -> None:
        self._time = 0.0

    def reset(self) -> None:
        self._positions = np.zeros(self.dof, dtype=float)
        self._velocities = np.zeros(self.dof, dtype=float)
        self._time = 0.0

    def step(self) -> None:
        self._time += float(self.dt)

    def stop(self) -> None:
        return None

    def current_time(self) -> float:
        return float(self._time)

    def current_joint_positions(self):
        return self._positions.copy()

    def current_joint_velocities(self):
        return self._velocities.copy()

    def current_end_effector_pose(self):
        z = 0.5 + 0.01 * float(np.sum(self._positions))
        return [0.5, 0.0, z], [0.0, 0.0, 0.0, 1.0]

    def apply_joint_command(self, command):
        target = np.asarray(command, dtype=float).reshape(-1)
        if target.size != self.dof:
            raise ValueError(f"Joint command size {target.size} incompatible with dof={self.dof}.")
        self._velocities = (target - self._positions) / max(float(self.dt), 1e-9)
        self._positions = target

    def apply_torque_command(self, command):
        torques = np.asarray(command, dtype=float).reshape(-1)
        if torques.size != self.dof:
            raise ValueError(f"Torque command size {torques.size} incompatible with dof={self.dof}.")
        self._velocities = torques * 0.0

    def current_frame(self):
        h, w = self.image_size_hw
        return np.zeros((h, w, 3), dtype=np.uint8)

    def current_camera_intrinsics(self):
        return np.eye(3, dtype=float)

    def current_camera_extrinsics(self):
        return {
            "position": [0.0, 0.0, 1.0],
            "orientation_quat_xyzw": [0.0, 0.0, 0.0, 1.0],
            "frame_id": "world",
            "child_frame_id": "camera",
            "timestamp": self._time,
        }

    def current_obstacles(self):
        return list(self._obstacles)

    def set_obstacles(self, obstacles: list[dict[str, object]]) -> None:
        self._obstacles = list(obstacles)

