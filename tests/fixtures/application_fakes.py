from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from typing import TYPE_CHECKING

import numpy as np
from manipulator_framework.core.contracts import (
    ClockInterface,
    ExecutionEngineInterface,
    ResultsRepositoryInterface,
    CameraInterface,
    RobotInterface,
    ControllerInterface,
    PersonDetectorInterface,
    PlannerInterface,
    TrackerInterface,
    MarkerDetectorInterface,
    PoseEstimatorInterface,
    ObstacleSourceInterface,
    ObstacleAvoidanceInterface,
)
from manipulator_framework.core.metrics import MetricsSnapshot, ScalarMetric
from manipulator_framework.core.experiments import RunResult
from manipulator_framework.core.runtime import CycleResult, StepResult
from manipulator_framework.core.types import (
    CameraFrame,
    CommandMode,
    ControlOutput,
    Detection2D,
    JointCommand,
    JointState,
    MarkerDetection,
    ObstacleState,
    PersonDetection,
    Pose3D,
    RobotState,
    TorqueCommand,
    TrackedTarget,
    Trajectory,
    TrajectorySample,
    TargetType,
    TrackingStatus,
)

if TYPE_CHECKING:
    from manipulator_framework.core.runtime import RuntimePipeline


class FakeMarkerDetector(MarkerDetectorInterface):
    def detect_markers(self, frame: CameraFrame) -> list[MarkerDetection]:
        return []


class FakePoseEstimator(PoseEstimatorInterface):
    def estimate_marker_pose(self, detection: MarkerDetection) -> Pose3D:
        return Pose3D(
            position=np.zeros(3),
            orientation_quat_xyzw=np.array([0, 0, 0, 1]),
            frame_id="camera_link",
        )

    def estimate_person_target(self, detection: PersonDetection) -> TrackedTarget:
        return TrackedTarget(
            target_id=detection.person_id_hint or "person_0000",
            target_type=TargetType.PERSON,
            status=TrackingStatus.DETECTED,
            confidence=detection.detection.confidence,
            latest_detection=detection.detection,
            estimated_pose=None,
            timestamp=detection.timestamp,
        )


class FakeObstacleSource(ObstacleSourceInterface):
    def get_obstacles(self) -> list[ObstacleState]:
        return []


class FakeObstacleAvoidance(ObstacleAvoidanceInterface):
    def adapt_trajectory(
        self,
        reference: Trajectory,
        obstacles: list[ObstacleState],
        robot_state: RobotState,
    ) -> Trajectory:
        return reference


class FakeClock(ClockInterface):
    """
    Simple deterministic clock for examples and tests.
    """

    def __init__(self, start_time: float = 0.0, step_dt: float = 0.1) -> None:
        self._now = float(start_time)
        self._dt = float(step_dt)

    def now(self) -> float:
        return self._now

    def dt(self) -> float:
        return self._dt

    def sleep_until(self, timestamp: float) -> None:
        if timestamp < self._now:
            raise ValueError("timestamp cannot be earlier than current fake clock time.")
        self._now = float(timestamp)

    def tick(self) -> float:
        """
        Advance the fake clock by one dt step.
        """
        self._now += self._dt
        return self._now


class FakeExecutionEngine(ExecutionEngineInterface):
    """
    Fake execution engine aligned with the real engine contract.
    """

    def __init__(
        self,
        *,
        success: bool = True,
        step_names: tuple[str, ...] = ("sensing", "planning", "control"),
        timestamp: float = 0.0,
        failure_step_index: int | None = None,
    ) -> None:
        self._cycle = 0
        self._success = bool(success)
        self._step_names = tuple(step_names)
        self._timestamp = float(timestamp)
        self._failure_step_index = failure_step_index

    def set_pipeline(self, pipeline: RuntimePipeline) -> None:
        pass

    def step(self) -> CycleResult:
        step_results: list[StepResult] = []

        for index, step_name in enumerate(self._step_names):
            step_success = self._success
            if self._failure_step_index is not None and index == self._failure_step_index:
                step_success = False

            step_results.append(
                StepResult(
                    step_name=step_name,
                    success=step_success,
                    message=(
                        f"{step_name} completed."
                        if step_success
                        else f"{step_name} failed."
                    ),
                    timestamp=self._timestamp,
                    metadata={},
                    metrics={},
                )
            )

            if not step_success:
                break

        overall_success = all(item.success for item in step_results)
        result = CycleResult(
            cycle_index=self._cycle,
            timestamp=self._timestamp,
            success=overall_success,
            observations={"num_steps": len(step_results)},
            commands={},
            metrics_delta={},
            events=tuple(f"{item.step_name}: {item.message}" for item in step_results),
            errors=tuple(item.message for item in step_results if not item.success),
        )
        self._cycle += 1
        return result

    def run(
        self,
        *,
        run_id: str,
        resolved_config: dict[str, Any],
        seed: int,
        num_cycles: int = 1,
        start_time: float | None = None,
        end_time: float | None = None,
    ) -> RunResult:
        if num_cycles <= 0:
            raise ValueError("num_cycles must be greater than zero.")

        results: list[CycleResult] = []
        for _ in range(num_cycles):
            results.append(self.step())

        return RunResult(
            run_id=run_id,
            success=all(item.success for item in results),
            num_cycles=len(results),
            summary={"backend_name": "fake"},
            metrics=MetricsSnapshot(
                scalar_metrics=(
                    ScalarMetric(name="success_rate", value=1.0 if all(item.success for item in results) else 0.0),
                )
            ),
            resolved_config=resolved_config,
            seed=seed,
            start_time=float(start_time or 0.0),
            end_time=float(end_time or 0.0),
            cycle_results=tuple(results),
        )

    def reset(self) -> None:
        self._cycle = 0


@dataclass
class InMemoryResultsRepository(ResultsRepositoryInterface):
    """
    In-memory repository aligned with the consolidated RunResult contract.
    """

    saved_results: list[RunResult] = field(default_factory=list)

    def save_run(self, result: RunResult) -> None:
        self.saved_results.append(result)


class FakeCamera(CameraInterface):
    def get_frame(self) -> CameraFrame:
        return CameraFrame(
            image=np.zeros((480, 640, 3), dtype=np.uint8),
            camera_id="fake_camera",
            frame_id="camera_link",
            timestamp=0.0,
        )

    def get_intrinsics(self) -> np.ndarray:
        return np.eye(3)

    def get_extrinsics(self) -> Pose3D | None:
        return Pose3D(
            position=np.zeros(3),
            orientation_quat_xyzw=np.array([0, 0, 0, 1]),
            frame_id="world",
        )


class FakeRobot(RobotInterface):
    def __init__(self) -> None:
        self.last_command: JointCommand | TorqueCommand | None = None

    def get_robot_state(self) -> RobotState:
        return RobotState(
            joint_state=JointState(
                positions=np.zeros(7),
                velocities=np.zeros(7),
                joint_names=tuple(f"joint_{i}" for i in range(7)),
                timestamp=0.0,
            ),
            end_effector_pose=Pose3D(
                position=np.zeros(3),
                orientation_quat_xyzw=np.array([0, 0, 0, 1]),
                frame_id="world",
            ),
            timestamp=0.0,
        )

    def send_joint_command(self, command: JointCommand) -> None:
        self.last_command = command

    def send_torque_command(self, command: TorqueCommand) -> None:
        self.last_command = command

    def get_end_effector_pose(self) -> Pose3D:
        return Pose3D(
            position=np.zeros(3),
            orientation_quat_xyzw=np.array([0, 0, 0, 1]),
            frame_id="world",
        )


class FakeController(ControllerInterface):
    def compute_control(
        self,
        robot_state: RobotState,
        reference: TrajectorySample,
        dt: float,
    ) -> ControlOutput:
        return ControlOutput(
            joint_command=JointCommand(
                values=np.zeros(7),
                mode=CommandMode.POSITION,
                joint_names=tuple(f"joint_{i}" for i in range(7)),
            ),
            status="ok",
            timestamp=reference.time_from_start,
        )

    def reset(self) -> None:
        pass


class FakePersonDetector(PersonDetectorInterface):
    def detect_people(self, frame: CameraFrame) -> list[PersonDetection]:
        return []


class FakePlanner(PlannerInterface):
    def plan(
        self,
        robot_state: RobotState,
        tracked_targets: list[TrackedTarget],
    ) -> Trajectory:
        # Trajectory must have at least one sample
        return Trajectory(
            samples=(
                TrajectorySample(
                    time_from_start=0.0,
                    joint_state=robot_state.joint_state,
                ),
            )
        )


class FakeTracker(TrackerInterface):
    def update(self, observations: list[TrackedTarget], timestamp: float) -> list[TrackedTarget]:
        return list(observations)

    def reset(self) -> None:
        pass
