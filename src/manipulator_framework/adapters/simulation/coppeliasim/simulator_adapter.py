from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from manipulator_framework.core.contracts import SimulatorInterface


@dataclass
class CoppeliaSimSimulatorAdapter(SimulatorInterface):
    """
    Adapter for high-level simulator lifecycle control.

    Expected sim_client API by convention:
    - start_simulation() or start()
    - step_simulation() or step()
    - stop_simulation() or stop()
    """

    sim_client: Any

    def start(self) -> None:
        self._call_required("start_simulation", "start")

    def step(self) -> None:
        self._call_required("step_simulation", "step")

    def stop(self) -> None:
        self._call_required("stop_simulation", "stop")

    def reset(self) -> None:
        self.stop()
        self.start()

    def _call_required(self, *method_names: str) -> Any:
        for method_name in method_names:
            candidate = getattr(self.sim_client, method_name, None)
            if callable(candidate):
                return candidate()

        raise NotImplementedError(
            "CoppeliaSim client must implement one of the methods: "
            + ", ".join(method_names)
            + "."
        )
