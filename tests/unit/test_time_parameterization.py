from __future__ import annotations

import numpy as np

from manipulator_framework.core.planning.time_parameterization import build_time_grid


def test_time_grid_contains_final_time() -> None:
    grid = build_time_grid(duration=1.0, time_step=0.3)

    assert np.isclose(grid[0], 0.0)
    assert np.isclose(grid[-1], 1.0)
    assert len(grid) >= 2
