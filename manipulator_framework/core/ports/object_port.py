from __future__ import annotations

from typing import Protocol

from ..models.pose import Pose


class ObjectPort(Protocol):
    """Minimal object manipulation boundary for pick-and-place flows."""

    def get_pose(self) -> Pose:
        """Return the current object pose in world frame."""

    def set_pose(self, pose: Pose) -> None:
        """Set object pose in world frame."""

    def attach_to_gripper(self) -> None:
        """Attach object to the configured gripper frame."""

    def detach_from_gripper(self) -> None:
        """Detach object from gripper and place it back in world frame."""
