from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from manipulator_framework.core.contracts import SimulatorInterface


@dataclass
class CoppeliaSimSimulatorAdapter(SimulatorInterface):
    """
    Adapter for high-level simulator lifecycle control.
    """
    sim_client: Any

    def start(self) -> None:
        self._start_simulation()

    def step(self) -> None:
        self._step_simulation()

    def stop(self) -> None:
        self._stop_simulation()

    def reset(self) -> None:
        self.stop()
        self.start()

    def _start_simulation(self) -> None:
        raise NotImplementedError("Bind simulator start API here.")

    def _step_simulation(self) -> None:
        raise NotImplementedError("Bind simulator step API here.")

    def _stop_simulation(self) -> None:
        raise NotImplementedError("Bind simulator stop API here.")
