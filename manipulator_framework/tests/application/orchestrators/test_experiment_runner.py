import unittest

from manipulator_framework.application.orchestrators.experiment_runner import (
    ExperimentRunner,
    PickAndPlaceWiring,
)
from manipulator_framework.application.use_cases.pick_and_place import PickAndPlaceResult
from manipulator_framework.config.experiment_config import ExperimentConfig
from manipulator_framework.core.models.marker_state import MarkerState
from manipulator_framework.core.models.pose import Pose
from manipulator_framework.core.models.robot_state import RobotState


class _FakeUseCase:
    def __init__(self, results: list[PickAndPlaceResult]) -> None:
        self._results = results
        self.calls = 0

    def run_once(self, max_control_steps=None) -> PickAndPlaceResult:
        del max_control_steps
        index = min(self.calls, len(self._results) - 1)
        self.calls += 1
        return self._results[index]


class _FakeUseCaseWithShutdown:
    def __init__(self) -> None:
        self.shutdown_calls = 0

    def run_once(self, max_control_steps=None) -> PickAndPlaceResult:
        del max_control_steps
        return PickAndPlaceResult(True, "ok", 1, 1)

    def shutdown(self) -> None:
        self.shutdown_calls += 1


class _FakeRobot:
    def __init__(self) -> None:
        self._q = (0.0, 0.0, 0.0)

    def get_state(self) -> RobotState:
        return RobotState(joints_positions=self._q)

    def get_joints_positions(self):
        return self._q

    def command_joints_positions(self, joints_positions):
        self._q = tuple(joints_positions)

    def command_joints_velocities(self, joints_velocities):
        self._q = tuple(
            q + 0.1 * q_dot for q, q_dot in zip(self._q, tuple(joints_velocities))
        )

    def step(self, reference_xyz=None):
        del reference_xyz
        return None


class _FakeCamera:
    def capture_frame(self):
        return object()

    def get_intrinsic_matrix(self):
        return ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))

    def get_distortion_coefficients(self):
        return ()

    def get_extrinsic_matrix(self):
        return (
            (1.0, 0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 0.0, 0.0, 1.0),
        )


class _FakePerception:
    def detect_markers(self, frame):
        del frame
        return (MarkerState(marker_id=7, pose_world=Pose(0.2, 0.1, 0.3)),)

    def detect_people(self, frame):
        del frame
        return ()


class _FakeKinematics:
    def forward_kinematics(self, joints_positions):
        return Pose(x=sum(joints_positions), y=0.0, z=0.0)

    def inverse_kinematics(self, target_pose, seed_joints_positions=None):
        del seed_joints_positions
        return (target_pose.x, target_pose.y, target_pose.z)

    def jacobian(self, joints_positions):
        del joints_positions
        return tuple(tuple(0.0 for _ in range(3)) for _ in range(6))

    def plan_joint_trajectory(self, start_joints_positions, goal_joints_positions, time_samples_s):
        del start_joints_positions, goal_joints_positions, time_samples_s
        return ()

    def plan_cartesian_trajectory(self, start_pose, goal_pose, time_samples_s):
        del start_pose, goal_pose, time_samples_s
        return ()


class TestExperimentRunner(unittest.TestCase):
    def test_run_honors_stop_on_success(self) -> None:
        fake_use_case = _FakeUseCase(
            [
                PickAndPlaceResult(False, "fail", 0, 0),
                PickAndPlaceResult(True, "ok", 1, 2),
                PickAndPlaceResult(True, "should_not_run", 1, 2),
            ]
        )
        runner = ExperimentRunner(use_case=fake_use_case)  # type: ignore[arg-type]

        results = runner.run(cycles=5, stop_on_success=True)

        self.assertEqual(len(results), 2)
        self.assertFalse(results[0].success)
        self.assertTrue(results[1].success)
        self.assertEqual(fake_use_case.calls, 2)

    def test_run_validates_cycles(self) -> None:
        runner = ExperimentRunner(use_case=_FakeUseCase([PickAndPlaceResult(True, "ok", 1, 1)]))  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            runner.run(cycles=0)

    def test_from_wiring_runs_minimal_flow(self) -> None:
        wiring = PickAndPlaceWiring(
            robot=_FakeRobot(),
            camera=_FakeCamera(),
            perception=_FakePerception(),
            kinematics=_FakeKinematics(),
            visualization=None,
        )
        runner = ExperimentRunner.from_wiring(
            wiring=wiring,
            trajectory_duration_s=0.2,
            control_dt_s=0.1,
        )

        results = runner.run(cycles=1)

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].success)
        self.assertEqual(results[0].reason, "trajectory_executed")

    def test_run_experiment_calls_use_case_shutdown(self) -> None:
        fake_use_case = _FakeUseCaseWithShutdown()
        config = ExperimentConfig()
        config.runtime.cycles = 1
        runner = ExperimentRunner(
            use_case=fake_use_case,  # type: ignore[arg-type]
            config=config,
            results_repository=None,
        )

        execution = runner.run_experiment()

        self.assertEqual(execution.metrics["cycles_executed"], 1)
        self.assertEqual(fake_use_case.shutdown_calls, 1)

    def test_from_config_supports_dynamic_pd_experiment(self) -> None:
        config = ExperimentConfig(experiment="pick_and_place_dyn_pd")
        config.runtime.backend = "mock"
        config.runtime.cycles = 1

        runner = ExperimentRunner.from_config(config=config, results_repository=None)
        results = runner.run(cycles=1)

        self.assertEqual(len(results), 1)
        self.assertIn(results[0].reason, {"trajectory_executed", "max_control_steps_reached"})


if __name__ == "__main__":
    unittest.main()

