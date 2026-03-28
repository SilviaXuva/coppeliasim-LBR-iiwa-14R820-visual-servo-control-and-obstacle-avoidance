from __future__ import annotations

import time

from manipulator_framework.core.contracts.clock_interface import ClockInterface


class SystemClock(ClockInterface):
    """Wall-clock implementation for non-simulated execution."""

    def __init__(self) -> None:
        self._last_time = time.time()

    def now(self) -> float:
        current = time.time()
        self._last_time = current
        return current

    def dt(self) -> float:
        current = time.time()
        delta = current - self._last_time
        self._last_time = current
        return delta

    def sleep_until(self, timestamp: float) -> None:
        remaining = timestamp - time.time()
        if remaining > 0.0:
            time.sleep(remaining)
