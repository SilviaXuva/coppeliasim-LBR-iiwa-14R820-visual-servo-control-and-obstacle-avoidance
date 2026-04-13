from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import math
from numbers import Real
from typing import Callable, Protocol

from ...core.controllers.kinematic.joint_pi import JointPIController
from ...core.models.marker_state import MarkerState
from ...core.models.pose import Pose
from ...core.ports.camera_port import CameraPort
from ...core.ports.dynamics_port import DynamicsPort
from ...core.ports.kinematics_port import KinematicsPort
from ...core.ports.perception_port import PerceptionPort
from ...core.ports.robot_port import RobotPort
from ...core.ports.visualization_port import VisualizationPort
from ...core.trajectory.quintic_trajectory import QuinticJointTrajectory
from ...core.controllers.dynamic.joint_pd import JointPDController


@dataclass(slots=True, frozen=True)
class PickAndPlaceResult:
    success: bool
    reason: str
    markers_detected: int
    executed_steps: int
    target_marker_id: int | None = None
    target_pose: Pose | None = None


class TrajectoryLike(Protocol):
    joints_positions: tuple[tuple[float, ...], ...]
    joints_velocities: tuple[tuple[float, ...], ...]


class TrajectoryGeneratorLike(Protocol):
    def generate(
        self,
        q0: tuple[float, ...],
        qf: tuple[float, ...],
        tf: float,
        dt: float,
    ) -> TrajectoryLike: ...


class ControlResultLike(Protocol):
    joints_velocities: tuple[float, ...]


class JointControllerLike(Protocol):
    def update(
        self,
        joints_positions: tuple[float, ...],
        joints_positions_ref: tuple[float, ...],
        joints_velocities_ref: tuple[float, ...] | None = None,
        dt: float = 0.0,
    ) -> ControlResultLike: ...


GainValue = Real | Sequence[float] | Sequence[Sequence[float]]


class PickAndPlaceUseCase:
    """
    First vertical flow orchestration:
    camera -> perception -> target pose -> kinematics -> trajectory/control -> robot
    """

    def __init__(
        self,
        robot: RobotPort,
        camera: CameraPort,
        perception: PerceptionPort,
        kinematics: KinematicsPort,
        visualization: VisualizationPort | None = None,
        trajectory_generator: TrajectoryGeneratorLike | None = None,
        controller: JointControllerLike | str | None = None,
        dynamics: DynamicsPort | None = None,
        kp: GainValue = 1.0,
        ki: GainValue = 0.0,
        kv: GainValue = 0.0,
        joints_torques_min: Sequence[float] | None = None,
        joints_torques_max: Sequence[float] | None = None,
        trajectory_duration_s: float = 2.0,
        control_dt_s: float = 0.05,
        target_height_offset_m: float = 0.0,
        use_legacy_gripper_rotation: bool = True,
        marker_selector: Callable[[tuple[MarkerState, ...]], MarkerState | None]
        | None = None,
    ) -> None:
        self._robot = robot
        self._camera = camera
        self._perception = perception
        self._kinematics = kinematics
        self._visualization = visualization

        self._trajectory_generator = (
            trajectory_generator
            if trajectory_generator is not None
            else QuinticJointTrajectory()
        )
        self._controller: JointControllerLike | None = None
        self._controller_strategy: str | None = None

        if isinstance(controller, str):
            self._controller_strategy = controller
        else:
            self._controller = controller

        self._dynamics = dynamics
        self._kp = self._normalize_gain(kp, "kp")
        self._ki = self._normalize_gain(ki, "ki")
        self._kv = self._normalize_gain(kv, "kv")
        self._joints_torques_min = joints_torques_min
        self._joints_torques_max = joints_torques_max

        self._trajectory_duration_s = float(trajectory_duration_s)
        self._control_dt_s = float(control_dt_s)
        if self._trajectory_duration_s <= 0.0:
            raise ValueError("`trajectory_duration_s` must be greater than zero.")
        if self._control_dt_s <= 0.0:
            raise ValueError("`control_dt_s` must be greater than zero.")
        self._target_height_offset_m = float(target_height_offset_m)
        self._use_legacy_gripper_rotation = bool(use_legacy_gripper_rotation)
        self._marker_selector = (
            marker_selector if marker_selector is not None else self._default_marker_selector
        )

    def run_once(self, max_control_steps: int | None = None) -> PickAndPlaceResult:
        marker, markers = self._detect_target_marker()
        if marker is None:
            return PickAndPlaceResult(
                success=False,
                reason="no_marker_detected_with_world_pose",
                markers_detected=len(markers),
                executed_steps=0,
            )

        target_pose = self._build_target_pose(marker)

        initial_state = self._robot.get_state()
        self._ensure_controller(joints_count=len(initial_state.joints_positions))
        controller = self._controller
        if controller is None:
            raise RuntimeError("Joint PI controller was not initialized.")

        try:
            goal_joints = self._kinematics.inverse_kinematics(
                target_pose=target_pose,
                seed_joints_positions=initial_state.joints_positions,
            )
        except Exception:
            self._robot.step(reference_xyz=target_pose.xyz)
            return PickAndPlaceResult(
                success=False,
                reason="inverse_kinematics_failed",
                markers_detected=len(markers),
                executed_steps=0,
                target_marker_id=marker.marker_id,
                target_pose=target_pose,
            )

        trajectory = self._trajectory_generator.generate(
            q0=initial_state.joints_positions,
            qf=goal_joints,
            tf=self._trajectory_duration_s,
            dt=self._control_dt_s,
        )

        if self._visualization is not None:
            reference_path = tuple(
                self._kinematics.forward_kinematics(joints_positions=q_ref)
                for q_ref in trajectory.joints_positions
            )
            self._visualization.update_reference_path(reference_path)

        executed_steps = 0
        for q_ref, dq_ref in zip(
            trajectory.joints_positions,
            trajectory.joints_velocities,
        ):
            if max_control_steps is not None and executed_steps >= max_control_steps:
                break

            state = self._robot.get_state()
            kwargs = {
                "joints_positions": state.joints_positions,
                "joints_positions_ref": q_ref,
                "joints_velocities_ref": dq_ref,
                "dt": self._control_dt_s,
            }
            if isinstance(controller, JointPDController):
                kwargs["joints_velocities"] = state.joints_velocities

            control = controller.update(**kwargs)
            self._robot.command_joints_velocities(control.joints_velocities)
            self._robot.step(reference_xyz=target_pose.xyz)

            if self._visualization is not None:
                self._visualization.update_robot_state(state)

            executed_steps += 1

        self._robot.command_joints_velocities(
            tuple(0.0 for _ in initial_state.joints_positions)
        )
        self._robot.step(reference_xyz=target_pose.xyz)

        completed_trajectory = executed_steps == len(trajectory.joints_positions)
        return PickAndPlaceResult(
            success=completed_trajectory,
            reason=(
                "trajectory_executed"
                if completed_trajectory
                else "max_control_steps_reached"
            ),
            markers_detected=len(markers),
            executed_steps=executed_steps,
            target_marker_id=marker.marker_id,
            target_pose=target_pose,
        )

    def shutdown(self) -> None:
        stop_method = getattr(self._robot, "stop", None)
        if callable(stop_method):
            try:
                stop_method()
            except Exception:
                pass

        if self._visualization is None:
            return
        clear_method = getattr(self._visualization, "clear", None)
        if callable(clear_method):
            try:
                clear_method()
            except Exception:
                pass

    def _detect_target_marker(self) -> tuple[MarkerState | None, tuple[MarkerState, ...]]:
        frame = self._camera.capture_frame()
        markers = tuple(self._perception.detect_markers(frame))
        people = tuple(self._perception.detect_people(frame))

        if self._visualization is not None:
            self._visualization.update_markers(markers)
            self._visualization.update_people(people)

        marker = self._marker_selector(markers)
        if marker is not None:
            return marker, markers

        self._robot.step()
        return None, markers

    def _ensure_controller(self, joints_count: int) -> None:
        if self._controller is not None:
            return

        strategy = self._controller_strategy or "kinematic_pi"

        if strategy == "kinematic_pi":
            self._controller = JointPIController(
                kp=self._kp,
                ki=self._ki,
                joints_count=joints_count,
            )
        elif strategy == "dynamic_pd":
            if self._dynamics is None:
                raise ValueError("`dynamics` must be provided when using dynamic PD controller.")
            if self._joints_torques_min is None or self._joints_torques_max is None:
                raise ValueError("`joints_torques_min` and `joints_torques_max` must be provided when using dynamic PD controller.")
            self._controller = JointPDController(
                dynamics=self._dynamics,
                kp=self._kp,
                kv=self._kv,
                joints_count=joints_count,
                joints_torques_min=self._joints_torques_min,
                joints_torques_max=self._joints_torques_max,
            )
        else:
            raise ValueError(f"Unknown controller strategy: {strategy}")


    def _build_target_pose(self, marker: MarkerState) -> Pose:
        if marker.pose_world is None:
            raise ValueError("Target marker must have a world pose.")
        marker_pose = marker.pose_world
        target_pose = Pose(
            x=marker_pose.x,
            y=marker_pose.y,
            z=marker_pose.z + self._target_height_offset_m,
            roll=marker_pose.roll,
            pitch=marker_pose.pitch,
            yaw=marker_pose.yaw,
        )
        if self._use_legacy_gripper_rotation:
            return self._apply_legacy_gripper_rotation(target_pose)
        return target_pose

    def _apply_legacy_gripper_rotation(self, target_pose: Pose) -> Pose:
        """
        Mirrors the yaw-bin strategy from legacy/7.test_onlyRandomGripperRotation.py.
        """
        yaw_deg = math.degrees(target_pose.yaw)
        snapped_yaw_deg = self._legacy_snap_yaw_deg(yaw_deg)
        return Pose(
            x=target_pose.x,
            y=target_pose.y,
            z=target_pose.z,
            roll=math.pi,
            pitch=0.0,
            yaw=math.radians(snapped_yaw_deg),
        )

    @staticmethod
    def _legacy_snap_yaw_deg(yaw_deg: float) -> float:
        if yaw_deg <= -135.0:
            return 0.0
        if yaw_deg <= -90.0:
            return -90.0
        if yaw_deg <= -45.0:
            return 90.0
        if yaw_deg < 0.0:
            return 180.0
        if yaw_deg < 45.0:
            return 0.0
        if yaw_deg < 90.0:
            return 90.0
        if yaw_deg < 135.0:
            return -90.0
        return 0.0

    @staticmethod
    def _default_marker_selector(markers: tuple[MarkerState, ...]) -> MarkerState | None:
        for marker in markers:
            if marker.pose_world is not None:
                return marker
        return None

    @staticmethod
    def _normalize_gain(
        gain: GainValue,
        gain_name: str,
    ) -> float | tuple[float, ...] | tuple[tuple[float, ...], ...]:
        if isinstance(gain, Real):
            return float(gain)
        if isinstance(gain, (str, bytes)):
            raise ValueError(
                f"`{gain_name}` must contain numeric values."
            )

        try:
            gain_values = tuple(gain)
        except TypeError:
            raise ValueError(
                f"`{gain_name}` must be scalar, vector or square matrix."
            ) from None

        if len(gain_values) == 0:
            raise ValueError(f"`{gain_name}` must not be empty.")

        if isinstance(gain_values[0], Real):
            try:
                return tuple(float(value) for value in gain_values)
            except (TypeError, ValueError):
                raise ValueError(
                    f"`{gain_name}` must contain numeric values."
                ) from None

        matrix_rows: list[tuple[float, ...]] = []
        for row in gain_values:
            if isinstance(row, (str, bytes)):
                raise ValueError(
                    f"`{gain_name}` must contain numeric values."
                ) from None
            try:
                matrix_rows.append(tuple(float(value) for value in row))  # type: ignore[arg-type]
            except (TypeError, ValueError):
                raise ValueError(
                    f"`{gain_name}` must contain numeric values."
                ) from None
        return tuple(matrix_rows)
