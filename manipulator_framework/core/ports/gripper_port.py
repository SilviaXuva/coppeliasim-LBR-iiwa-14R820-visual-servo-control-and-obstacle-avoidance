from __future__ import annotations

from typing import Protocol


class GripperPort(Protocol):
    """Minimal gripper boundary used by application use-cases."""

    def open(self) -> None:
        """Open the gripper."""

    def close(self) -> None:
        """Close the gripper."""

    def grasp(self) -> bool:
        """
        Try grasping and report whether a stable grasp was detected.

        Backends may use proximity/contact/sensor criteria when available.
        If such signals are unavailable, implementations should clearly document
        their fallback heuristic.
        """

    def release(self) -> None:
        """Release whatever is currently grasped."""
