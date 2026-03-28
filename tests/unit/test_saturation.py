from __future__ import annotations

import numpy as np

from manipulator_framework.core.control.saturation import symmetric_clip


def test_symmetric_clip_limits_vector() -> None:
    values = np.array([-3.0, -1.0, 0.5, 4.0])
    clipped = symmetric_clip(values, 2.0)

    assert np.allclose(clipped, np.array([-2.0, -1.0, 0.5, 2.0]))
