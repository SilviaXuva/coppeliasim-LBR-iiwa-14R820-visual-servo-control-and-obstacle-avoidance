from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from numbers import Real
import random
from typing import Any
from uuid import uuid4

from ...core.controllers.kinematic.joint_pi import JointPIController
from ...core.models.marker_state import MarkerState
from ...core.models.pose import Pose
from ...core.models.robot_state import RobotState
from ...core.ports.camera_port import CameraPort
from ...core.ports.kinematics_port import KinematicsPort
from ...core.ports.perception_port import PerceptionPort
from ...core.ports.robot_port import RobotPort
from ...core.ports.visualization_port import VisualizationPort
from ...core.trajectory.quintic_trajectory import QuinticJointTrajectory
from ...config.experiment_config import ExperimentConfig
from ...infrastructure.results_repository import ResultsRepository
from ..use_cases.pick_and_place import PickAndPlaceResult, PickAndPlaceUseCase

GainValue = Real | Sequence[float] | Sequence[Sequence[float]]


@dataclass(slots=True)
class PickAndPlaceWiring:
    robot: RobotPort
    camera: CameraPort
    perception: PerceptionPort
    kinematics: KinematicsPort
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
        kp: GainValue = 1.0,
        ki: GainValue = 0.0,
        trajectory_duration_s: float = 2.0,
        control_dt_s: float = 0.05,
        target_height_offset_m: float = 0.0,
        config: ExperimentConfig | None = None,
        results_repository: ResultsRepository | None = None,
    ) -> "ExperimentRunner":
        initial_state = wiring.robot.get_state()
        controller = JointPIController(
            kp=kp,
            ki=ki,
            joints_count=len(initial_state.joints_positions),
        )
        use_case = PickAndPlaceUseCase(
            robot=wiring.robot,
            camera=wiring.camera,
            perception=wiring.perception,
            kinematics=wiring.kinematics,
            visualization=wiring.visualization,
            trajectory_generator=QuinticJointTrajectory(),
            controller=controller,
            trajectory_duration_s=trajectory_duration_s,
            control_dt_s=control_dt_s,
            target_height_offset_m=target_height_offset_m,
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
        if config.experiment != "pick_and_place":
            raise ValueError(
                f"Unsupported experiment '{config.experiment}'."
            )

        wiring = cls._build_pick_and_place_wiring(config)
        repository = (
            results_repository
            if results_repository is not None
            else ResultsRepository(config.persistence.output_dir)
        )
        return cls.from_wiring(
            wiring=wiring,
            kp=config.pick_and_place.kp,
            ki=config.pick_and_place.ki,
            trajectory_duration_s=config.pick_and_place.trajectory_duration_s,
            control_dt_s=config.pick_and_place.control_dt_s,
            target_height_offset_m=config.pick_and_place.target_height_offset_m,
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

        started_at = datetime.now(timezone.utc)
        try:
            cycle_results = self.run(
                cycles=self._config.runtime.cycles,
                max_control_steps_per_cycle=self._config.runtime.max_control_steps_per_cycle,
                stop_on_success=self._config.runtime.stop_on_success,
            )
        finally:
            self._shutdown_use_case(self._use_case)
        finished_at = datetime.now(timezone.utc)

        metrics = self._collect_metrics(
            started_at=started_at,
            finished_at=finished_at,
            cycle_results=cycle_results,
        )

        run_id = f"{started_at.strftime('%Y%m%dT%H%M%S')}_{uuid4().hex[:8]}"
        artifacts: dict[str, str] = {}
        if self._results_repository is not None:
            artifacts = self._results_repository.save_experiment_results(
                experiment=self._config.experiment,
                config=asdict(self._config),
                metrics=metrics,
                cycles_rows=self._cycle_results_to_rows(cycle_results),
                run_id=run_id,
                save_json=self._config.persistence.save_json,
                save_csv=self._config.persistence.save_csv,
            )

        return ExperimentExecution(
            experiment=self._config.experiment,
            run_id=run_id,
            metrics=metrics,
            artifacts=artifacts,
            cycle_results=cycle_results,
        )

    @staticmethod
    def _set_random_seed(seed: int) -> None:
        random.seed(seed)
        try:
            import numpy as np

            np.random.seed(seed)
        except Exception:
            pass

    @staticmethod
    def _collect_metrics(
        *,
        started_at: datetime,
        finished_at: datetime,
        cycle_results: tuple[PickAndPlaceResult, ...],
    ) -> dict[str, Any]:
        cycles_executed = len(cycle_results)
        success_count = sum(1 for result in cycle_results if result.success)
        failure_count = cycles_executed - success_count
        total_steps = sum(result.executed_steps for result in cycle_results)
        mean_steps = (total_steps / cycles_executed) if cycles_executed > 0 else 0.0
        duration_s = (finished_at - started_at).total_seconds()

        return {
            "started_at_utc": started_at.isoformat(),
            "finished_at_utc": finished_at.isoformat(),
            "duration_s": duration_s,
            "cycles_executed": cycles_executed,
            "success_count": success_count,
            "failure_count": failure_count,
            "success_rate": (success_count / cycles_executed) if cycles_executed > 0 else 0.0,
            "total_executed_steps": total_steps,
            "mean_executed_steps": mean_steps,
        }

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
        visualization: VisualizationPort | None = None
        return PickAndPlaceWiring(
            robot=robot,
            camera=camera,
            perception=perception,
            kinematics=kinematics,
            visualization=visualization,
        )

    @classmethod
    def _build_coppelia_wiring(cls, config: ExperimentConfig) -> PickAndPlaceWiring:
        from ...adapters.perception.aruco_detector_adapter import ArucoDetectorAdapter
        from ...adapters.perception.coppelia_camera_adapter import CoppeliaCameraAdapter
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
        kinematics = RTBKinematicsAdapter(robot=LBRIiwaRTB())
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
            visualization=visualization,
        )


class _MockRobotAdapter(RobotPort):
    def __init__(self, joints_count: int = 7) -> None:
        self._q = tuple(0.0 for _ in range(joints_count))

    def get_state(self) -> RobotState:
        return RobotState(joints_positions=self._q)

    def get_joints_positions(self) -> tuple[float, ...]:
        return self._q

    def command_joints_positions(self, joints_positions: tuple[float, ...]) -> None:
        self._q = tuple(float(value) for value in joints_positions)

    def command_joints_velocities(self, joints_velocities: tuple[float, ...]) -> None:
        q_dot = tuple(float(value) for value in joints_velocities)
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
