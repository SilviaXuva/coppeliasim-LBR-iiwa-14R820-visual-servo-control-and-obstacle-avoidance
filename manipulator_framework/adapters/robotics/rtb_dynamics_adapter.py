from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from roboticstoolbox import DHRobot, ERobot

from ...core.ports.dynamics_port import DynamicsMatrix, DynamicsPort, DynamicsVector


class RTBDynamicsAdapter(DynamicsPort):
    """Implements DynamicsPort using Robotics Toolbox."""

    def __init__(self, robot: DHRobot | ERobot) -> None:
        self._robot = robot

    def inertia(self, joints_positions: Sequence[float]) -> DynamicsMatrix:
        matrix = self._robot.inertia(np.asarray(joints_positions, dtype=float))
        return self._as_matrix(matrix)

    def coriolis(
        self,
        joints_positions: Sequence[float],
        joints_velocities: Sequence[float],
    ) -> DynamicsMatrix:
        matrix = self._robot.coriolis(
            np.asarray(joints_positions, dtype=float),
            np.asarray(joints_velocities, dtype=float),
        )
        return self._as_matrix(matrix)

    def gravity(self, joints_positions: Sequence[float]) -> DynamicsVector:
        vector = self._robot.gravload(np.asarray(joints_positions, dtype=float))
        return self._as_vector(vector)

    @staticmethod
    def _as_matrix(matrix: object) -> DynamicsMatrix:
        matrix_array = np.asarray(matrix, dtype=float)
        if matrix_array.ndim != 2:
            raise ValueError("Expected a 2D dynamics matrix.")
        return tuple(
            tuple(float(value) for value in row) for row in matrix_array.tolist()
        )

    @staticmethod
    def _as_vector(vector: object) -> DynamicsVector:
        vector_array = np.asarray(vector, dtype=float).reshape(-1)
        return tuple(float(value) for value in vector_array)
