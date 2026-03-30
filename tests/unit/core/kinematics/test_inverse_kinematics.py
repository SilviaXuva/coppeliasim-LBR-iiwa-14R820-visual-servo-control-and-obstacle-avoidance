from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from manipulator_framework.core.kinematics.inverse_kinematics import InverseKinematicsSolver
from manipulator_framework.core.robot_model import Iiwa14R820Model
from manipulator_framework.core.types import Pose3D


@dataclass
class _FakeIKSolution:
    q: np.ndarray
    success: bool
    iterations: int = 4
    residual: float = 1e-4


class _FakeBackend:
    received_target_matrix: np.ndarray | None = None

    def __init__(self, model):
        self.model = model

    def solve_inverse_kinematics(self, *, target_matrix: np.ndarray, q0: np.ndarray):
        _FakeBackend.received_target_matrix = np.asarray(target_matrix, dtype=float)
        return _FakeIKSolution(q=np.asarray(q0, dtype=float), success=True)


def test_inverse_kinematics_accepts_pose3d_without_external_types(monkeypatch) -> None:
    model = Iiwa14R820Model()
    solver = InverseKinematicsSolver(model=model)

    monkeypatch.setattr(
        "manipulator_framework.core.kinematics.inverse_kinematics.RoboticsToolboxIiwaBackend",
        _FakeBackend,
    )

    pose = Pose3D(
        position=np.array([0.5, 0.0, 0.6], dtype=float),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0], dtype=float),
    )
    result = solver.compute(pose)

    assert result.success is True
    assert _FakeBackend.received_target_matrix is not None
    assert _FakeBackend.received_target_matrix.shape == (4, 4)

