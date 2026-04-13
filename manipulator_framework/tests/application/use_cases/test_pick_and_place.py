import unittest
from dataclasses import dataclass
import math

from manipulator_framework.application.use_cases.pick_and_place import PickAndPlaceUseCase
from manipulator_framework.core.models.marker_state import MarkerState
from manipulator_framework.core.models.pose import Pose
from manipulator_framework.core.models.robot_state import RobotState


@dataclass(slots=True)
class _ControlResult:
    joints_velocities: tuple[float, ...]


@dataclass(slots=True)
class _Trajectory:
    joints_positions: tuple[tuple[float, ...], ...]
    joints_velocities: tuple[tuple[float, ...], ...]


class _FakeTrajectoryGenerator:
    def __init__(self, trajectory: _Trajectory) -> None:
        self.trajectory = trajectory
        self.calls = 0

    def generate(
        self,
        q0: tuple[float, ...],
        qf: tuple[float, ...],
        tf: float,
        dt: float,
    ) -> _Trajectory:
        del q0, qf, tf, dt
        self.calls += 1
        return self.trajectory


class _FakeController:
    def __init__(self) -> None:
        self.calls = 0

    def update(
        self,
        joints_positions: tuple[float, ...],
        joints_positions_ref: tuple[float, ...],
        joints_velocities_ref: tuple[float, ...] | None = None,
        dt: float = 0.0,
    ) -> _ControlResult:
        del joints_positions, joints_positions_ref, dt
        self.calls += 1
        if joints_velocities_ref is None:
            return _ControlResult(joints_velocities=(0.0, 0.0, 0.0))
        return _ControlResult(joints_velocities=tuple(joints_velocities_ref))


class _FakeRobot:
    def __init__(self, joints_count: int = 3) -> None:
        self._q = tuple(0.0 for _ in range(joints_count))
        self.velocity_commands: list[tuple[float, ...]] = []
        self.step_calls: list[tuple[float, float, float] | None] = []

    def get_state(self) -> RobotState:
        return RobotState(joints_positions=self._q)

    def get_joints_positions(self) -> tuple[float, ...]:
        return self._q

    def command_joints_positions(self, joints_positions: tuple[float, ...]) -> None:
        self._q = tuple(joints_positions)

    def command_joints_velocities(self, joints_velocities: tuple[float, ...]) -> None:
        command = tuple(float(value) for value in joints_velocities)
        self.velocity_commands.append(command)
        self._q = tuple(
            q + 0.1 * q_dot for q, q_dot in zip(self._q, command)
        )

    def step(self, reference_xyz: tuple[float, float, float] | None = None) -> None:
        self.step_calls.append(reference_xyz)


class _FakeCamera:
    def capture_frame(self) -> object:
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
    def __init__(self, markers: tuple[MarkerState, ...]) -> None:
        self._markers = markers

    def detect_markers(self, frame: object):
        del frame
        return self._markers

    def detect_people(self, frame: object):
        del frame
        return ()


class _FakePerceptionSequence:
    def __init__(self, markers_sequence: tuple[tuple[MarkerState, ...], ...]) -> None:
        self._markers_sequence = markers_sequence
        self.calls = 0

    def detect_markers(self, frame: object):
        del frame
        index = min(self.calls, len(self._markers_sequence) - 1)
        self.calls += 1
        return self._markers_sequence[index]

    def detect_people(self, frame: object):
        del frame
        return ()


class _FakeKinematics:
    def __init__(self, fail_inverse: bool = False) -> None:
        self._fail_inverse = fail_inverse

    def forward_kinematics(self, joints_positions):
        return Pose(x=sum(joints_positions), y=0.0, z=0.0)

    def inverse_kinematics(self, target_pose: Pose, seed_joints_positions=None):
        del seed_joints_positions
        if self._fail_inverse:
            raise RuntimeError("ik failed")
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


class _FakeVisualization:
    def __init__(self) -> None:
        self.robot_updates = 0
        self.reference_updates = 0
        self.marker_updates = 0
        self.people_updates = 0

    def update_robot_state(self, state: RobotState) -> None:
        del state
        self.robot_updates += 1

    def update_reference_path(self, reference_path) -> None:
        del reference_path
        self.reference_updates += 1

    def update_markers(self, markers) -> None:
        del markers
        self.marker_updates += 1

    def update_people(self, people) -> None:
        del people
        self.people_updates += 1

    def clear(self) -> None:
        return None


class TestPickAndPlaceUseCase(unittest.TestCase):
    def setUp(self) -> None:
        self.marker = MarkerState(marker_id=1, pose_world=Pose(0.3, 0.1, 0.2))
        self.trajectory = _Trajectory(
            joints_positions=((0.0, 0.0, 0.0), (0.1, 0.1, 0.1), (0.2, 0.1, 0.3)),
            joints_velocities=((0.0, 0.0, 0.0), (0.5, 0.2, 0.1), (0.0, 0.0, 0.0)),
        )

    def test_run_once_success_with_visualization(self) -> None:
        robot = _FakeRobot(joints_count=3)
        visualization = _FakeVisualization()
        controller = _FakeController()
        generator = _FakeTrajectoryGenerator(self.trajectory)
        use_case = PickAndPlaceUseCase(
            robot=robot,
            camera=_FakeCamera(),
            perception=_FakePerception((self.marker,)),
            kinematics=_FakeKinematics(),
            visualization=visualization,
            trajectory_generator=generator,
            controller=controller,
            trajectory_duration_s=1.0,
            control_dt_s=0.1,
        )

        result = use_case.run_once()

        self.assertTrue(result.success)
        self.assertEqual(result.reason, "trajectory_executed")
        self.assertEqual(result.executed_steps, 3)
        self.assertEqual(result.target_marker_id, 1)
        self.assertEqual(generator.calls, 1)
        self.assertEqual(controller.calls, 3)
        self.assertEqual(len(robot.velocity_commands), 4)  # 3 control + stop
        self.assertEqual(robot.velocity_commands[-1], (0.0, 0.0, 0.0))
        self.assertEqual(len(robot.step_calls), 4)  # 3 control + final stop step
        self.assertEqual(visualization.marker_updates, 1)
        self.assertEqual(visualization.people_updates, 1)
        self.assertEqual(visualization.reference_updates, 1)
        self.assertEqual(visualization.robot_updates, 3)

    def test_run_once_returns_no_marker_failure(self) -> None:
        robot = _FakeRobot()
        use_case = PickAndPlaceUseCase(
            robot=robot,
            camera=_FakeCamera(),
            perception=_FakePerception(()),
            kinematics=_FakeKinematics(),
            trajectory_duration_s=1.0,
            control_dt_s=0.1,
        )

        result = use_case.run_once()

        self.assertFalse(result.success)
        self.assertEqual(result.reason, "no_marker_detected_with_world_pose")
        self.assertEqual(result.executed_steps, 0)
        self.assertEqual(robot.velocity_commands, [])
        self.assertEqual(len(robot.step_calls), 1)

    def test_run_once_returns_inverse_kinematics_failure(self) -> None:
        robot = _FakeRobot()
        use_case = PickAndPlaceUseCase(
            robot=robot,
            camera=_FakeCamera(),
            perception=_FakePerception((self.marker,)),
            kinematics=_FakeKinematics(fail_inverse=True),
            trajectory_duration_s=1.0,
            control_dt_s=0.1,
        )

        result = use_case.run_once()

        self.assertFalse(result.success)
        self.assertEqual(result.reason, "inverse_kinematics_failed")
        self.assertEqual(result.executed_steps, 0)
        self.assertEqual(robot.velocity_commands, [])
        self.assertEqual(len(robot.step_calls), 1)

    def test_run_once_reports_max_control_steps_reached(self) -> None:
        robot = _FakeRobot()
        use_case = PickAndPlaceUseCase(
            robot=robot,
            camera=_FakeCamera(),
            perception=_FakePerception((self.marker,)),
            kinematics=_FakeKinematics(),
            trajectory_generator=_FakeTrajectoryGenerator(self.trajectory),
            controller=_FakeController(),
            trajectory_duration_s=1.0,
            control_dt_s=0.1,
        )

        result = use_case.run_once(max_control_steps=1)

        self.assertFalse(result.success)
        self.assertEqual(result.reason, "max_control_steps_reached")
        self.assertEqual(result.executed_steps, 1)
        self.assertEqual(len(robot.velocity_commands), 2)  # 1 control + stop
        self.assertEqual(len(robot.step_calls), 2)  # 1 control + final stop step

    def test_target_pose_uses_legacy_gripper_rotation_bins(self) -> None:
        robot = _FakeRobot()
        marker = MarkerState(
            marker_id=2,
            pose_world=Pose(0.3, 0.1, 0.2, roll=0.0, pitch=0.0, yaw=math.radians(80.0)),
        )
        use_case = PickAndPlaceUseCase(
            robot=robot,
            camera=_FakeCamera(),
            perception=_FakePerception((marker,)),
            kinematics=_FakeKinematics(),
            trajectory_generator=_FakeTrajectoryGenerator(
                _Trajectory(
                    joints_positions=((0.0, 0.0, 0.0),),
                    joints_velocities=((0.0, 0.0, 0.0),),
                )
            ),
            controller=_FakeController(),
            trajectory_duration_s=1.0,
            control_dt_s=0.1,
        )

        result = use_case.run_once()

        self.assertTrue(result.success)
        self.assertIsNotNone(result.target_pose)
        target_pose = result.target_pose
        assert target_pose is not None
        self.assertAlmostEqual(target_pose.roll, math.pi, places=8)
        self.assertAlmostEqual(target_pose.pitch, 0.0, places=8)
        self.assertAlmostEqual(target_pose.yaw, math.radians(90.0), places=8)

    def test_run_once_does_single_marker_detection_attempt(self) -> None:
        robot = _FakeRobot()
        perception = _FakePerceptionSequence(((), (self.marker,)))
        use_case = PickAndPlaceUseCase(
            robot=robot,
            camera=_FakeCamera(),
            perception=perception,
            kinematics=_FakeKinematics(),
            trajectory_generator=_FakeTrajectoryGenerator(
                _Trajectory(
                    joints_positions=((0.0, 0.0, 0.0),),
                    joints_velocities=((0.0, 0.0, 0.0),),
                )
            ),
            controller=_FakeController(),
            trajectory_duration_s=1.0,
            control_dt_s=0.1,
        )

        result = use_case.run_once()

        self.assertFalse(result.success)
        self.assertEqual(result.reason, "no_marker_detected_with_world_pose")
        self.assertEqual(perception.calls, 1)
        self.assertEqual(len(robot.step_calls), 1)


if __name__ == "__main__":
    unittest.main()

