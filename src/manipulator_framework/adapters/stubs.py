from __future__ import annotations

import numpy as np
from typing import Any

from manipulator_framework.core.contracts import (
    RobotInterface, 
    CameraInterface, 
    MarkerDetectorInterface, 
    PoseEstimatorInterface, 
    ObstacleSourceInterface, 
    ObstacleAvoidanceInterface,
    ControllerInterface
)
from manipulator_framework.core.types import (
    RobotState, JointState, Pose3D, CameraFrame, MarkerDetection, 
    ObstacleState, Trajectory, ControlOutput, JointCommand, CommandMode,
    TrajectorySample, TrackedTarget, Detection2D
)

class StubRobot(RobotInterface):
    def get_robot_state(self) -> RobotState:
        return RobotState(
            joint_state=JointState(
                positions=np.zeros(7), 
                velocities=np.zeros(7), 
                joint_names=tuple(f"j{i}" for i in range(7))
            ),
            end_effector_pose=Pose3D(np.zeros(3), np.array([0,0,0,1]), "world"),
            timestamp=0.0
        )
    def send_joint_command(self, command: JointCommand) -> None: pass
    def send_torque_command(self, command: Any) -> None: pass
    def get_end_effector_pose(self) -> Pose3D:
        return Pose3D(np.zeros(3), np.array([0,0,0,1]), "world")

class StubCamera(CameraInterface):
    def get_frame(self) -> CameraFrame:
        return CameraFrame(np.zeros((10,10,3), dtype=np.uint8), "stub", "stub", 0.0)
    def get_intrinsics(self) -> np.ndarray: return np.eye(3)
    def get_extrinsics(self) -> Pose3D: return Pose3D(np.zeros(3), np.array([0,0,0,1]), "world")

class StubMarkerDetector(MarkerDetectorInterface):
    def detect_markers(self, frame: CameraFrame) -> list[MarkerDetection]:
        # Return one marker to allow the pipeline to proceed to PBVS/Avoidance
        det = Detection2D((0,0,10,10), 1.0, timestamp=0.0)
        return [MarkerDetection(marker_id=1, detection=det, timestamp=0.0)]

class StubPoseEstimator(PoseEstimatorInterface):
    def estimate_marker_pose(self, detection: MarkerDetection) -> Pose3D | None:
        return Pose3D(np.zeros(3), np.array([0,0,0,1]), "camera")

    def estimate_person_target(self, detection: Any) -> TrackedTarget | None:
        return None

class StubObstacleSource(ObstacleSourceInterface):
    def get_obstacles(self) -> list[ObstacleState]: return []

class StubObstacleAvoidance(ObstacleAvoidanceInterface):
    def adapt_trajectory(self, reference: Trajectory, obstacles: list[ObstacleState], robot_state: RobotState) -> Trajectory:
        return reference

class StubController(ControllerInterface):
    def compute_control(self, robot_state: RobotState, reference: TrajectorySample, dt: float) -> ControlOutput:
        return ControlOutput(
            joint_command=JointCommand(np.zeros(7), CommandMode.POSITION, tuple(f"j{i}" for i in range(7))),
            status="stub",
            timestamp=0.0
        )
    def reset(self) -> None: pass
