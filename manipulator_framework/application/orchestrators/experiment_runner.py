from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from numbers import Real
import platform
import random
import subprocess
import sys
from typing import Any
from uuid import uuid4

from ...core.models.marker_state import MarkerState
from ...core.models.pose import Pose
from ...core.models.robot_state import RobotState
from ...core.ports.camera_port import CameraPort
from ...core.ports.dynamics_port import DynamicsPort
from ...core.ports.kinematics_port import KinematicsPort
from ...core.ports.perception_port import PerceptionPort
from ...core.ports.robot_port import RobotPort
from ...core.ports.visualization_port import VisualizationPort
from ...core.trajectory.quintic_trajectory import QuinticJointTrajectory
from ...config.experiment_config import ExperimentConfig
from ...infrastructure.results_repository import ResultsRepository
from ..use_cases.pick_and_place import PickAndPlaceResult, PickAndPlaceUseCase

GainValue = Real | Sequence[float] | Sequence[Sequence[float]]
_EXPERIMENT_PICK_AND_PLACE_KIN_PI = "pick_and_place_kin_pi"
_EXPERIMENT_PICK_AND_PLACE_DYN_PD = "pick_and_place_dyn_pd"
_ARTIFACT_SCHEMA_VERSION = "1.0"
_CONVERGENCE_EPSILON_L2 = 0.02


@dataclass(slots=True)
class PickAndPlaceWiring:
    robot: RobotPort
    camera: CameraPort
    perception: PerceptionPort
    kinematics: KinematicsPort
    dynamics: DynamicsPort | None = None
    visualization: VisualizationPort | None = None

@dataclass(slots=True, frozen=True)
class ExperimentExecution:
    experiment: str
    run_id: str
    metrics: dict[str, Any]
    artifacts: dict[str, str]
    cycle_results: tuple[PickAndPlaceResult, ...]

class ExperimentRunner:
    """Loads config, wires dependencies, executes use-cases and persists artifacts."""

    def __init__(
        self,
        use_case: PickAndPlaceUseCase,
        config: ExperimentConfig | None = None,
        results_repository: ResultsRepository | None = None,
    ) -> None:
        self._use_case = use_case
        self._config = config
        self._results_repository = results_repository

    @classmethod
    def from_wiring(
        cls,
        wiring: PickAndPlaceWiring,
        trajectory_duration_s: float = 2.0,
        control_dt_s: float = 0.05,
        target_height_offset_m: float = 0.0,
        config: ExperimentConfig | None = None,
        results_repository: ResultsRepository | None = None,
    ) -> "ExperimentRunner":
        kwargs: dict[str, Any] = {}
        if config is not None:
            if config.experiment == _EXPERIMENT_PICK_AND_PLACE_KIN_PI:
                kwargs["controller"] = "kinematic_pi"
            elif config.experiment == _EXPERIMENT_PICK_AND_PLACE_DYN_PD:
                kwargs["controller"] = "dynamic_pd"
            kwargs["kp"] = config.pick_and_place.kp
            kwargs["ki"] = config.pick_and_place.ki
            kwargs["kv"] = config.pick_and_place.kv
            kwargs["joints_torques_min"] = config.pick_and_place.tau_min
            kwargs["joints_torques_max"] = config.pick_and_place.tau_max

        initial_state = wiring.robot.get_state()
        use_case = PickAndPlaceUseCase(
            robot=wiring.robot,
            camera=wiring.camera,
            perception=wiring.perception,
            kinematics=wiring.kinematics,
            dynamics=wiring.dynamics,
            visualization=wiring.visualization,
            trajectory_generator=QuinticJointTrajectory(),
            trajectory_duration_s=trajectory_duration_s,
            control_dt_s=control_dt_s,
            target_height_offset_m=target_height_offset_m,
            **kwargs,
        )
        return cls(
            use_case=use_case,
            config=config,
            results_repository=results_repository,
        )

    @classmethod
    def from_config(
        cls,
        config: ExperimentConfig,
        results_repository: ResultsRepository | None = None,
    ) -> "ExperimentRunner":
        if config.experiment not in (
            _EXPERIMENT_PICK_AND_PLACE_KIN_PI,
            _EXPERIMENT_PICK_AND_PLACE_DYN_PD,
        ):
            raise ValueError(f"Unsupported experiment '{config.experiment}'.")

        wiring = cls._build_pick_and_place_wiring(config)
        repository = (
            results_repository
            if results_repository is not None
            else ResultsRepository(config.persistence.output_dir)
        )

        if config.experiment == _EXPERIMENT_PICK_AND_PLACE_DYN_PD:
            if wiring.dynamics is None:
                raise ValueError(
                    "DynamicsPort wiring is required for 'pick_and_place_dyn_pd'."
                )
            controller = "dynamic_pd"
        else:
            controller = "kinematic_pi"

        initial_state = wiring.robot.get_state()

        use_case = PickAndPlaceUseCase(
            robot=wiring.robot,
            camera=wiring.camera,
            perception=wiring.perception,
            kinematics=wiring.kinematics,
            dynamics=wiring.dynamics,
            visualization=wiring.visualization,
            trajectory_generator=QuinticJointTrajectory(),
            controller=controller,
            kp=config.pick_and_place.kp,
            ki=config.pick_and_place.ki,
            kv=config.pick_and_place.kv,
            joints_torques_min=config.pick_and_place.tau_min,
            joints_torques_max=config.pick_and_place.tau_max,
            trajectory_duration_s=config.pick_and_place.trajectory_duration_s,
            control_dt_s=config.pick_and_place.control_dt_s,
            target_height_offset_m=config.pick_and_place.target_height_offset_m,
        )
        return cls(
            use_case=use_case,
            config=config,
            results_repository=repository,
        )

    def run(
        self,
        cycles: int = 1,
        max_control_steps_per_cycle: int | None = None,
        stop_on_success: bool = False,
    ) -> tuple[PickAndPlaceResult, ...]:
        if cycles <= 0:
            raise ValueError("`cycles` must be greater than zero.")

        results: list[PickAndPlaceResult] = []
        for _ in range(cycles):
            result = self._use_case.run_once(
                max_control_steps=max_control_steps_per_cycle
            )
            results.append(result)
            if stop_on_success and result.success:
                break
        return tuple(results)

    def run_experiment(self) -> ExperimentExecution:
        if self._config is None:
            raise ValueError("ExperimentRunner must be created from config to run_experiment().")

        self._set_random_seed(self._config.runtime.random_seed)
        controller_name = (
            "dynamic_pd"
            if self._config.experiment == _EXPERIMENT_PICK_AND_PLACE_DYN_PD
            else "kinematic_pi"
        )

        started_at = datetime.now(timezone.utc)
        events_rows: list[dict[str, Any]] = [
            self._make_event(
                event_type="run_started",
                severity="info",
                started_at=started_at,
                cycle_index=None,
                step_index=None,
                data={"controller": controller_name},
            )
        ]
        cycle_results: list[PickAndPlaceResult] = []
        try:
            for cycle_index in range(1, self._config.runtime.cycles + 1):
                events_rows.append(
                    self._make_event(
                        event_type="cycle_started",
                        severity="info",
                        started_at=started_at,
                        cycle_index=cycle_index,
                        step_index=None,
                        data={},
                    )
                )
                result = self._use_case.run_once(
                    max_control_steps=self._config.runtime.max_control_steps_per_cycle
                )
                cycle_results.append(result)
                events_rows.append(
                    self._make_event(
                        event_type="cycle_finished",
                        severity="info",
                        started_at=started_at,
                        cycle_index=cycle_index,
                        step_index=None,
                        data={
                            "success": result.success,
                            "reason": result.reason,
                            "executed_steps": result.executed_steps,
                            "target_marker_id": result.target_marker_id,
                        },
                    )
                )
                if self._config.runtime.stop_on_success and result.success:
                    break
        finally:
            self._shutdown_use_case(self._use_case)
        finished_at = datetime.now(timezone.utc)
        cycle_results_tuple = tuple(cycle_results)

        timeseries_rows = self._build_timeseries_rows(
            run_id="",
            cycle_results=cycle_results_tuple,
        )

        metrics = self._collect_metrics(
            started_at=started_at,
            finished_at=finished_at,
            cycles_planned=self._config.runtime.cycles,
            cycle_results=cycle_results_tuple,
            timeseries_rows=timeseries_rows,
        )

        run_id = f"{started_at.strftime('%Y%m%dT%H%M%S')}_{uuid4().hex[:8]}"
        timeseries_rows = self._build_timeseries_rows(
            run_id=run_id,
            cycle_results=cycle_results_tuple,
        )
        convergence_events = self._build_convergence_events(
            started_at=started_at,
            cycle_results=cycle_results_tuple,
        )
        events_rows.extend(convergence_events)
        events_rows.append(
            self._make_event(
                event_type="run_finished",
                severity="info",
                started_at=started_at,
                cycle_index=None,
                step_index=None,
                data={"success_rate": metrics["success_rate"]},
            )
        )
        summary = self._build_summary(
            run_id=run_id,
            controller=controller_name,
            metrics=metrics,
        )
        config_snapshot = self._build_config_snapshot(
            run_id=run_id,
            config=self._config,
        )
        events_payload = {
            "schema_version": _ARTIFACT_SCHEMA_VERSION,
            "run_id": run_id,
            "events": events_rows,
        }
        artifacts: dict[str, str] = {}
        if self._results_repository is not None:
            artifacts = self._results_repository.save_experiment_results(
                experiment=self._config.experiment,
                config=asdict(self._config),
                metrics=metrics,
                cycles_rows=self._cycle_results_to_rows(cycle_results_tuple),
                summary=summary,
                config_snapshot=config_snapshot,
                timeseries_rows=timeseries_rows,
                events=events_payload,
                run_id=run_id,
                save_json=self._config.persistence.save_json,
                save_csv=self._config.persistence.save_csv,
            )

        return ExperimentExecution(
            experiment=self._config.experiment,
            run_id=run_id,
            metrics=metrics,
            artifacts=artifacts,
            cycle_results=cycle_results_tuple,
        )

    @staticmethod
    def _set_random_seed(seed: int) -> None:
        random.seed(seed)
        try:
            import numpy as np

            np.random.seed(seed)
        except Exception:
            pass

    def _collect_metrics(
        self,
        *,
        started_at: datetime,
        finished_at: datetime,
        cycles_planned: int,
        cycle_results: tuple[PickAndPlaceResult, ...],
        timeseries_rows: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        cycles_executed = len(cycle_results)
        success_count = sum(1 for result in cycle_results if result.success)
        failure_count = cycles_executed - success_count
        total_steps = sum(result.executed_steps for result in cycle_results)
        mean_steps = (total_steps / cycles_executed) if cycles_executed > 0 else 0.0
        duration_s = (finished_at - started_at).total_seconds()
        reason_counts = dict(Counter(result.reason for result in cycle_results))

        q_error_l2_values = [
            float(row["q_error_l2"])
            for row in timeseries_rows
            if row.get("q_error_l2") is not None
        ]
        q_error_linf_values = [
            float(row["q_error_linf"])
            for row in timeseries_rows
            if row.get("q_error_linf") is not None
        ]
        dq_cmd_l2_values = [
            float(row["dq_cmd_l2"])
            for row in timeseries_rows
            if row.get("dq_cmd_l2") is not None
        ]
        tau_cmd_l2_values = [
            float(row["tau_cmd_l2"])
            for row in timeseries_rows
            if row.get("tau_cmd_l2") is not None
        ]
        tau_sat_counts = [
            int(row["tau_saturated_count"])
            for row in timeseries_rows
            if row.get("tau_saturated_count") is not None
        ]
        cycles_with_torque_saturation = sum(
            1
            for result in cycle_results
            if any(
                int(step_row.get("tau_saturated_count", 0) or 0) > 0
                for step_row in result.step_metrics
            )
        )

        converged_steps = [
            first_step
            for first_step in (
                self._first_converged_step(result.step_metrics)
                for result in cycle_results
            )
            if first_step is not None
        ]
        error_decay_ratios = [
            ratio
            for ratio in (
                self._error_decay_ratio(result.step_metrics)
                for result in cycle_results
            )
            if ratio is not None
        ]
        q_error_l2_values_sorted = sorted(q_error_l2_values)
        p95_error = (
            q_error_l2_values_sorted[
                min(
                    len(q_error_l2_values_sorted) - 1,
                    int(0.95 * (len(q_error_l2_values_sorted) - 1)),
                )
            ]
            if len(q_error_l2_values_sorted) > 0
            else None
        )

        return {
            "schema_version": _ARTIFACT_SCHEMA_VERSION,
            "started_at_utc": started_at.isoformat(),
            "finished_at_utc": finished_at.isoformat(),
            "duration_s": duration_s,
            "cycles_planned": cycles_planned,
            "cycles_executed": cycles_executed,
            "success_count": success_count,
            "failure_count": failure_count,
            "success_rate": (success_count / cycles_executed) if cycles_executed > 0 else 0.0,
            "total_executed_steps": total_steps,
            "mean_executed_steps": mean_steps,
            "aggregate": {
                "total_control_steps": total_steps,
                "mean_control_steps_per_cycle": mean_steps,
            },
            "comparison": {
                "tracking_error_l2_mean": (
                    sum(q_error_l2_values) / len(q_error_l2_values)
                    if len(q_error_l2_values) > 0
                    else None
                ),
                "tracking_error_l2_p95": p95_error,
                "command_velocity_l2_mean": (
                    sum(dq_cmd_l2_values) / len(dq_cmd_l2_values)
                    if len(dq_cmd_l2_values) > 0
                    else None
                ),
                "command_torque_l2_mean": (
                    sum(tau_cmd_l2_values) / len(tau_cmd_l2_values)
                    if len(tau_cmd_l2_values) > 0
                    else None
                ),
            },
            "convergence": {
                "epsilon_l2": _CONVERGENCE_EPSILON_L2,
                "converged_cycles": len(converged_steps),
                "converged_rate": (
                    len(converged_steps) / cycles_executed if cycles_executed > 0 else 0.0
                ),
                "median_first_converged_step": self._median_int(converged_steps),
                "error_decay_ratio_mean": (
                    sum(error_decay_ratios) / len(error_decay_ratios)
                    if len(error_decay_ratios) > 0
                    else None
                ),
            },
            "safety_deviation": {
                "max_tracking_error_linf": max(q_error_linf_values) if len(q_error_linf_values) > 0 else None,
                "cycles_with_marker_loss": reason_counts.get("no_marker_detected_with_world_pose", 0),
                "cycles_with_ik_failure": reason_counts.get("inverse_kinematics_failed", 0),
                "cycles_with_torque_saturation": cycles_with_torque_saturation,
                "torque_saturation_step_ratio": (
                    sum(1 for count in tau_sat_counts if count > 0) / len(tau_sat_counts)
                    if len(tau_sat_counts) > 0
                    else 0.0
                ),
            },
            "reason_counts": reason_counts,
        }

    @staticmethod
    def _build_timeseries_rows(
        *,
        run_id: str,
        cycle_results: tuple[PickAndPlaceResult, ...],
    ) -> tuple[dict[str, Any], ...]:
        rows: list[dict[str, Any]] = []
        for cycle_index, result in enumerate(cycle_results, start=1):
            for step_row in result.step_metrics:
                row = dict(step_row)
                row["run_id"] = run_id
                row["cycle_index"] = cycle_index
                rows.append(row)
        return tuple(rows)

    def _build_convergence_events(
        self,
        *,
        started_at: datetime,
        cycle_results: tuple[PickAndPlaceResult, ...],
    ) -> tuple[dict[str, Any], ...]:
        events: list[dict[str, Any]] = []
        for cycle_index, result in enumerate(cycle_results, start=1):
            first_step = self._first_converged_step(result.step_metrics)
            if first_step is None:
                continue
            step_row = result.step_metrics[first_step - 1]
            events.append(
                self._make_event(
                    event_type="convergence_reached",
                    severity="info",
                    started_at=started_at,
                    cycle_index=cycle_index,
                    step_index=first_step,
                    data={"q_error_l2": step_row.get("q_error_l2")},
                )
            )
        return tuple(events)

    def _build_summary(
        self,
        *,
        run_id: str,
        controller: str,
        metrics: Mapping[str, Any],
    ) -> dict[str, Any]:
        return {
            "schema_version": _ARTIFACT_SCHEMA_VERSION,
            "run_id": run_id,
            "experiment": self._config.experiment if self._config is not None else None,
            "controller": controller,
            "backend": self._config.runtime.backend if self._config is not None else None,
            "started_at_utc": metrics.get("started_at_utc"),
            "finished_at_utc": metrics.get("finished_at_utc"),
            "duration_s": metrics.get("duration_s"),
            "cycles_planned": metrics.get("cycles_planned"),
            "cycles_executed": metrics.get("cycles_executed"),
            "success_count": metrics.get("success_count"),
            "failure_count": metrics.get("failure_count"),
            "success_rate": metrics.get("success_rate"),
            "primary_reason_counts": metrics.get("reason_counts", {}),
        }

    @staticmethod
    def _build_config_snapshot(
        *,
        run_id: str,
        config: ExperimentConfig,
    ) -> dict[str, Any]:
        return {
            "schema_version": _ARTIFACT_SCHEMA_VERSION,
            "run_id": run_id,
            "experiment_config": asdict(config),
            "reproducibility": {
                "random_seed": config.runtime.random_seed,
                "python_version": sys.version,
                "platform": platform.platform(),
                "git_commit": ExperimentRunner._git_commit(),
                "git_dirty": ExperimentRunner._git_dirty(),
            },
            "units": {
                "time": "s",
                "position": "m",
                "angle": "rad",
                "joint_velocity": "rad/s",
                "joint_torque": "N.m",
            },
        }

    @staticmethod
    def _first_converged_step(
        step_metrics: Sequence[Mapping[str, Any]],
    ) -> int | None:
        for step_row in step_metrics:
            value = step_row.get("q_error_l2")
            if value is None:
                continue
            if float(value) <= _CONVERGENCE_EPSILON_L2:
                step_index = step_row.get("step_index")
                if step_index is None:
                    continue
                return int(step_index)
        return None

    @staticmethod
    def _error_decay_ratio(
        step_metrics: Sequence[Mapping[str, Any]],
    ) -> float | None:
        q_error_l2 = [
            float(step_row["q_error_l2"])
            for step_row in step_metrics
            if step_row.get("q_error_l2") is not None
        ]
        if len(q_error_l2) < 2:
            return None
        initial = q_error_l2[0]
        if abs(initial) < 1e-12:
            return 0.0
        return q_error_l2[-1] / initial

    @staticmethod
    def _median_int(values: Sequence[int]) -> int | None:
        if len(values) == 0:
            return None
        sorted_values = sorted(int(value) for value in values)
        middle = len(sorted_values) // 2
        if len(sorted_values) % 2 == 1:
            return sorted_values[middle]
        return int(round((sorted_values[middle - 1] + sorted_values[middle]) / 2.0))

    @staticmethod
    def _make_event(
        *,
        event_type: str,
        severity: str,
        started_at: datetime,
        cycle_index: int | None,
        step_index: int | None,
        data: Mapping[str, Any],
    ) -> dict[str, Any]:
        return {
            "ts_utc": datetime.now(timezone.utc).isoformat(),
            "elapsed_s": max(
                0.0,
                (datetime.now(timezone.utc) - started_at).total_seconds(),
            ),
            "cycle_index": cycle_index,
            "step_index": step_index,
            "type": event_type,
            "severity": severity,
            "data": dict(data),
        }

    @staticmethod
    def _git_commit() -> str | None:
        try:
            completed = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            )
            commit = completed.stdout.strip()
            return commit or None
        except Exception:
            return None

    @staticmethod
    def _git_dirty() -> bool:
        try:
            completed = subprocess.run(
                ["git", "status", "--porcelain"],
                check=True,
                capture_output=True,
                text=True,
            )
            return len(completed.stdout.strip()) > 0
        except Exception:
            return False

    @staticmethod
    def _cycle_results_to_rows(
        cycle_results: tuple[PickAndPlaceResult, ...],
    ) -> tuple[dict[str, Any], ...]:
        rows: list[dict[str, Any]] = []
        for cycle_index, result in enumerate(cycle_results, start=1):
            target_pose = result.target_pose
            rows.append(
                {
                    "cycle_index": cycle_index,
                    "success": result.success,
                    "reason": result.reason,
                    "markers_detected": result.markers_detected,
                    "executed_steps": result.executed_steps,
                    "target_marker_id": result.target_marker_id,
                    "target_x": None if target_pose is None else target_pose.x,
                    "target_y": None if target_pose is None else target_pose.y,
                    "target_z": None if target_pose is None else target_pose.z,
                    "target_roll": None if target_pose is None else target_pose.roll,
                    "target_pitch": None if target_pose is None else target_pose.pitch,
                    "target_yaw": None if target_pose is None else target_pose.yaw,
                }
            )
        return tuple(rows)

    @staticmethod
    def _shutdown_use_case(use_case: object) -> None:
        shutdown_method = getattr(use_case, "shutdown", None)
        if callable(shutdown_method):
            shutdown_method()

    @classmethod
    def _build_pick_and_place_wiring(
        cls,
        config: ExperimentConfig,
    ) -> PickAndPlaceWiring:
        backend = config.runtime.backend.lower()
        if backend == "mock":
            return cls._build_mock_wiring()
        if backend == "coppelia":
            return cls._build_coppelia_wiring(config)
        raise ValueError(
            f"Unsupported backend '{config.runtime.backend}'. Supported: ['mock', 'coppelia']."
        )

    @classmethod
    def _build_mock_wiring(cls) -> PickAndPlaceWiring:
        robot = _MockRobotAdapter()
        camera = _MockCameraAdapter()
        perception = _MockPerceptionAdapter()
        kinematics = _MockKinematicsAdapter()
        dynamics = _MockDynamicsAdapter(joints_count=7)
        visualization: VisualizationPort | None = None
        return PickAndPlaceWiring(
            robot=robot,
            camera=camera,
            perception=perception,
            kinematics=kinematics,
            dynamics=dynamics,
            visualization=visualization,
        )

    @classmethod
    def _build_coppelia_wiring(cls, config: ExperimentConfig) -> PickAndPlaceWiring:
        from ...adapters.perception.aruco_detector_adapter import ArucoDetectorAdapter
        from ...adapters.perception.coppelia_camera_adapter import CoppeliaCameraAdapter
        from ...adapters.robotics.rtb_dynamics_adapter import RTBDynamicsAdapter
        from ...adapters.robotics.rtb_kinematics_adapter import RTBKinematicsAdapter
        from ...adapters.robotics.rtb_lbr_iiwa import LBRIiwaRTB
        from ...adapters.simulation.coppelia_adapter import CoppeliaAdapter
        from ...adapters.visualization.pyplot_adapter import PyPlotAdapter

        robot = CoppeliaAdapter(
            host=config.coppelia.host,
            port=config.coppelia.port,
            scene_path=config.coppelia.scene_path,
            robot_path=config.coppelia.robot_path,
            joints_count=config.coppelia.joints_count,
            joints_prefix=config.coppelia.joints_prefix,
            tip_path=config.coppelia.tip_path,
            auto_start=True,
        )
        camera = CoppeliaCameraAdapter(
            sim=robot.sim,
            sensor_path=config.coppelia.camera_sensor_path,
            distortion_coefficients=config.coppelia.camera_distortion_coefficients,
            frame_rotation=config.coppelia.camera_frame_rotation,
        )
        perception = ArucoDetectorAdapter(
            camera=camera,
            marker_length_m=config.pick_and_place.marker_length_m,
            dictionary_name=config.pick_and_place.aruco_dictionary,
        )
        rtb_robot_model = LBRIiwaRTB()
        kinematics = RTBKinematicsAdapter(robot=rtb_robot_model)
        dynamics = RTBDynamicsAdapter(robot=rtb_robot_model)
        visualization: VisualizationPort | None = None
        if config.runtime.enable_visualization:
            visualization = PyPlotAdapter()

        # Matches legacy startup behavior: one simulation step before first vision read.
        robot.step()

        return PickAndPlaceWiring(
            robot=robot,
            camera=camera,
            perception=perception,
            kinematics=kinematics,
            dynamics=dynamics,
            visualization=visualization,
        )


class _MockRobotAdapter(RobotPort):
    def __init__(self, joints_count: int = 7) -> None:
        self._q = tuple(0.0 for _ in range(joints_count))
        self._q_dot = tuple(0.0 for _ in range(joints_count))

    def get_state(self) -> RobotState:
        return RobotState(joints_positions=self._q, joints_velocities=self._q_dot)

    def get_joints_positions(self) -> tuple[float, ...]:
        return self._q

    def command_joints_positions(self, joints_positions: tuple[float, ...]) -> None:
        self._q = tuple(float(value) for value in joints_positions)

    def command_joints_velocities(self, joints_velocities: tuple[float, ...]) -> None:
        q_dot = tuple(float(value) for value in joints_velocities)
        self._q_dot = q_dot
        self._q = tuple(
            q_i + 0.05 * q_dot_i for q_i, q_dot_i in zip(self._q, q_dot)
        )

    def step(self, reference_xyz: tuple[float, float, float] | None = None) -> None:
        del reference_xyz
        return None


class _MockCameraAdapter(CameraPort):
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


class _MockPerceptionAdapter(PerceptionPort):
    def detect_markers(self, frame: object) -> tuple[MarkerState, ...]:
        del frame
        return (
            MarkerState(marker_id=1, pose_world=Pose(x=0.60, y=0.0, z=0.25)),
        )

    def detect_people(self, frame: object):
        del frame
        return ()


class _MockDynamicsAdapter(DynamicsPort):
    def __init__(self, joints_count: int) -> None:
        self._joints_count = joints_count

    def inertia(self, joints_positions: Sequence[float]) -> tuple[tuple[float, ...], ...]:
        del joints_positions
        return tuple(
            tuple(1.0 if row == column else 0.0 for column in range(self._joints_count))
            for row in range(self._joints_count)
        )

    def coriolis(
        self,
        joints_positions: Sequence[float],
        joints_velocities: Sequence[float],
    ) -> tuple[tuple[float, ...], ...]:
        del joints_positions, joints_velocities
        return tuple(
            tuple(0.0 for _ in range(self._joints_count))
            for _ in range(self._joints_count)
        )

    def gravity(self, joints_positions: Sequence[float]) -> tuple[float, ...]:
        del joints_positions
        return tuple(0.0 for _ in range(self._joints_count))


class _MockKinematicsAdapter(KinematicsPort):
    def forward_kinematics(self, joints_positions):
        joints = tuple(float(value) for value in joints_positions)
        return Pose(
            x=sum(joints[:3]),
            y=0.0 if len(joints) < 2 else joints[1],
            z=0.0 if len(joints) < 3 else joints[2],
        )

    def inverse_kinematics(self, target_pose, seed_joints_positions=None):
        if seed_joints_positions is not None:
            joints = list(float(value) for value in seed_joints_positions)
        else:
            joints = [0.0 for _ in range(7)]
        if len(joints) >= 1:
            joints[0] = target_pose.x
        if len(joints) >= 2:
            joints[1] = target_pose.y
        if len(joints) >= 3:
            joints[2] = target_pose.z
        return tuple(joints)

    def jacobian(self, joints_positions):
        del joints_positions
        return tuple(tuple(0.0 for _ in range(7)) for _ in range(6))

    def plan_joint_trajectory(self, start_joints_positions, goal_joints_positions, time_samples_s):
        del start_joints_positions, goal_joints_positions, time_samples_s
        return ()

    def plan_cartesian_trajectory(self, start_pose, goal_pose, time_samples_s):
        del start_pose, goal_pose, time_samples_s
        return ()
