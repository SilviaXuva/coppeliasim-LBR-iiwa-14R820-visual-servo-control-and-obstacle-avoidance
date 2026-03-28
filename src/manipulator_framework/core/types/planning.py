from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np

from .aliases import Timestamp
from .mixins import SerializableMixin
from .robot import JointState


@dataclass(frozen=True)
class TrajectorySample(SerializableMixin):
    time_from_start: float
    joint_state: JointState

    def __post_init__(self) -> None:
        if self.time_from_start < 0.0:
            raise ValueError("time_from_start must be non-negative.")


@dataclass(frozen=True)
class Trajectory(SerializableMixin):
    samples: tuple[TrajectorySample, ...] = field(default_factory=tuple)
    name: str = "unnamed_trajectory"
    timestamp: Timestamp = 0.0

    def __post_init__(self) -> None:
        if not self.samples:
            raise ValueError("Trajectory must contain at least one sample.")

    @property
    def duration(self) -> float:
        return self.samples[-1].time_from_start

    @property
    def dof(self) -> int:
        return self.samples[0].joint_state.dof
