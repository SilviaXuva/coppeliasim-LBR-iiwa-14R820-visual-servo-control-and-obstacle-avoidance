from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Pose:
    """Minimal Cartesian pose (position + RPY orientation) for the core domain."""

    x: float
    y: float
    z: float
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0

    @property
    def xyz(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)

    @property
    def rpy(self) -> tuple[float, float, float]:
        return (self.roll, self.pitch, self.yaw)

    def as_vector(self) -> tuple[float, float, float, float, float, float]:
        return (self.x, self.y, self.z, self.roll, self.pitch, self.yaw)

    @classmethod
    def from_xyz_rpy(
        cls,
        xyz: tuple[float, float, float],
        rpy: tuple[float, float, float],
    ) -> "Pose":
        return cls(
            x=xyz[0],
            y=xyz[1],
            z=xyz[2],
            roll=rpy[0],
            pitch=rpy[1],
            yaw=rpy[2],
        )
