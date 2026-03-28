from __future__ import annotations

import numpy as np

from manipulator_framework.core.robot_model import Iiwa14R820Model
from manipulator_framework.core.kinematics import JacobianSolver


def test_geometric_jacobian_has_expected_shape() -> None:
    model = Iiwa14R820Model()
    solver = JacobianSolver(model)

    jac = solver.compute_geometric(model.qz)

    assert jac.shape == (6, 7)
    assert np.isfinite(jac).all()
