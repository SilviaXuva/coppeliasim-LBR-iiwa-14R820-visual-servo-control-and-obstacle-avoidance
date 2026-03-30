from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import time

import numpy as np

from manipulator_framework.application.composition.application_composer import ApplicationComposer
from manipulator_framework.application.services.experiment_service import ExperimentService
from manipulator_framework.application.services.runtime_execution_service import RuntimeExecutionService
from manipulator_framework.application.use_cases.run_joint_trajectory import RunJointTrajectory
from manipulator_framework.application.use_cases.run_pbvs_with_avoidance import RunPBVSWithAvoidance
from manipulator_framework.adapters.simulation.coppeliasim.client import CoppeliaSimClient
from manipulator_framework.adapters.simulation.coppeliasim.robot_adapter import CoppeliaSimRobotAdapter
from manipulator_framework.adapters.simulation.coppeliasim.camera_adapter import CoppeliaSimCameraAdapter
from manipulator_framework.adapters.simulation.coppeliasim.obstacle_source import CoppeliaSimObstacleSource
from manipulator_framework.adapters.simulation.coppeliasim.simulator_adapter import (
    CoppeliaSimSimulatorAdapter,
)
from manipulator_framework.adapters.simulation.pyplot import (
    DefaultPyPlotBackend,
    PyPlotCameraAdapter,
    PyPlotObstacleSource,
    PyPlotRobotAdapter,
    PyPlotSimulatorAdapter,
)
from manipulator_framework.adapters.vision.aruco.aruco_opencv_adapter import ArucoOpenCVAdapter
from manipulator_framework.adapters.vision.aruco.opencv_pose_estimator_adapter import OpenCVPoseEstimatorAdapter
from manipulator_framework.adapters.vision.yolo.yolo_ultralytics_adapter import (
    YoloUltralyticsPersonDetectorAdapter,
)
from manipulator_framework.adapters.vision.stub_detectors import StubPersonDetector
from manipulator_framework.core.contracts import (
    CameraInterface,
    ClockInterface,
    ControllerInterface,
    ExecutionEngineInterface,
    MarkerDetectorInterface,
    ObstacleAvoidanceInterface,
    ObstacleSourceInterface,
    PersonDetectorInterface,
    PoseEstimatorInterface,
    ResultsRepositoryInterface,
    RobotInterface,
    SimulatorInterface,
    TrackerInterface,
    VisualServoInterface,
)
from manipulator_framework.core.control.joint_pd_controller import JointSpacePDController
from manipulator_framework.core.runtime import (
    ActuationStep,
    AvoidanceStep,
    ControlStep,
    EstimationStep,
    ExecutionEngine,
    MetricsStep,
    PerceptionStep,
    RuntimePipeline,
    SensingStep,
    SimulatorStep,
    VisualServoStep,
)
from manipulator_framework.core.tracking import NearestNeighborTracker, NullTracker
from manipulator_framework.core.types import Pose3D
from manipulator_framework.core.visual_servoing.pbvs_controller import PBVSController
from manipulator_framework.core.visual_servoing.reference_generation import PBVSReferenceGenerator
from manipulator_framework.core.obstacle_avoidance.cuckoo_search_avoidance import CuckooSearchAvoidance
from manipulator_framework.infrastructure.config.loader import YAMLConfigurationLoader
from manipulator_framework.infrastructure.persistence.filesystem_results_repository import (
    FileSystemResultsRepository,
)


@dataclass
class _FixedStepClock(ClockInterface):
    """
    Deterministic simulation clock using configured runtime.dt.
    """

    fixed_dt: float
    _now: float = 0.0

    def now(self) -> float:
        current = self._now
        self._now += self.fixed_dt
        return current

    def dt(self) -> float:
        return self.fixed_dt

    def sleep_until(self, timestamp: float) -> None:
        self._now = float(timestamp)

    def tick(self) -> float:
        self._now += self.fixed_dt
        return self._now

@dataclass
class SimulationComposer(ApplicationComposer):
    """
    Simulation-specialized composition root.
    Populates thick use cases with CoppeliaSim adapters and scientific components.
    """
    config: dict[str, Any]
    sim_client: Any | None = None
    yolo_model: Any | None = None
    pyplot_backend: Any | None = None
    _clock: _FixedStepClock | None = field(default=None, init=False, repr=False)
    _resolved_config: dict[str, Any] | None = field(default=None, init=False, repr=False)

    @classmethod
    def from_yaml(
        cls,
        config_path: str = "configs/app/pbvs_official.yaml",
        *,
        sim_client: Any | None = None,
        pyplot_backend: Any | None = None,
    ) -> "SimulationComposer":
        loader = YAMLConfigurationLoader()
        config = loader.load_and_resolve(config_path)
        simulation_cfg = config.get("simulation", {})
        backend = str(simulation_cfg.get("backend", "coppeliasim")).lower()
        if backend == "coppeliasim" and sim_client is None:
            sim_client = CoppeliaSimClient.connect(config.get("simulation", {}))
        return cls(
            config=config,
            sim_client=sim_client,
            pyplot_backend=pyplot_backend,
        )

    def build_robot(self) -> RobotInterface:
        simulation_cfg = self._config().get("simulation", {})
        joint_names = tuple(
            simulation_cfg.get(
                "joint_names",
                tuple(f"LBR_iiwa_14_R820_joint{i}" for i in range(1, 8)),
            )
        )
        backend = self._simulation_backend_name()
        if backend == "pyplot":
            return PyPlotRobotAdapter(
                backend=self._require_pyplot_backend(),
                joint_names=joint_names,
            )
        if backend == "coppeliasim":
            return CoppeliaSimRobotAdapter(
                sim_client=self._require_sim_client(),
                robot_handle=simulation_cfg.get("robot_handle", "LBR_iiwa_14_R820"),
                joint_names=joint_names,
            )
        raise ValueError(f"Unsupported simulation.backend='{backend}'.")

    def build_camera(self) -> CameraInterface:
        simulation_cfg = self._config().get("simulation", {})
        backend = self._simulation_backend_name()
        if backend == "pyplot":
            return PyPlotCameraAdapter(
                backend=self._require_pyplot_backend(),
                camera_id=str(simulation_cfg.get("camera_id", "pyplot_camera")),
                frame_id=str(simulation_cfg.get("camera_frame_id", "camera")),
            )
        if backend == "coppeliasim":
            return CoppeliaSimCameraAdapter(
                sim_client=self._require_sim_client(),
                camera_handle=simulation_cfg.get("camera_handle", "vision_sensor"),
                camera_id=str(simulation_cfg.get("camera_id", "sim_camera")),
                frame_id=str(simulation_cfg.get("camera_frame_id", "camera")),
            )
        raise ValueError(f"Unsupported simulation.backend='{backend}'.")

    def build_marker_detector(self) -> MarkerDetectorInterface:
        marker_cfg = self._config().get("perception", {}).get("marker_detector", {})
        dictionary = marker_cfg.get(
            "dictionary",
            self._config().get("vision", {}).get("aruco_dictionary", "DICT_4X4_50"),
        )
        return ArucoOpenCVAdapter(dictionary_name=str(dictionary))

    def build_pose_estimator(self, camera: CameraInterface | None = None) -> PoseEstimatorInterface:
        marker_cfg = self._config().get("perception", {}).get("marker_detector", {})
        marker_length = float(
            marker_cfg.get(
                "marker_length_m",
                self._config().get("vision", {}).get("marker_size", 0.1),
            )
        )
        camera_matrix = np.eye(3)
        if camera is not None:
            try:
                camera_matrix = np.asarray(camera.get_intrinsics(), dtype=float)
            except Exception:
                camera_matrix = np.eye(3)
        return OpenCVPoseEstimatorAdapter(
            camera_matrix=camera_matrix,
            distortion_coeffs=np.zeros(5),
            marker_length_m=marker_length,
        )

    def build_tracker(self) -> TrackerInterface:
        tracking_cfg = self._config().get("tracking", {})
        mode = str(tracking_cfg.get("mode", "nearest_neighbor")).lower()
        if mode in {"none", "null", "disabled"}:
            return NullTracker()
        if mode in {"nearest_neighbor", "nearest-neighbor", "nn"}:
            return NearestNeighborTracker()
        raise ValueError(f"Unsupported tracking.mode='{mode}'.")

    def build_obstacle_source(self) -> ObstacleSourceInterface:
        simulation_cfg = self._config().get("simulation", {})
        backend = self._simulation_backend_name()
        if backend == "pyplot":
            return PyPlotObstacleSource(backend=self._require_pyplot_backend())
        if backend == "coppeliasim":
            return CoppeliaSimObstacleSource(
                sim_client=self._require_sim_client(),
                obstacle_handles=tuple(simulation_cfg.get("obstacle_handles", ())),
            )
        raise ValueError(f"Unsupported simulation.backend='{backend}'.")

    def build_simulator(self) -> SimulatorInterface:
        backend = self._simulation_backend_name()
        if backend == "pyplot":
            return PyPlotSimulatorAdapter(backend=self._require_pyplot_backend())
        if backend == "coppeliasim":
            return CoppeliaSimSimulatorAdapter(sim_client=self._require_sim_client())
        raise ValueError(f"Unsupported simulation.backend='{backend}'.")

    def build_pbvs_controller(self) -> VisualServoInterface:
        gain = float(self._config().get("visual_servoing", {}).get("gain", 0.1))
        return PBVSController(
            reference_generator=PBVSReferenceGenerator(gain=gain)
        )

    def build_obstacle_avoidance(self) -> ObstacleAvoidanceInterface:
        safe_distance = float(
            self._config().get("obstacle_avoidance", {}).get(
                "clearance_m",
                self._config().get("planning", {}).get("safe_distance", 0.5),
            )
        )
        return CuckooSearchAvoidance(safe_distance=safe_distance)

    def build_trajectory_follower(self) -> ControllerInterface:
        return JointSpacePDController(dof=7)

    def build_person_detector(self) -> PersonDetectorInterface:
        yolo_cfg = self._resolve_person_detector_config()
        backend = str(yolo_cfg.get("backend", "yolo")).lower()
        if backend in {"stub", "none", "disabled"}:
            return StubPersonDetector()
        confidence_threshold = float(yolo_cfg.get("confidence_threshold", 0.5))
        model = self.yolo_model or self._load_yolo_model(yolo_cfg)
        return YoloUltralyticsPersonDetectorAdapter(
            model=model,
            confidence_threshold=confidence_threshold,
        )

    def build_clock(self) -> ClockInterface:
        if self._clock is None:
            runtime_cfg = self._config().get("runtime", {})
            dt = float(runtime_cfg.get("dt", 0.01))
            self._clock = _FixedStepClock(fixed_dt=dt, _now=time.time())
        return self._clock

    def build_execution_engine(self, pipeline: RuntimePipeline | None = None) -> ExecutionEngineInterface:
        runtime_cfg = self._config().get("runtime", {})
        sampling_period_s = float(runtime_cfg.get("dt", 0.01))
        return ExecutionEngine(
            clock=self.build_clock(),
            pipeline=pipeline or RuntimePipeline(steps=[]),
            sampling_period_s=sampling_period_s,
        )

    def build_runtime_execution_service(self) -> RuntimeExecutionService:
        return RuntimeExecutionService(clock=self.build_clock())

    def build_results_repository(self) -> ResultsRepositoryInterface:
        base_dir = str(self._config().get("results", {}).get("base_dir", "experiments/runs"))
        return FileSystemResultsRepository(base_dir=base_dir)

    def build_experiment_service(self) -> ExperimentService:
        return ExperimentService(results_repository=self.build_results_repository())

    def build_run_pbvs_with_avoidance(self) -> RunPBVSWithAvoidance:
        """
        Assemble the official base experiment with all scientific dependencies resolved.
        """
        resolved = self._config()
        self.config = resolved

        robot = self.build_robot()
        camera = self.build_camera()
        simulator = self.build_simulator()
        marker_detector = self.build_marker_detector()
        pose_estimator = self.build_pose_estimator(camera=camera)
        person_detector = self.build_person_detector()
        tracker = self.build_tracker()
        pbvs_controller = self.build_pbvs_controller()
        avoidance_module = self.build_obstacle_avoidance()
        obstacle_source = self.build_obstacle_source()
        trajectory_follower = self.build_trajectory_follower()

        planning_cfg = resolved.get("planning", {})
        obstacle_cfg = resolved.get("obstacle_avoidance", {})
        runtime_cfg = resolved.get("runtime", {})
        runtime_pipeline = self._build_runtime_pipeline(
            robot=robot,
            camera=camera,
            simulator=simulator,
            marker_detector=marker_detector,
            pose_estimator=pose_estimator,
            person_detector=person_detector,
            tracker=tracker,
            pbvs_controller=pbvs_controller,
            avoidance_module=avoidance_module,
            obstacle_source=obstacle_source,
            trajectory_follower=trajectory_follower,
            control_dt=float(runtime_cfg.get("dt", 0.01)),
            enable_avoidance=bool(
                obstacle_cfg.get(
                    "enabled",
                    planning_cfg.get("enable_avoidance", True),
                )
            ),
            desired_target_pose=self._resolve_desired_target_pose(resolved),
        )

        execution_engine = self.build_execution_engine(pipeline=runtime_pipeline)
        runtime_execution_service = self.build_runtime_execution_service()
        experiment_service = self.build_experiment_service()

        return RunPBVSWithAvoidance(
            robot=robot,
            camera=camera,
            simulator=simulator,
            marker_detector=marker_detector,
            pose_estimator=pose_estimator,
            person_detector=person_detector,
            tracker=tracker,
            pbvs_controller=pbvs_controller,
            avoidance_module=avoidance_module,
            obstacle_source=obstacle_source,
            trajectory_follower=trajectory_follower,
            config_service=YAMLConfigurationLoader(),
            execution_engine=execution_engine,
            runtime_execution_service=runtime_execution_service,
            experiment_service=experiment_service,
        )

    def _build_runtime_pipeline(
        self,
        *,
        robot: RobotInterface,
        camera: CameraInterface,
        simulator: SimulatorInterface,
        marker_detector: MarkerDetectorInterface,
        pose_estimator: PoseEstimatorInterface,
        person_detector: PersonDetectorInterface,
        tracker: TrackerInterface,
        pbvs_controller: VisualServoInterface,
        avoidance_module: ObstacleAvoidanceInterface,
        obstacle_source: ObstacleSourceInterface,
        trajectory_follower: ControllerInterface,
        control_dt: float,
        enable_avoidance: bool,
        desired_target_pose: Pose3D,
    ) -> RuntimePipeline:
        steps = [
            SimulatorStep(simulator=simulator),
            SensingStep(robot=robot, camera=camera),
            PerceptionStep(marker_detector=marker_detector, pose_estimator=pose_estimator),
            EstimationStep(
                person_detector=person_detector,
                target_estimator=pose_estimator,
                tracker=tracker,
            ),
            VisualServoStep(
                pbvs_controller=pbvs_controller,
                desired_target_pose=desired_target_pose,
                dt=control_dt,
            ),
        ]

        if enable_avoidance:
            steps.append(
                AvoidanceStep(
                    avoidance_module=avoidance_module,
                    obstacle_source=obstacle_source,
                )
            )

        steps.append(ControlStep(controller=trajectory_follower, dt=control_dt))
        steps.append(ActuationStep(robot=robot))
        visual_success_threshold = float(
            self._config().get("visual_servoing", {}).get(
                "success_threshold",
                self._config().get("visual_servoing", {}).get("convergence_threshold_m", 0.02),
            )
        )
        steps.append(MetricsStep(visual_success_threshold=visual_success_threshold))

        return RuntimePipeline(steps=steps)

    def _resolve_desired_target_pose(self, resolved_config: dict[str, Any]) -> Pose3D:
        target_cfg = resolved_config.get("visual_servoing", {}).get("desired_target_pose", {})
        return Pose3D(
            position=np.asarray(target_cfg.get("position", [0.5, 0.0, 0.5]), dtype=float),
            orientation_quat_xyzw=np.asarray(
                target_cfg.get("orientation_quat_xyzw", [0.0, 0.0, 0.0, 1.0]),
                dtype=float,
            ),
        )

    def _config(self) -> dict[str, Any]:
        if self._resolved_config is None:
            loader = YAMLConfigurationLoader()
            self._resolved_config = loader.resolve(dict(self.config))
        return self._resolved_config

    def _require_sim_client(self) -> Any:
        if self.sim_client is None:
            raise RuntimeError(
                "simulation.backend='coppeliasim' requires sim_client. "
                "Create it with CoppeliaSimClient.connect(config['simulation'])."
            )
        return self.sim_client

    def _require_pyplot_backend(self) -> Any:
        if self.pyplot_backend is None:
            runtime_cfg = self._config().get("runtime", {})
            simulation_cfg = self._config().get("simulation", {})
            joint_names = simulation_cfg.get(
                "joint_names",
                tuple(f"LBR_iiwa_14_R820_joint{i}" for i in range(1, 8)),
            )
            backend = DefaultPyPlotBackend(
                dof=len(tuple(joint_names)),
                dt=float(runtime_cfg.get("dt", 0.01)),
            )
            self.pyplot_backend = backend
        return self.pyplot_backend

    def _simulation_backend_name(self) -> str:
        simulation_cfg = self._config().get("simulation", {})
        return str(simulation_cfg.get("backend", "coppeliasim")).lower()

    def _resolve_person_detector_config(self) -> dict[str, Any]:
        loader = YAMLConfigurationLoader()
        yolo_file_cfg = loader.load("configs/perception/yolo.yaml")
        yolo_section = yolo_file_cfg.get("perception", {}).get("person_detector", {})
        app_section = self._config().get("perception", {}).get("person_detector", {})
        merged: dict[str, Any] = {**yolo_section, **app_section}
        merged["enabled"] = bool(merged.get("enabled", True))
        merged.setdefault("backend", "yolo")
        return merged

    def _load_yolo_model(self, yolo_cfg: dict[str, Any]) -> Any:
        model_name = str(yolo_cfg.get("model_name", "yolo11n.pt"))
        if "." not in model_name:
            model_name = f"{model_name}.pt"
        try:
            from ultralytics import YOLO  # type: ignore
        except Exception as exc:  # pragma: no cover - depends on optional dependency
            raise RuntimeError(
                "Ultralytics is required for the official person detector. "
                "Install optional dependency group 'yolo'."
            ) from exc
        return YOLO(model_name)

    def build_simulation_use_case(self) -> RunJointTrajectory | RunPBVSWithAvoidance:
        """Build the simulation use case declared in app.use_case."""
        use_case_name = str(self._config().get("app", {}).get("use_case", "run_joint_trajectory"))
        if use_case_name == "run_pbvs_with_avoidance":
            return self.build_run_pbvs_with_avoidance()
        return self.build_run_joint_trajectory()

    def build_run_visual_servo(self) -> RunPBVSWithAvoidance:
        """Compatibility alias for the full PBVS experiment use case."""
        return self.build_run_pbvs_with_avoidance()
