from __future__ import annotations

import numpy as np

from manipulator_framework.core.kinematics.frame_transforms import compose_transforms, invert_transform


def test_transform_inversion_is_consistent() -> None:
    T = np.eye(4)
    T[:3, 3] = np.array([0.3, -0.2, 1.1])

    T_inv = invert_transform(T)
    identity = compose_transforms(T, T_inv)

    assert np.allclose(identity, np.eye(4), atol=1e-9)
