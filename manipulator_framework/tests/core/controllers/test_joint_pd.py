import unittest

import numpy as np

from manipulator_framework.core.controllers.dynamic.joint_pd import JointPDController
from manipulator_framework.core.ports.dynamics_port import DynamicsPort


class _FakeDynamics(DynamicsPort):
    def __init__(
        self,
        inertia_matrix: tuple[tuple[float, ...], ...],
        coriolis_matrix: tuple[tuple[float, ...], ...],
        gravity_vector: tuple[float, ...],
    ) -> None:
        self._inertia_matrix = inertia_matrix
        self._coriolis_matrix = coriolis_matrix
        self._gravity_vector = gravity_vector

    def inertia(self, joints_positions):
        del joints_positions
        return self._inertia_matrix

    def coriolis(self, joints_positions, joints_velocities):
        del joints_positions, joints_velocities
        return self._coriolis_matrix

    def gravity(self, joints_positions):
        del joints_positions
        return self._gravity_vector


class TestJointPDController(unittest.TestCase):
    def test_zero_error_keeps_velocity_and_zero_acceleration(self) -> None:
        dynamics = _FakeDynamics(
            inertia_matrix=((1.0, 0.0), (0.0, 1.0)),
            coriolis_matrix=((0.0, 0.0), (0.0, 0.0)),
            gravity_vector=(1.5, -0.5),
        )
        controller = JointPDController(
            dynamics=dynamics,
            kp=10.0,
            kv=5.0,
            joints_count=2,
            joints_torques_min=(-10.0, -10.0),
            joints_torques_max=(10.0, 10.0),
        )

        result = controller.compute(
            joints_positions=(0.3, -0.2),
            joints_positions_ref=(0.3, -0.2),
            joints_velocities=(0.7, -0.4),
            joints_velocities_ref=(0.7, -0.4),
            dt=0.1,
        )

        self.assertEqual(result.joints_torques, (1.5, -0.5))
        self.assertAlmostEqual(result.joints_accelerations[0], 0.0, places=8)
        self.assertAlmostEqual(result.joints_accelerations[1], 0.0, places=8)
        self.assertAlmostEqual(result.joints_velocities[0], 0.7, places=8)
        self.assertAlmostEqual(result.joints_velocities[1], -0.4, places=8)

    def test_torque_is_saturated_by_injected_limits(self) -> None:
        dynamics = _FakeDynamics(
            inertia_matrix=((1.0, 0.0), (0.0, 1.0)),
            coriolis_matrix=((0.0, 0.0), (0.0, 0.0)),
            gravity_vector=(0.0, 0.0),
        )
        controller = JointPDController(
            dynamics=dynamics,
            kp=10.0,
            kv=0.0,
            joints_count=2,
            joints_torques_min=(-5.0, -5.0),
            joints_torques_max=(5.0, 5.0),
        )

        result = controller.compute(
            joints_positions=(0.0, 0.0),
            joints_positions_ref=(2.0, -2.0),
            joints_velocities=(0.0, 0.0),
            joints_velocities_ref=(0.0, 0.0),
            dt=0.1,
        )

        self.assertEqual(result.joints_torques, (5.0, -5.0))
        self.assertEqual(result.joints_accelerations, (5.0, -5.0))
        self.assertEqual(result.joints_velocities, (0.5, -0.5))

    def test_output_dimensions_match_joints_count(self) -> None:
        inertia_matrix = np.eye(3, dtype=float)
        dynamics = _FakeDynamics(
            inertia_matrix=tuple(tuple(float(value) for value in row) for row in inertia_matrix),
            coriolis_matrix=((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
            gravity_vector=(0.0, 0.0, 0.0),
        )
        controller = JointPDController(
            dynamics=dynamics,
            kp=(1.0, 2.0, 3.0),
            kv=(0.1, 0.2, 0.3),
            joints_count=3,
            joints_torques_min=(-100.0, -100.0, -100.0),
            joints_torques_max=(100.0, 100.0, 100.0),
        )

        result = controller.update(
            joints_positions=(0.0, 0.0, 0.0),
            joints_positions_ref=(1.0, 1.0, 1.0),
            joints_velocities=(0.0, 0.0, 0.0),
            joints_velocities_ref=(0.0, 0.0, 0.0),
            dt=0.05,
        )

        self.assertEqual(len(result.joints_accelerations), 3)
        self.assertEqual(len(result.joints_velocities), 3)
        self.assertEqual(len(result.joints_torques), 3)
        self.assertEqual(len(result.joints_velocities), 3)

    def test_singular_inertia_uses_stable_fallback(self) -> None:
        dynamics = _FakeDynamics(
            inertia_matrix=((1.0, 0.0), (0.0, 0.0)),
            coriolis_matrix=((0.0, 0.0), (0.0, 0.0)),
            gravity_vector=(0.0, 0.0),
        )
        controller = JointPDController(
            dynamics=dynamics,
            kp=1.0,
            kv=0.0,
            joints_count=2,
            joints_torques_min=(-100.0, -100.0),
            joints_torques_max=(100.0, 100.0),
        )

        result = controller.compute(
            joints_positions=(0.0, 0.0),
            joints_positions_ref=(2.0, 2.0),
            joints_velocities=(0.0, 0.0),
            joints_velocities_ref=(0.0, 0.0),
            dt=0.1,
        )

        self.assertAlmostEqual(result.joints_accelerations[0], 2.0, places=8)
        self.assertAlmostEqual(result.joints_accelerations[1], 0.0, places=8)
        self.assertAlmostEqual(result.joints_velocities[0], 0.2, places=8)
        self.assertAlmostEqual(result.joints_velocities[1], 0.0, places=8)


if __name__ == "__main__":
    unittest.main()
