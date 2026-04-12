import unittest

from manipulator_framework.core.trajectory.quintic_trajectory import (
    QuinticJointTrajectory,
    generate,
)


class TestQuinticJointTrajectory(unittest.TestCase):
    def test_generate_respects_boundary_conditions(self) -> None:
        trajectory = generate(q0=[0.0, 1.0], qf=[1.0, -1.0], tf=2.0, dt=0.5)

        self.assertEqual(trajectory.joints_positions[0], (0.0, 1.0))
        self.assertAlmostEqual(trajectory.joints_positions[-1][0], 1.0, places=8)
        self.assertAlmostEqual(trajectory.joints_positions[-1][1], -1.0, places=8)

        self.assertAlmostEqual(trajectory.joints_velocities[0][0], 0.0, places=8)
        self.assertAlmostEqual(trajectory.joints_velocities[0][1], 0.0, places=8)
        self.assertAlmostEqual(trajectory.joints_velocities[-1][0], 0.0, places=8)
        self.assertAlmostEqual(trajectory.joints_velocities[-1][1], 0.0, places=8)

        self.assertAlmostEqual(trajectory.joints_accelerations[0][0], 0.0, places=8)
        self.assertAlmostEqual(trajectory.joints_accelerations[-1][0], 0.0, places=8)

    def test_generate_validates_parameters(self) -> None:
        generator = QuinticJointTrajectory()

        with self.assertRaises(ValueError):
            generator.generate(q0=[0.0], qf=[1.0], tf=0.0, dt=0.1)
        with self.assertRaises(ValueError):
            generator.generate(q0=[0.0], qf=[1.0], tf=1.0, dt=0.0)
        with self.assertRaises(ValueError):
            generator.generate_from_time_samples(
                q0=[0.0],
                qf=[1.0, 2.0],
                time_samples_s=[0.0, 1.0],
            )
        with self.assertRaises(ValueError):
            generator.generate_from_time_samples(
                q0=[0.0],
                qf=[1.0],
                time_samples_s=[1.0, 1.0],
            )


if __name__ == "__main__":
    unittest.main()
