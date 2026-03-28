from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class ExponentialMovingAverageFilter:
    """
    Minimal exponential moving average filter for vector estimates.
    """
    alpha: float
    _state: np.ndarray | None = None

    def update(self, value: np.ndarray) -> np.ndarray:
        arr = np.asarray(value, dtype=float)

        if not (0.0 < self.alpha <= 1.0):
            raise ValueError("alpha must be in (0, 1].")

        if self._state is None:
            self._state = arr.copy()
        else:
            self._state = self.alpha * arr + (1.0 - self.alpha) * self._state

        return self._state.copy()

    def reset(self) -> None:
        self._state = None
