from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import math
from numbers import Real
from typing import Callable, Protocol

from ...core.models.marker_state import MarkerState
from ...core.models.pose import Pose
from ...core.ports.camera_port import CameraPort
from ...core.ports.conveyor_port import ConveyorPort
from ...core.ports.dynamics_port import DynamicsPort
from ...core.ports.gripper_port import GripperPort
from ...core.ports.kinematics_port import KinematicsPort
from ...core.ports.object_port import ObjectPort
from ...core.ports.perception_port import PerceptionPort
from ...core.ports.robot_port import RobotPort
from ...core.ports.visualization_port import VisualizationPort
from ...core.trajectory.quintic_trajectory import QuinticJointTrajectory
from ...infrastructure.logging import get_logger


@dataclass(slots=True, frozen=True)
class PickAndPlaceResult:
    success: bool
    reason: str
    markers_detected: int
    executed_steps: int
    target_marker_id: int | None = None
    target_pose: Pose | None = None
    pick_success: bool = False
    place_success: bool = False
    termination_reason: str = ""
    completed_phases: tuple[str, ...] = ()
    step_metrics: tuple[dict[str, float | int | str | None], ...] = ()


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
_HOME_JOINTS_RAD = tuple(
    math.radians(value)
    for value in (0.0, 0.0, 0.0, 90.0, 0.0, -90.0, 90.0)
)
_LOGGER = get_logger(__name__)


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
        gripper: GripperPort | None = None,
        tracked_object: ObjectPort | None = None,
        conveyor: ConveyorPort | None = None,
        place_pose: Pose | None = None,
        pre_grasp_offset: Sequence[float] = (0.0, 0.0, 0.10),
        lift_offset: Sequence[float] = (0.0, 0.0, 0.10),
        retreat_offset: Sequence[float] = (0.0, 0.0, 0.10),
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
        self._gripper = gripper
        self._tracked_object = tracked_object
        self._conveyor = conveyor
        self._place_pose = place_pose
        self._pre_grasp_offset = self._normalize_xyz_offset(
            pre_grasp_offset,
            "pre_grasp_offset",
        )
        self._lift_offset = self._normalize_xyz_offset(
            lift_offset,
            "lift_offset",
        )
        self._retreat_offset = self._normalize_xyz_offset(
            retreat_offset,
            "retreat_offset",
        )
        self._marker_selector = (
            marker_selector if marker_selector is not None else self._default_marker_selector
        )

    def run_once(self, max_control_steps: int | None = None) -> PickAndPlaceResult:
        return self.execute(max_control_steps=max_control_steps)

    def execute(self, max_control_steps: int | None = None) -> PickAndPlaceResult:
        _LOGGER.info(
            "Pick-and-place execution started: full_flow=%s max_control_steps=%s",
            self._supports_full_pick_and_place(),
            max_control_steps,
        )
        self._safe_stop_conveyor()
        try:
            current_state = self._robot.get_state()
            self._ensure_controller(joints_count=len(current_state.joints_positions))
            controller = self._controller
            if controller is None:
                raise RuntimeError("Joint PI controller was not initialized.")

            if not self._supports_full_pick_and_place():
                return self._execute_approach_only(
                    controller=controller,
                    max_control_steps=max_control_steps,
                )
            return self._execute_full_pick_and_place(
                controller=controller,
                max_control_steps=max_control_steps,
            )
        finally:
            self._safe_start_conveyor()

    def _execute_approach_only(
        self,
        *,
        controller: JointControllerLike,
        max_control_steps: int | None,
    ) -> PickAndPlaceResult:
        _LOGGER.info("Target detection started.")
        marker, markers = self._detect_target()
        if marker is None:
            _LOGGER.warning("Target detection failed: no marker with world pose.")
            return self._failure_result(
                termination_reason="no_marker_detected_with_world_pose",
                markers_detected=len(markers),
                executed_steps=0,
                target_marker_id=None,
                target_pose=None,
                completed_phases=(),
                step_metrics=(),
                pick_success=False,
                place_success=False,
            )

        grasp_pose = self._compute_grasp_pose(marker)
        _LOGGER.info(
            "Target detection succeeded: markers_detected=%s target_marker_id=%s",
            len(markers),
            marker.marker_id,
        )
        success, reason, executed_steps, rows = self._move_to_pose(
            controller=controller,
            target_pose=grasp_pose,
            target_marker_id=marker.marker_id,
            phase_name="approach_target",
            max_control_steps=max_control_steps,
            step_index_offset=0,
        )
        if not success:
            _LOGGER.warning(
                "Approach target failed: reason=%s executed_steps=%s target_marker_id=%s",
                reason,
                executed_steps,
                marker.marker_id,
            )
            return self._failure_result(
                termination_reason=reason,
                markers_detected=len(markers),
                executed_steps=executed_steps,
                target_marker_id=marker.marker_id,
                target_pose=grasp_pose,
                completed_phases=("detect_target",),
                step_metrics=tuple(rows),
                pick_success=False,
                place_success=False,
            )

        _LOGGER.info(
            "Approach target finished: executed_steps=%s target_marker_id=%s",
            executed_steps,
            marker.marker_id,
        )
        return self._success_result(
            termination_reason="trajectory_executed",
            markers_detected=len(markers),
            executed_steps=executed_steps,
            target_marker_id=marker.marker_id,
            target_pose=grasp_pose,
            completed_phases=("detect_target", "approach_target"),
            step_metrics=tuple(rows),
            pick_success=False,
            place_success=False,
        )

    def _execute_full_pick_and_place(
        self,
        *,
        controller: JointControllerLike,
        max_control_steps: int | None,
    ) -> PickAndPlaceResult:
        if self._gripper is None or self._tracked_object is None or self._place_pose is None:
            return self._failure_result(
                termination_reason="full_pick_and_place_not_configured",
                markers_detected=0,
                executed_steps=0,
                target_marker_id=None,
                target_pose=None,
                completed_phases=(),
                step_metrics=(),
                pick_success=False,
                place_success=False,
            )

        executed_steps = 0
        remaining_steps = max_control_steps
        step_metrics: list[dict[str, float | int | str | None]] = []
        completed_phases: list[str] = []
        pick_success = False
        place_success = False
        target_pose: Pose | None = None
        target_marker_id: int | None = None
        markers_detected = 0

        self._log_phase_started("moving to home")
        success, reason, used_steps, rows = self._move_to_home(
            controller=controller,
            max_control_steps=remaining_steps,
            step_index_offset=executed_steps,
            phase_name="move_home_start",
        )
        executed_steps += used_steps
        step_metrics.extend(rows)
        remaining_steps = self._remaining_steps(remaining_steps, used_steps)
        if not success:
            self._log_phase_failed("moving to home", reason, executed_steps, target_marker_id)
            return self._failure_result(
                termination_reason=reason,
                markers_detected=markers_detected,
                executed_steps=executed_steps,
                target_marker_id=target_marker_id,
                target_pose=target_pose,
                completed_phases=tuple(completed_phases),
                step_metrics=tuple(step_metrics),
                pick_success=pick_success,
                place_success=place_success,
            )
        completed_phases.append("move_home_start")

        _LOGGER.info("Target detection started.")
        marker, markers = self._detect_target()
        markers_detected = len(markers)
        if marker is None:
            _LOGGER.warning("Target detection failed: no marker with world pose.")
            return self._failure_result(
                termination_reason="no_marker_detected_with_world_pose",
                markers_detected=markers_detected,
                executed_steps=executed_steps,
                target_marker_id=target_marker_id,
                target_pose=target_pose,
                completed_phases=tuple(completed_phases),
                step_metrics=tuple(step_metrics),
                pick_success=pick_success,
                place_success=place_success,
            )
        completed_phases.append("detect_target")
        _LOGGER.info(
            "Target detection succeeded: markers_detected=%s target_marker_id=%s",
            markers_detected,
            marker.marker_id,
        )

        target_marker_id = marker.marker_id
        target_pose = self._compute_grasp_pose(marker)
        pre_grasp_pose = self._compute_offset_pose(target_pose, self._pre_grasp_offset)

        self._log_phase_started("pre-grasp")
        success, reason, used_steps, rows = self._move_to_pose(
            controller=controller,
            target_pose=pre_grasp_pose,
            target_marker_id=target_marker_id,
            phase_name="move_pre_grasp",
            max_control_steps=remaining_steps,
            step_index_offset=executed_steps,
        )
        executed_steps += used_steps
        step_metrics.extend(rows)
        remaining_steps = self._remaining_steps(remaining_steps, used_steps)
        if not success:
            self._log_phase_failed("pre-grasp", reason, executed_steps, target_marker_id)
            return self._failure_result(
                termination_reason=reason,
                markers_detected=markers_detected,
                executed_steps=executed_steps,
                target_marker_id=target_marker_id,
                target_pose=target_pose,
                completed_phases=tuple(completed_phases),
                step_metrics=tuple(step_metrics),
                pick_success=pick_success,
                place_success=place_success,
            )
        completed_phases.append("move_pre_grasp")

        self._log_phase_started("grasp approach")
        success, reason, used_steps, rows = self._move_to_pose(
            controller=controller,
            target_pose=target_pose,
            target_marker_id=target_marker_id,
            phase_name="move_grasp",
            max_control_steps=remaining_steps,
            step_index_offset=executed_steps,
        )
        executed_steps += used_steps
        step_metrics.extend(rows)
        remaining_steps = self._remaining_steps(remaining_steps, used_steps)
        if not success:
            self._log_phase_failed("grasp approach", reason, executed_steps, target_marker_id)
            return self._failure_result(
                termination_reason=reason,
                markers_detected=markers_detected,
                executed_steps=executed_steps,
                target_marker_id=target_marker_id,
                target_pose=target_pose,
                completed_phases=tuple(completed_phases),
                step_metrics=tuple(step_metrics),
                pick_success=pick_success,
                place_success=place_success,
            )
        completed_phases.append("move_grasp")

        self._log_phase_started("grasp")
        self._gripper.open()
        if not self._grasp_object():
            self._log_phase_failed("grasp", "grasp_failed", executed_steps, target_marker_id)
            return self._failure_result(
                termination_reason="grasp_failed",
                markers_detected=markers_detected,
                executed_steps=executed_steps,
                target_marker_id=target_marker_id,
                target_pose=target_pose,
                completed_phases=tuple(completed_phases),
                step_metrics=tuple(step_metrics),
                pick_success=False,
                place_success=False,
            )
        completed_phases.append("grasp")
        _LOGGER.info("Grasp completed: target_marker_id=%s", target_marker_id)

        self._log_phase_started("attach")
        try:
            self._tracked_object.attach_to_gripper()
        except Exception:
            self._safe_release_and_detach()
            self._log_phase_failed(
                "attach",
                "attach_to_gripper_failed",
                executed_steps,
                target_marker_id,
            )
            return self._failure_result(
                termination_reason="attach_to_gripper_failed",
                markers_detected=markers_detected,
                executed_steps=executed_steps,
                target_marker_id=target_marker_id,
                target_pose=target_pose,
                completed_phases=tuple(completed_phases),
                step_metrics=tuple(step_metrics),
                pick_success=False,
                place_success=False,
            )
        completed_phases.append("attach")
        pick_success = True
        _LOGGER.info("Attach completed: target_marker_id=%s", target_marker_id)

        lift_pose = self._compute_offset_pose(target_pose, self._lift_offset)
        self._log_phase_started("lift")
        success, reason, used_steps, rows = self._move_to_pose(
            controller=controller,
            target_pose=lift_pose,
            target_marker_id=target_marker_id,
            phase_name="lift",
            max_control_steps=remaining_steps,
            step_index_offset=executed_steps,
        )
        executed_steps += used_steps
        step_metrics.extend(rows)
        remaining_steps = self._remaining_steps(remaining_steps, used_steps)
        if not success:
            self._safe_release_and_detach()
            self._log_phase_failed("lift", reason, executed_steps, target_marker_id)
            return self._failure_result(
                termination_reason=reason,
                markers_detected=markers_detected,
                executed_steps=executed_steps,
                target_marker_id=target_marker_id,
                target_pose=target_pose,
                completed_phases=tuple(completed_phases),
                step_metrics=tuple(step_metrics),
                pick_success=pick_success,
                place_success=False,
            )
        completed_phases.append("lift")

        pre_place_pose = self._compute_offset_pose(self._place_pose, self._pre_grasp_offset)
        self._log_phase_started("place")
        success, reason, used_steps, rows = self._move_to_pose(
            controller=controller,
            target_pose=pre_place_pose,
            target_marker_id=target_marker_id,
            phase_name="move_pre_place",
            max_control_steps=remaining_steps,
            step_index_offset=executed_steps,
        )
        executed_steps += used_steps
        step_metrics.extend(rows)
        remaining_steps = self._remaining_steps(remaining_steps, used_steps)
        if not success:
            self._safe_release_and_detach()
            self._log_phase_failed("place", reason, executed_steps, target_marker_id)
            return self._failure_result(
                termination_reason=reason,
                markers_detected=markers_detected,
                executed_steps=executed_steps,
                target_marker_id=target_marker_id,
                target_pose=target_pose,
                completed_phases=tuple(completed_phases),
                step_metrics=tuple(step_metrics),
                pick_success=pick_success,
                place_success=False,
            )
        completed_phases.append("move_pre_place")

        success, reason, used_steps, rows = self._move_to_pose(
            controller=controller,
            target_pose=self._place_pose,
            target_marker_id=target_marker_id,
            phase_name="move_place",
            max_control_steps=remaining_steps,
            step_index_offset=executed_steps,
        )
        executed_steps += used_steps
        step_metrics.extend(rows)
        remaining_steps = self._remaining_steps(remaining_steps, used_steps)
        if not success:
            self._safe_release_and_detach()
            self._log_phase_failed("place", reason, executed_steps, target_marker_id)
            return self._failure_result(
                termination_reason=reason,
                markers_detected=markers_detected,
                executed_steps=executed_steps,
                target_marker_id=target_marker_id,
                target_pose=target_pose,
                completed_phases=tuple(completed_phases),
                step_metrics=tuple(step_metrics),
                pick_success=pick_success,
                place_success=False,
            )
        completed_phases.append("move_place")

        self._log_phase_started("release")
        self._release_object()
        completed_phases.append("release")
        try:
            self._tracked_object.detach_from_gripper()
        except Exception:
            self._log_phase_failed(
                "release",
                "detach_from_gripper_failed",
                executed_steps,
                target_marker_id,
            )
            return self._failure_result(
                termination_reason="detach_from_gripper_failed",
                markers_detected=markers_detected,
                executed_steps=executed_steps,
                target_marker_id=target_marker_id,
                target_pose=target_pose,
                completed_phases=tuple(completed_phases),
                step_metrics=tuple(step_metrics),
                pick_success=pick_success,
                place_success=False,
            )
        completed_phases.append("detach")
        place_success = True
        _LOGGER.info("Release completed: target_marker_id=%s", target_marker_id)

        retreat_pose = self._compute_offset_pose(self._place_pose, self._retreat_offset)
        self._log_phase_started("retreat")
        success, reason, used_steps, rows = self._move_to_pose(
            controller=controller,
            target_pose=retreat_pose,
            target_marker_id=target_marker_id,
            phase_name="retreat",
            max_control_steps=remaining_steps,
            step_index_offset=executed_steps,
        )
        executed_steps += used_steps
        step_metrics.extend(rows)
        remaining_steps = self._remaining_steps(remaining_steps, used_steps)
        if not success:
            self._log_phase_failed("retreat", reason, executed_steps, target_marker_id)
            return self._failure_result(
                termination_reason=reason,
                markers_detected=markers_detected,
                executed_steps=executed_steps,
                target_marker_id=target_marker_id,
                target_pose=target_pose,
                completed_phases=tuple(completed_phases),
                step_metrics=tuple(step_metrics),
                pick_success=pick_success,
                place_success=place_success,
            )
        completed_phases.append("retreat")

        self._log_phase_started("moving to home")
        success, reason, used_steps, rows = self._move_to_home(
            controller=controller,
            max_control_steps=remaining_steps,
            step_index_offset=executed_steps,
            phase_name="move_home_end",
        )
        executed_steps += used_steps
        step_metrics.extend(rows)
        if not success:
            self._log_phase_failed("moving to home", reason, executed_steps, target_marker_id)
            return self._failure_result(
                termination_reason=reason,
                markers_detected=markers_detected,
                executed_steps=executed_steps,
                target_marker_id=target_marker_id,
                target_pose=target_pose,
                completed_phases=tuple(completed_phases),
                step_metrics=tuple(step_metrics),
                pick_success=pick_success,
                place_success=place_success,
            )
        completed_phases.append("move_home_end")

        _LOGGER.info(
            "Pick-and-place completed: executed_steps=%s target_marker_id=%s",
            executed_steps,
            target_marker_id,
        )
        return self._success_result(
            termination_reason="pick_and_place_completed",
            markers_detected=markers_detected,
            executed_steps=executed_steps,
            target_marker_id=target_marker_id,
            target_pose=target_pose,
            completed_phases=tuple(completed_phases),
            step_metrics=tuple(step_metrics),
            pick_success=pick_success,
            place_success=place_success,
        )

    def _supports_full_pick_and_place(self) -> bool:
        return (
            self._gripper is not None
            and self._tracked_object is not None
            and self._place_pose is not None
        )

    def _move_to_home(
        self,
        *,
        controller: JointControllerLike,
        max_control_steps: int | None,
        step_index_offset: int,
        phase_name: str,
    ) -> tuple[bool, str, int, list[dict[str, float | int | str | None]]]:
        current_state = self._robot.get_state()
        if len(current_state.joints_positions) != len(_HOME_JOINTS_RAD):
            _LOGGER.warning("Moving to home failed: home joints mismatch.")
            return False, "home_joints_mismatch", 0, []
        return self._move_to_joints(
            controller=controller,
            target_joints=_HOME_JOINTS_RAD,
            target_marker_id=None,
            phase_name=phase_name,
            max_control_steps=max_control_steps,
            step_index_offset=step_index_offset,
        )

    def _move_to_pose(
        self,
        *,
        controller: JointControllerLike,
        target_pose: Pose,
        target_marker_id: int | None,
        phase_name: str,
        max_control_steps: int | None,
        step_index_offset: int,
    ) -> tuple[bool, str, int, list[dict[str, float | int | str | None]]]:
        return self._execute_motion(
            controller=controller,
            target_pose=target_pose,
            target_marker_id=target_marker_id,
            phase_name=phase_name,
            max_control_steps=max_control_steps,
            step_index_offset=step_index_offset,
        )

    def _move_to_joints(
        self,
        *,
        controller: JointControllerLike,
        target_joints: Sequence[float],
        target_marker_id: int | None,
        phase_name: str,
        max_control_steps: int | None,
        step_index_offset: int,
    ) -> tuple[bool, str, int, list[dict[str, float | int | str | None]]]:
        return self._execute_joint_motion(
            controller=controller,
            target_joints=target_joints,
            target_marker_id=target_marker_id,
            phase_name=phase_name,
            max_control_steps=max_control_steps,
            step_index_offset=step_index_offset,
        )

    def _execute_motion(
        self,
        *,
        controller: JointControllerLike,
        target_pose: Pose,
        target_marker_id: int | None,
        phase_name: str,
        max_control_steps: int | None,
        step_index_offset: int,
    ) -> tuple[bool, str, int, list[dict[str, float | int | str | None]]]:
        state_at_start = self._robot.get_state()
        try:
            goal_joints = self._kinematics.inverse_kinematics(
                target_pose=target_pose,
                seed_joints_positions=state_at_start.joints_positions,
            )
        except Exception:
            _LOGGER.warning(
                "Motion planning failed: inverse kinematics failed for phase=%s target_marker_id=%s",
                phase_name,
                target_marker_id,
            )
            self._robot.step(reference_xyz=target_pose.xyz)
            return False, "inverse_kinematics_failed", 0, []

        trajectory = self._trajectory_generator.generate(
            q0=state_at_start.joints_positions,
            qf=goal_joints,
            tf=self._trajectory_duration_s,
            dt=self._control_dt_s,
        )

        return self._execute_trajectory(
            controller=controller,
            trajectory=trajectory,
            reference_xyz=target_pose.xyz,
            target_marker_id=target_marker_id,
            phase_name=phase_name,
            max_control_steps=max_control_steps,
            step_index_offset=step_index_offset,
        )

    def _execute_joint_motion(
        self,
        *,
        controller: JointControllerLike,
        target_joints: Sequence[float],
        target_marker_id: int | None,
        phase_name: str,
        max_control_steps: int | None,
        step_index_offset: int,
    ) -> tuple[bool, str, int, list[dict[str, float | int | str | None]]]:
        state_at_start = self._robot.get_state()
        target_joints_tuple = tuple(float(value) for value in target_joints)
        if len(target_joints_tuple) != len(state_at_start.joints_positions):
            return False, "home_joints_mismatch", 0, []

        trajectory = self._trajectory_generator.generate(
            q0=state_at_start.joints_positions,
            qf=target_joints_tuple,
            tf=self._trajectory_duration_s,
            dt=self._control_dt_s,
        )
        return self._execute_trajectory(
            controller=controller,
            trajectory=trajectory,
            reference_xyz=None,
            target_marker_id=target_marker_id,
            phase_name=phase_name,
            max_control_steps=max_control_steps,
            step_index_offset=step_index_offset,
        )

    def _execute_trajectory(
        self,
        *,
        controller: JointControllerLike,
        trajectory: TrajectoryLike,
        reference_xyz: tuple[float, float, float] | None,
        target_marker_id: int | None,
        phase_name: str,
        max_control_steps: int | None,
        step_index_offset: int,
    ) -> tuple[bool, str, int, list[dict[str, float | int | str | None]]]:
        if self._visualization is not None:
            reference_path = tuple(
                self._kinematics.forward_kinematics(joints_positions=q_ref)
                for q_ref in trajectory.joints_positions
            )
            self._visualization.update_reference_path(reference_path)

        executed_steps = 0
        step_metrics: list[dict[str, float | int | str | None]] = []
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
            if self._controller_requires_joints_velocities(controller):
                kwargs["joints_velocities"] = state.joints_velocities

            control = controller.update(**kwargs)
            self._robot.command_joints_velocities(control.joints_velocities)
            self._robot.step(reference_xyz=reference_xyz)

            if self._visualization is not None:
                self._visualization.update_robot_state(state)

            step_index = step_index_offset + executed_steps + 1
            q_error = tuple(
                float(q_ref_i - q_i)
                for q_ref_i, q_i in zip(q_ref, state.joints_positions)
            )
            tau_tuple = self._extract_numeric_tuple(
                getattr(control, "joints_torques", None)
            )
            tau_sat_count = 0
            if (
                tau_tuple is not None
                and self._joints_torques_min is not None
                and self._joints_torques_max is not None
            ):
                tau_sat_count = self._count_saturated(
                    tau_tuple=tau_tuple,
                    tau_min=self._joints_torques_min,
                    tau_max=self._joints_torques_max,
                )

            step_metrics.append(
                {
                    "step_index": step_index,
                    "t_s": step_index * self._control_dt_s,
                    "phase": phase_name,
                    "controller": self._controller_name(controller),
                    "target_marker_id": target_marker_id,
                    "q_error_l2": self._norm_l2(q_error),
                    "q_error_linf": self._norm_linf(q_error),
                    "dq_ref_l2": self._norm_l2(dq_ref),
                    "dq_cmd_l2": self._norm_l2(control.joints_velocities),
                    "dq_meas_l2": self._norm_l2(state.joints_velocities),
                    "tau_cmd_l2": None if tau_tuple is None else self._norm_l2(tau_tuple),
                    "tau_cmd_max_abs": (
                        None if tau_tuple is None else self._max_abs(tau_tuple)
                    ),
                    "tau_saturated_count": tau_sat_count,
                }
            )

            executed_steps += 1

        state_at_stop = self._robot.get_state()
        self._robot.command_joints_velocities(
            tuple(0.0 for _ in state_at_stop.joints_positions)
        )
        self._robot.step(reference_xyz=reference_xyz)

        completed_trajectory = executed_steps == len(trajectory.joints_positions)
        if completed_trajectory:
            return True, "trajectory_executed", executed_steps, step_metrics
        _LOGGER.warning(
            "Trajectory interrupted: phase=%s reason=max_control_steps_reached executed_steps=%s",
            phase_name,
            executed_steps,
        )
        return False, "max_control_steps_reached", executed_steps, step_metrics

    @staticmethod
    def _log_phase_started(phase_name: str) -> None:
        _LOGGER.info("%s started.", phase_name.capitalize())

    @staticmethod
    def _log_phase_failed(
        phase_name: str,
        reason: str,
        executed_steps: int,
        target_marker_id: int | None,
    ) -> None:
        _LOGGER.warning(
            "%s failed: reason=%s executed_steps=%s target_marker_id=%s",
            phase_name.capitalize(),
            reason,
            executed_steps,
            target_marker_id,
        )

    def _grasp_object(self) -> bool:
        if self._gripper is None:
            return False
        return bool(self._gripper.grasp())

    def _release_object(self) -> None:
        if self._gripper is None:
            return
        self._gripper.release()

    def _detect_target(self) -> tuple[MarkerState | None, tuple[MarkerState, ...]]:
        return self._detect_target_marker()

    def _compute_grasp_pose(self, marker: MarkerState) -> Pose:
        return self._build_target_pose(marker)

    def _compute_offset_pose(
        self,
        base_pose: Pose,
        offset_xyz: Sequence[float],
    ) -> Pose:
        offset = self._normalize_xyz_offset(offset_xyz, "offset_xyz")
        return Pose(
            x=base_pose.x + offset[0],
            y=base_pose.y + offset[1],
            z=base_pose.z + offset[2],
            roll=base_pose.roll,
            pitch=base_pose.pitch,
            yaw=base_pose.yaw,
        )

    @staticmethod
    def _remaining_steps(
        max_control_steps: int | None,
        used_steps: int,
    ) -> int | None:
        if max_control_steps is None:
            return None
        return max(0, int(max_control_steps) - int(used_steps))

    @staticmethod
    def _success_result(
        *,
        termination_reason: str,
        markers_detected: int,
        executed_steps: int,
        target_marker_id: int | None,
        target_pose: Pose | None,
        completed_phases: tuple[str, ...],
        step_metrics: tuple[dict[str, float | int | str | None], ...],
        pick_success: bool,
        place_success: bool,
    ) -> PickAndPlaceResult:
        return PickAndPlaceResult(
            success=True,
            reason=termination_reason,
            markers_detected=markers_detected,
            executed_steps=executed_steps,
            target_marker_id=target_marker_id,
            target_pose=target_pose,
            pick_success=pick_success,
            place_success=place_success,
            termination_reason=termination_reason,
            completed_phases=completed_phases,
            step_metrics=step_metrics,
        )

    @staticmethod
    def _failure_result(
        *,
        termination_reason: str,
        markers_detected: int,
        executed_steps: int,
        target_marker_id: int | None,
        target_pose: Pose | None,
        completed_phases: tuple[str, ...],
        step_metrics: tuple[dict[str, float | int | str | None], ...],
        pick_success: bool,
        place_success: bool,
    ) -> PickAndPlaceResult:
        return PickAndPlaceResult(
            success=False,
            reason=termination_reason,
            markers_detected=markers_detected,
            executed_steps=executed_steps,
            target_marker_id=target_marker_id,
            target_pose=target_pose,
            pick_success=pick_success,
            place_success=place_success,
            termination_reason=termination_reason,
            completed_phases=completed_phases,
            step_metrics=step_metrics,
        )

    def _safe_release_and_detach(self) -> None:
        if self._gripper is not None:
            try:
                self._gripper.release()
            except Exception:
                pass
        if self._tracked_object is not None:
            try:
                self._tracked_object.detach_from_gripper()
            except Exception:
                pass

    def _safe_stop_conveyor(self) -> None:
        if self._conveyor is None:
            return
        try:
            self._conveyor.stop()
        except Exception:
            pass

    def _safe_start_conveyor(self) -> None:
        if self._conveyor is None:
            return
        try:
            self._conveyor.start()
        except Exception:
            pass

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
            from ...core.controllers.kinematic.joint_pi import JointPIController

            self._controller = JointPIController(
                kp=self._kp,
                ki=self._ki,
                joints_count=joints_count,
            )
        elif strategy == "dynamic_pd":
            from ...core.controllers.dynamic.joint_pd import JointPDController

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

    @staticmethod
    def _controller_name(controller: JointControllerLike) -> str:
        if controller.__class__.__name__ == "JointPDController":
            return "dynamic_pd"
        if controller.__class__.__name__ == "JointPIController":
            return "kinematic_pi"
        return controller.__class__.__name__.lower()

    @staticmethod
    def _controller_requires_joints_velocities(controller: JointControllerLike) -> bool:
        return controller.__class__.__name__ == "JointPDController"

    @staticmethod
    def _extract_numeric_tuple(values: object) -> tuple[float, ...] | None:
        if values is None:
            return None
        try:
            tuple_values = tuple(float(value) for value in values)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return None
        return tuple_values

    @staticmethod
    def _norm_l2(values: Sequence[float]) -> float:
        return math.sqrt(sum(float(value) ** 2 for value in values))

    @staticmethod
    def _norm_linf(values: Sequence[float]) -> float:
        if len(values) == 0:
            return 0.0
        return max(abs(float(value)) for value in values)

    @staticmethod
    def _max_abs(values: Sequence[float]) -> float:
        if len(values) == 0:
            return 0.0
        return max(abs(float(value)) for value in values)

    @staticmethod
    def _count_saturated(
        *,
        tau_tuple: Sequence[float],
        tau_min: Sequence[float],
        tau_max: Sequence[float],
    ) -> int:
        epsilon = 1e-9
        count = 0
        for tau_i, tau_min_i, tau_max_i in zip(tau_tuple, tau_min, tau_max):
            if abs(float(tau_i) - float(tau_min_i)) <= epsilon:
                count += 1
                continue
            if abs(float(tau_i) - float(tau_max_i)) <= epsilon:
                count += 1
        return count

    @staticmethod
    def _normalize_xyz_offset(
        values: Sequence[float],
        values_name: str,
    ) -> tuple[float, float, float]:
        try:
            offset = tuple(float(value) for value in values)
        except (TypeError, ValueError):
            raise ValueError(
                f"`{values_name}` must contain numeric values."
            ) from None
        if len(offset) != 3:
            raise ValueError(f"`{values_name}` must contain exactly 3 values.")
        return (offset[0], offset[1], offset[2])
