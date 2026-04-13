import unittest

import numpy as np

from manipulator_framework.core.controllers.kinematic.joint_pi import JointPIController


class TestJointPIController(unittest.TestCase):
    def test_compute_matches_pi_equation(self) -> None:
        controller = JointPIController(kp=[2.0, 3.0], ki=[0.5, 0.25], joints_count=2)

        result = controller.compute(
            joints_positions=[1.0, 2.0],
            joints_positions_ref=[1.5, 1.0],
            joints_velocities_ref=[0.1, -0.2],
            dt=0.2,
            integral_state=[0.3, -0.4],
        )

        # u = kp*e + ki*(int + e*dt) + qdot_ref
        expected_u0 = 2.0 * 0.5 + 0.5 * (0.3 + 0.5 * 0.2) + 0.1
        expected_u1 = 3.0 * (-1.0) + 0.25 * (-0.4 + (-1.0) * 0.2) - 0.2

        self.assertAlmostEqual(result.joints_positions_error[0], 0.5, places=8)
        self.assertAlmostEqual(result.joints_positions_error[1], -1.0, places=8)
        self.assertAlmostEqual(result.joints_velocities[0], expected_u0, places=8)
        self.assertAlmostEqual(result.joints_velocities[1], expected_u1, places=8)
        self.assertEqual(result.next_integral_state, (0.5, -1.0))

    def test_update_persists_integral_state(self) -> None:
        controller = JointPIController(kp=1.0, ki=0.0, joints_count=3)

        result = controller.update(
            joints_positions=[0.0, 0.0, 0.0],
            joints_positions_ref=[1.0, 2.0, 3.0],
            dt=0.1,
        )

        self.assertEqual(result.joints_positions_error, (1.0, 2.0, 3.0))
        self.assertEqual(controller.integral_state, (1.0, 2.0, 3.0))

    def test_matrix_gain_uses_diagonal(self) -> None:
        controller = JointPIController(
            kp=[[10.0, 1.0], [2.0, 20.0]],
            ki=[[1.0, 0.0], [0.0, 2.0]],
            joints_count=2,
        )
        result = controller.compute(
            joints_positions=[0.0, 0.0],
            joints_positions_ref=[1.0, 1.0],
            joints_velocities_ref=[0.0, 0.0],
            dt=0.0,
        )
        self.assertEqual(result.joints_velocities, (10.0, 20.0))

    def test_invalid_shapes_raise(self) -> None:
        with self.assertRaises(ValueError):
            JointPIController(kp=[1.0], ki=[1.0], joints_count=2)

        controller = JointPIController(kp=1.0, ki=1.0, joints_count=2)
        with self.assertRaises(ValueError):
            controller.compute(
                joints_positions=[0.0],
                joints_positions_ref=[0.0, 0.0],
                joints_velocities_ref=[0.0, 0.0]
            )

    def test_accepts_numpy_scalar_vector_and_matrix_gains(self) -> None:
        controller = JointPIController(
            kp=np.float64(2.0),
            ki=np.array([[1.0, 0.0], [0.0, 3.0]], dtype=float),
            joints_count=2,
        )
        result = controller.compute(
            joints_positions=np.array([0.0, 1.0], dtype=float),
            joints_positions_ref=np.array([1.0, 2.0], dtype=float),
            joints_velocities_ref=np.array([0.1, -0.1], dtype=float),
            dt=0.5,
            integral_state=np.array([0.2, -0.2], dtype=float),
        )
        # e = [1, 1]
        # u0 = 2*1 + 1*(0.2 + 1*0.5) + 0.1 = 2.8
        # u1 = 2*1 + 3*(-0.2 + 1*0.5) - 0.1 = 2.8
        self.assertAlmostEqual(result.joints_velocities[0], 2.8, places=8)
        self.assertAlmostEqual(result.joints_velocities[1], 2.8, places=8)


if __name__ == "__main__":
    unittest.main()
