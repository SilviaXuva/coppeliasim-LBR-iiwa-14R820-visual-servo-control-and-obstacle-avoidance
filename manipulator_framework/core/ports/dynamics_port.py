from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol


DynamicsMatrix = tuple[tuple[float, ...], ...]
DynamicsVector = tuple[float, ...]


class DynamicsPort(Protocol):
    """Manipulator dynamics boundary required by dynamic controllers."""

    def inertia(self, joints_positions: Sequence[float]) -> DynamicsMatrix:
        """Return the joint-space inertia matrix M(q)."""

    def coriolis(
        self,
        joints_positions: Sequence[float],
        joints_velocities: Sequence[float],
    ) -> DynamicsMatrix:
        """Return the Coriolis matrix C(q, dq)."""

    def gravity(self, joints_positions: Sequence[float]) -> DynamicsVector:
        """Return the gravity vector g(q)."""
