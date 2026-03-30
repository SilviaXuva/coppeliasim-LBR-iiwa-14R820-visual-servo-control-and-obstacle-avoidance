from __future__ import annotations

import numpy as np

from manipulator_framework.core.estimation import ExponentialMovingAverageFilter


def test_exponential_moving_average_filter_updates_state() -> None:
    filt = ExponentialMovingAverageFilter(alpha=0.5)

    x1 = filt.update(np.array([1.0, 1.0]))
    x2 = filt.update(np.array([3.0, 3.0]))

    assert np.allclose(x1, np.array([1.0, 1.0]))
    assert np.allclose(x2, np.array([2.0, 2.0]))
