from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from manipulator_framework.core.contracts import SimulatorInterface


@dataclass
class PyPlotSimulatorAdapter(SimulatorInterface):
    """
    Minimal simulator/lifecycle adapter for PyPlot-based backends.

    Expected backend API by convention:
    - start() or reset()
    - step()
    - stop() optional
    """

    backend: Any

    def start(self) -> None:
        self._call_optional("start", "reset")

    def step(self) -> None:
        self._call_required("step")

    def stop(self) -> None:
        self._call_optional("stop")

    def reset(self) -> None:
        self._call_optional("reset", "start")

    def _call_required(self, *names: str) -> Any:
        for name in names:
            candidate = getattr(self.backend, name, None)
            if callable(candidate):
                return candidate()
        raise NotImplementedError(
            f"PyPlot backend must implement one of the methods: {', '.join(names)}."
        )

    def _call_optional(self, *names: str) -> Any | None:
        for name in names:
            candidate = getattr(self.backend, name, None)
            if callable(candidate):
                return candidate()
        return None
