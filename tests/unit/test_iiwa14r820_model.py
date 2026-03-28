from __future__ import annotations

from manipulator_framework.core.robot_model import Iiwa14R820Model


def test_model_has_expected_dof() -> None:
    model = Iiwa14R820Model()
    assert model.dof == 7


def test_model_default_configurations_have_correct_shape() -> None:
    model = Iiwa14R820Model()
    assert model.qz.shape == (7,)
    assert model.qr.shape == (7,)


def test_joint_limits_shape_is_correct() -> None:
    model = Iiwa14R820Model()
    assert model.joint_limits.lower.shape == (7,)
    assert model.joint_limits.upper.shape == (7,)
