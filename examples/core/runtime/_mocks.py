from __future__ import annotations

import numpy as np

from manipulator_framework.core.contracts import (
    CameraInterface,
    ClockInterface,
    ControllerInterface,
    PersonDetectorInterface,
    PlannerInterface,
    RobotInterface,
    TrackerInterface,
)
from manipulator_framework.core.types import (
    CameraFrame,
    CommandMode,
    ControlOutput,
    JointCommand,
    JointState,
    PersonDetection,
    RobotState,
    Trajectory,
    TrajectorySample,
)


class FakeClock(ClockInterface):
    def __init__(self) -> None:
        self._time = 0.0

    def now(self) -> float:
        self._time += 0.1
        return self._time

    def dt(self) -> float:
        pass

    def sleep_until(self, timestamp: float) -> None:
        pass

class FakeRobot(RobotInterface):
    def __init__(self) -> None:
        self.last_command: JointCommand | None = None

    def get_robot_state(self) -> RobotState:
        return RobotState(
            joint_state=JointState(
                positions=np.zeros(7),
                velocities=np.zeros(7),
                joint_names=tuple(f"joint_{i+1}" for i in range(7)),
                timestamp=0.0,
            ),
            timestamp=0.0,
        )

    def send_joint_command(self, command: JointCommand) -> None:
        self.last_command = command

    def send_torque_command(self, command: TorqueCommand) -> None:
        pass

    def get_end_effector_pose(self) -> Pose3D:
        pass

class FakeCamera(CameraInterface):
    def get_frame(self) -> CameraFrame:
        return CameraFrame(
            image=np.zeros((480, 640, 3), dtype=np.uint8),
            camera_id='sim_camera',
            frame_id='camera',
            timestamp=0.0,
            intrinsics=np.array(
                [
                    [600.0, 0.0, 320.0],
                    [0.0, 600.0, 240.0],
                    [0.0, 0.0, 1.0],
                ]
            ),
        )

    def get_intrinsics(self) -> np.ndarray:
        pass

    def get_extrinsics(self) -> Pose3D | None:
        pass

class FakePersonDetector(PersonDetectorInterface):
    def detect_people(self, frame: CameraFrame) -> list[PersonDetection]:
        return []


class FakeTracker(TrackerInterface):
    def update(self, detections, timestamp: float):
        return []

    def reset(self) -> None:
        return None


class FakePlanner(PlannerInterface):
    def plan(self, robot_state: RobotState, tracked_targets) -> Trajectory:
        return Trajectory(
            samples=(
                TrajectorySample(time_from_start=0.0, joint_state=robot_state.joint_state),
                TrajectorySample(
                    time_from_start=0.1,
                    joint_state=JointState(
                        positions=0.1 * np.ones(7),
                        velocities=np.zeros(7),
                        accelerations=np.zeros(7),
                        joint_names=robot_state.joint_state.joint_names,
                        timestamp=0.1,
                    ),
                ),
            ),
            name="fake_reference",
            timestamp=0.0,
        )


class FakeController(ControllerInterface):
    def compute_control(self, robot_state: RobotState, reference: TrajectorySample, dt: float) -> ControlOutput:
        command = JointCommand(
            values=np.asarray(reference.joint_state.positions, dtype=float),
            mode=CommandMode.POSITION,
            joint_names=reference.joint_state.joint_names,
            timestamp=reference.time_from_start,
        )

        return ControlOutput(
            joint_command=command,
            torque_command=None,
            status="ok",
            message="Fake controller output.",
            timestamp=reference.time_from_start,
        )

    def reset(self) -> None:
        return None
