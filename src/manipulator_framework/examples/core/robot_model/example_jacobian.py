from __future__ import annotations

import numpy as np

from manipulator_framework.core.robot_model import Iiwa14R820Model
from manipulator_framework.core.kinematics import JacobianSolver


def main() -> None:
    model = Iiwa14R820Model()
    jac_solver = JacobianSolver(model)

    q = np.array([0.0, 0.2, -0.1, 0.3, 0.0, -0.2, 0.1], dtype=float)
    jac = jac_solver.compute_geometric(q)

    print("Jacobian shape:", jac.shape)
    print(jac)


if __name__ == "__main__":
    main()
