import unittest

from manipulator_framework.core.models.marker_state import MarkerState
from manipulator_framework.core.models.person_state import PersonState
from manipulator_framework.core.models.pose import Pose
from manipulator_framework.core.models.robot_state import RobotState


class TestModels(unittest.TestCase):
    def test_pose_helpers(self) -> None:
        pose = Pose(x=1.0, y=2.0, z=3.0, roll=0.1, pitch=0.2, yaw=0.3)
        rebuilt = Pose.from_xyz_rpy((1.0, 2.0, 3.0), (0.1, 0.2, 0.3))

        self.assertEqual(pose.xyz, (1.0, 2.0, 3.0))
        self.assertEqual(pose.rpy, (0.1, 0.2, 0.3))
        self.assertEqual(pose.as_vector(), (1.0, 2.0, 3.0, 0.1, 0.2, 0.3))
        self.assertEqual(rebuilt, pose)

    def test_robot_state_defaults_and_count(self) -> None:
        state = RobotState(joints_positions=(0.0, 1.0, 2.0))
        self.assertEqual(state.joints_count, 3)
        self.assertEqual(state.joints_velocities, ())
        self.assertEqual(state.joints_accelerations, ())

    def test_marker_and_person_defaults(self) -> None:
        marker = MarkerState(marker_id=10)
        person = PersonState(person_id="p0")

        self.assertEqual(marker.marker_id, 10)
        self.assertEqual(marker.corners_uv, ())
        self.assertIsNone(marker.pose_world)

        self.assertEqual(person.person_id, "p0")
        self.assertEqual(person.velocity_xyz, (0.0, 0.0, 0.0))
        self.assertTrue(person.tracked)

    def test_slots_are_enabled(self) -> None:
        pose = Pose(0.0, 0.0, 0.0)
        with self.assertRaises(AttributeError):
            _ = pose.__dict__


if __name__ == "__main__":
    unittest.main()
