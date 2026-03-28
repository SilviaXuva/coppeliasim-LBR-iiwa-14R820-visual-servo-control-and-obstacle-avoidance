from __future__ import annotations

import numpy as np


def validate_duration(duration: float) -> None:
    if duration <= 0.0:
        raise ValueError("duration must be positive.")


def validate_time_step(time_step: float) -> None:
    if time_step <= 0.0:
        raise ValueError("time_step must be positive.")


def build_time_grid(duration: float, time_step: float) -> np.ndarray:
    """
    Build a closed time grid including the final time exactly.
    """
    validate_duration(duration)
    validate_time_step(time_step)

    steps = int(np.floor(duration / time_step))
    grid = np.arange(0.0, steps * time_step + 1e-12, time_step, dtype=float)

    if grid.size == 0 or not np.isclose(grid[-1], duration):
        grid = np.append(grid, duration)

    return grid
