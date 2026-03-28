from __future__ import annotations

import numpy as np

from manipulator_framework.core.kinematics.frame_transforms import compose_transforms, invert_transform


def main() -> None:
    T_ab = np.eye(4)
    T_ab[:3, 3] = np.array([1.0, 0.0, 0.0])

    T_bc = np.eye(4)
    T_bc[:3, 3] = np.array([0.0, 2.0, 0.0])

    T_ac = compose_transforms(T_ab, T_bc)
    T_ca = invert_transform(T_ac)

    print("T_ac:")
    print(T_ac)
    print("T_ca:")
    print(T_ca)


if __name__ == "__main__":
    main()
