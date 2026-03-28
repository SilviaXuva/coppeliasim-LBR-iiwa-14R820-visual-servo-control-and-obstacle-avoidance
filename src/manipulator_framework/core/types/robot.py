from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np

from .aliases import Timestamp
from .enums import CommandMode
from .geometry import Pose3D, Twist
from .mixins import SerializableMixin


def _as_joint_vector(data: np.ndarray | list[float] | tuple[float, ...], dof: int | None = None) -> np.ndarray:
    arr = np.asarray(data, dtype=float).reshape(-1)
    if dof is not None and arr.size != dof:
        raise ValueError(f"Expected vector with {dof} elements, got {arr.size}.")
    return arr


@dataclass(frozen=True)
class JointState(SerializableMixin):
    positions: np.ndarray
    velocities: np.ndarray | None = None
    accelerations: np.ndarray | None = None
    efforts: np.ndarray | None = None
    joint_names: tuple[str, ...] = ()
    timestamp: Timestamp = 0.0

    def __post_init__(self) -> None:
        positions = _as_joint_vector(self.positions)
        dof = positions.size
        object.__setattr__(self, "positions", positions)

        if self.velocities is not None:
            object.__setattr__(self, "velocities", _as_joint_vector(self.velocities, dof))
        if self.accelerations is not None:
            object.__setattr__(self, "accelerations", _as_joint_vector(self.accelerations, dof))
        if self.efforts is not None:
            object.__setattr__(self, "efforts", _as_joint_vector(self.efforts, dof))

        if self.joint_names and len(self.joint_names) != dof:
            raise ValueError("joint_names size must match number of joints.")

    @property
    def dof(self) -> int:
        return int(self.positions.size)


@dataclass(frozen=True)
class JointCommand(SerializableMixin):
    values: np.ndarray
    mode: CommandMode
    joint_names: tuple[str, ...] = ()
    timestamp: Timestamp = 0.0

    def __post_init__(self) -> None:
        values = _as_joint_vector(self.values)
        object.__setattr__(self, "values", values)

        if self.joint_names and len(self.joint_names) != values.size:
            raise ValueError("joint_names size must match command size.")

    @property
    def positions(self) -> list[float]:
        """Alias for position-mode commands (kept for ROS adapter/tests compatibility)."""
        return self.values.tolist()

    @property
    def velocities(self) -> None:
        """Placeholder to satisfy ROS adapter expectations; velocity commands not represented here."""
        return None

    @property
    def accelerations(self) -> None:
        """Placeholder to satisfy ROS adapter expectations; acceleration commands not represented here."""
        return None

@dataclass(frozen=True)
class TorqueCommand(SerializableMixin):
    torques: np.ndarray
    joint_names: tuple[str, ...] = ()
    timestamp: Timestamp = 0.0

    def __post_init__(self) -> None:
        torques = _as_joint_vector(self.torques)
        object.__setattr__(self, "torques", torques)

        if self.joint_names and len(self.joint_names) != torques.size:
            raise ValueError("joint_names size must match torques size.")


@dataclass(frozen=True)
class RobotState(SerializableMixin):
    joint_state: JointState
    end_effector_pose: Pose3D | None = None
    end_effector_twist: Twist | None = None
    is_ready: bool = True
    timestamp: Timestamp = 0.0
