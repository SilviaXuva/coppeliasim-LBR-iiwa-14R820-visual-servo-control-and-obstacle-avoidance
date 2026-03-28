from __future__ import annotations

import numpy as np

from manipulator_framework.core.robot_model import Iiwa14R820Model
from manipulator_framework.core.kinematics import ForwardKinematicsSolver


def main() -> None:
    model = Iiwa14R820Model()
    fk_solver = ForwardKinematicsSolver(model)

    q = model.qz
    pose = fk_solver.compute(q, timestamp=0.0)

    print("Model name:", model.name)
    print("DOF:", model.dof)
    print("Pose:", pose.to_dict())


if __name__ == "__main__":
    main()
