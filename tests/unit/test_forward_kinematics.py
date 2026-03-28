from __future__ import annotations

from manipulator_framework.core.robot_model import Iiwa14R820Model
from manipulator_framework.core.kinematics import ForwardKinematicsSolver


def test_forward_kinematics_returns_pose3d() -> None:
    model = Iiwa14R820Model()
    solver = ForwardKinematicsSolver(model)

    pose = solver.compute(model.qz)

    assert pose.position.shape == (3,)
    assert pose.orientation_quat_xyzw.shape == (4,)
    assert pose.frame_id == model.base_frame
    assert pose.child_frame_id == model.tool_frame
