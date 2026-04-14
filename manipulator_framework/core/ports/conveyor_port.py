from __future__ import annotations

from typing import Protocol


class ConveyorPort(Protocol):
    """Minimal conveyor boundary used by application use-cases."""

    def start(self) -> None:
        """Start conveyor movement using the configured nominal speed."""

    def stop(self) -> None:
        """Stop conveyor movement."""

    def set_speed(self, speed: float) -> None:
        """Set conveyor speed."""

    def get_speed(self) -> float:
        """Return current conveyor speed."""
