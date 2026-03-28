from __future__ import annotations

from dataclasses import dataclass

from .aliases import Timestamp
from .mixins import SerializableMixin
from .robot import JointCommand, TorqueCommand


@dataclass(frozen=True)
class ControlOutput(SerializableMixin):
    joint_command: JointCommand | None = None
    torque_command: TorqueCommand | None = None
    status: str = "ok"
    message: str = ""
    timestamp: Timestamp = 0.0

    def __post_init__(self) -> None:
        if self.joint_command is None and self.torque_command is None:
            raise ValueError("ControlOutput must contain at least one command.")
