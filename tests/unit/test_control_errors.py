from __future__ import annotations

import numpy as np

from manipulator_framework.core.control.errors import compute_joint_tracking_error
from manipulator_framework.core.types import JointState


def test_joint_tracking_error_is_computed_correctly() -> None:
    current = JointState(
        positions=np.array([0.0, 1.0]),
        velocities=np.array([0.5, -0.5]),
        timestamp=0.0,
    )
    reference = JointState(
        positions=np.array([1.0, 0.0]),
        velocities=np.array([0.0, 0.0]),
        timestamp=0.0,
    )

    error = compute_joint_tracking_error(current, reference)

    assert np.allclose(error.position_error, np.array([1.0, -1.0]))
    assert np.allclose(error.velocity_error, np.array([-0.5, 0.5]))
