from __future__ import annotations

from ...core.ports.conveyor_port import ConveyorPort


class CoppeliaConveyorAdapter(ConveyorPort):
    """Conveyor adapter backed by CoppeliaSim Remote API."""

    def __init__(
        self,
        sim: object,
        conveyor_path: str,
        *,
        default_speed: float = 0.1,
    ) -> None:
        self._sim = sim
        self._conveyor_handle = self._resolve_handle(conveyor_path)
        self._default_speed = float(default_speed)
        self._speed = self._default_speed

    def start(self) -> None:
        self.set_speed(self._default_speed)

    def stop(self) -> None:
        self.set_speed(0.0)

    def set_speed(self, speed: float) -> None:
        speed_value = float(speed)
        self._sim.writeCustomTableData(
            self._conveyor_handle,
            "__ctrl__",
            {"vel": speed_value},
        )
        self._speed = speed_value

    def get_speed(self) -> float:
        try:
            state = self._sim.readCustomTableData(self._conveyor_handle, "__state__")
            if isinstance(state, dict) and "vel" in state:
                return float(state["vel"])
        except Exception:
            pass
        return self._speed

    def _resolve_handle(self, conveyor_path: str) -> int:
        get_object = getattr(self._sim, "getObject", None)
        if callable(get_object):
            return int(get_object(conveyor_path))
        get_object_handle = getattr(self._sim, "getObjectHandle", None)
        if callable(get_object_handle):
            return int(get_object_handle(conveyor_path))
        raise ValueError("Coppelia sim object does not expose `getObject` or `getObjectHandle`.")
