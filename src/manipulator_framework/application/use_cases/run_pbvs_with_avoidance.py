from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Any

import numpy as np
from manipulator_framework.application.dto.run_requests import RunPBVSWithAvoidanceRequest
from manipulator_framework.application.dto.run_responses import RunResponse
from manipulator_framework.application.services.experiment_service import ExperimentService
from manipulator_framework.application.services.runtime_execution_service import RuntimeExecutionService
from manipulator_framework.core.contracts import (
    CameraInterface,
    ConfigurationInterface,
    ControllerInterface,
    ExecutionEngineInterface,
    MarkerDetectorInterface,
    PersonDetectorInterface,
    PoseEstimatorInterface,
    RobotInterface,
    TrackerInterface,
    ObstacleAvoidanceInterface,
    ObstacleSourceInterface,
    SimulatorInterface,
    VisualServoInterface,
)
from manipulator_framework.core.experiments import RunArtifact, RunResult
from manipulator_framework.core.metrics import MetricsSnapshot, ScalarMetric
from manipulator_framework.core.runtime import (
    ActuationStep,
    AvoidanceStep,
    ControlStep,
    EstimationStep,
    MetricsStep,
    PerceptionStep,
    RuntimePipeline,
    SimulatorStep,
    SensingStep,
    VisualServoStep,
)
from manipulator_framework.core.types import Pose3D


@dataclass(frozen=True)
class PBVSAvoidanceExecutionRequest:
    """
    Resolved execution request for the official PBVS + avoidance experiment pipeline.
    """

    resolved_config: dict[str, Any]
    duration: float
    max_cycles: int | None
    control_dt: float
    seed: int
    enable_avoidance: bool
    desired_target_pose: Pose3D


@dataclass
class RunPBVSWithAvoidance:
    """
    Thickened application use case for PBVS + Obstacle Avoidance.
    
    Instead of being a thin wrapper, this use case represents the real scientific pipeline.
    It orchestrates the specific sequence of sensing, perception, tracking, 
    PBVS control, and obstacle avoidance as a first-class citizen of the application layer.
    """
    # Dependencies required for the scientific pipeline (Domain Components)
    robot: RobotInterface
    camera: CameraInterface
    marker_detector: MarkerDetectorInterface
    pose_estimator: PoseEstimatorInterface
    person_detector: PersonDetectorInterface
    tracker: TrackerInterface
    pbvs_controller: VisualServoInterface
    avoidance_module: ObstacleAvoidanceInterface
    obstacle_source: ObstacleSourceInterface
    
    # Secondary controller to track the generated trajectory
    trajectory_follower: ControllerInterface

    # Infrastructure services
    config_service: ConfigurationInterface
    execution_engine: ExecutionEngineInterface
    runtime_execution_service: RuntimeExecutionService
    experiment_service: ExperimentService
    simulator: SimulatorInterface | None = None

    def execute(self, request: RunPBVSWithAvoidanceRequest) -> RunResponse:
        execution_request = self._resolve_execution_request(request)
        pipeline = self._build_runtime_pipeline(execution_request)

        # 1. Assemble and bind official runtime pipeline
        self.execution_engine.set_pipeline(pipeline)

        if self.simulator is not None:
            self.simulator.start()

        try:
            # 2. Execute resolved run plan
            run_result = self.runtime_execution_service.execute(
                execution_engine=self.execution_engine,
                request=replace(
                    request,
                    config=execution_request.resolved_config,
                    seed=execution_request.seed,
                ),
                duration=execution_request.duration,
                max_cycles=execution_request.max_cycles,
            )
        finally:
            if self.simulator is not None:
                self.simulator.stop()

        run_result = self._enrich_scientific_metrics(
            run_result=run_result,
            execution_request=execution_request,
        )

        # 3. Enrich canonical run result with experiment-level metadata
        run_result = replace(
            run_result,
            artifacts=(
                RunArtifact(
                    name="scientific_summary",
                    path=f"experiments/runs/{request.run_id}/summary.json",
                    kind="json",
                    description="Full PBVS-Avoidance scientific report.",
                ),
            ),
            summary={
                **run_result.summary,
                "experiment_name": "run_pbvs_with_avoidance",
                "scenario_name": execution_request.resolved_config.get(
                    "scenario_name",
                    "pbvs_with_avoidance_scene",
                ),
                "backend_name": execution_request.resolved_config.get("backend_name", "mock"),
                "pipeline_kind": "official_pbvs_with_avoidance",
                "pipeline_stages": (
                    "sensing",
                    "perception",
                    "estimation",
                    "visual_servo",
                    "avoidance" if execution_request.enable_avoidance else "avoidance_disabled",
                    "control",
                    "actuation",
                    "metrics_collection",
                ),
                "avoidance_enabled": execution_request.enable_avoidance,
                "control_dt": execution_request.control_dt,
                "seed": execution_request.seed,
                "tracking_mode": execution_request.resolved_config.get("tracking", {}).get(
                    "mode",
                    "nearest_neighbor",
                ),
            },
        )

        # 4. Persist scientific traceability bundle
        self.experiment_service.persist(result=run_result)

        return RunResponse(run_result=run_result)

    def _enrich_scientific_metrics(
        self,
        *,
        run_result: RunResult,
        execution_request: PBVSAvoidanceExecutionRequest,
    ) -> RunResult:
        cycles = list(run_result.cycle_results)
        detection_rate = 0.0
        if cycles:
            detection_rate = float(
                sum(
                    1
                    for cycle in cycles
                    if int(cycle.observations.get("num_person_detections", 0)) > 0
                )
            ) / float(len(cycles))

        final_visual_error = 0.0
        for cycle in reversed(cycles):
            value = cycle.metrics_delta.get("visual_translation_error")
            if isinstance(value, (int, float)):
                final_visual_error = float(value)
                break

        minimum_clearance = float(
            execution_request.resolved_config.get("obstacle_avoidance", {}).get("clearance_m", 0.0)
        )
        clearance_values = [
            float(cycle.metrics_delta["minimum_clearance"])
            for cycle in cycles
            if "minimum_clearance" in cycle.metrics_delta
            and isinstance(cycle.metrics_delta["minimum_clearance"], (int, float))
        ]
        if clearance_values:
            minimum_clearance = min(clearance_values)

        convergence_threshold = float(
            execution_request.resolved_config.get("visual_servoing", {}).get(
                "convergence_threshold_m",
                0.02,
            )
        )
        convergence_time = float(run_result.end_time - run_result.start_time)
        for cycle in cycles:
            value = cycle.metrics_delta.get("visual_translation_error")
            if isinstance(value, (int, float)) and float(value) <= convergence_threshold:
                convergence_time = max(0.0, float(cycle.timestamp - run_result.start_time))
                break

        protocol_scalars = (
            ScalarMetric(name="task_success", value=1.0 if run_result.success else 0.0, unit="ratio"),
            ScalarMetric(
                name="final_visual_error",
                value=final_visual_error,
                unit="m",
                description="Final PBVS translation error.",
            ),
            ScalarMetric(
                name="minimum_clearance",
                value=minimum_clearance,
                unit="m",
                description="Minimum observed clearance to obstacles.",
            ),
            ScalarMetric(
                name="convergence_time",
                value=convergence_time,
                unit="s",
                description="Time until visual error reaches protocol threshold.",
            ),
            ScalarMetric(name="num_cycles_total", value=float(run_result.num_cycles), unit="cycles"),
            ScalarMetric(
                name="valid_detection_rate",
                value=detection_rate,
                unit="ratio",
                description="Fraction of cycles with at least one person detection.",
            ),
        )

        summary = dict(run_result.summary)
        summary.update(
            {
                "task_success": bool(run_result.success),
                "final_visual_error": final_visual_error,
                "minimum_clearance": minimum_clearance,
                "convergence_time": convergence_time,
                "num_cycles_total": run_result.num_cycles,
                "valid_detection_rate": detection_rate,
            }
        )

        metrics = MetricsSnapshot(
            scalar_metrics=tuple(run_result.metrics.scalar_metrics) + protocol_scalars,
            series=dict(run_result.metrics.series),
            metadata=dict(run_result.metrics.metadata),
        )

        return replace(run_result, summary=summary, metrics=metrics)

    def _resolve_execution_request(
        self,
        request: RunPBVSWithAvoidanceRequest,
    ) -> PBVSAvoidanceExecutionRequest:
        resolved_config = self.config_service.resolve(request.config)

        runtime_cfg = resolved_config.get("runtime", {})
        planning_cfg = resolved_config.get("planning", {})
        experiment_cfg = resolved_config.get("experiment", {})
        obstacle_cfg = resolved_config.get("obstacle_avoidance", {})

        duration = float(request.duration)
        if duration <= 0.0:
            duration = float(planning_cfg.get("duration", 1.0))

        seed = int(request.seed) if int(request.seed) != 0 else int(experiment_cfg.get("seed", 0))

        avoidance_enabled_by_config = bool(
            obstacle_cfg.get(
                "enabled",
                planning_cfg.get("enable_avoidance", True),
            )
        )

        return PBVSAvoidanceExecutionRequest(
            resolved_config=resolved_config,
            duration=duration,
            max_cycles=request.max_cycles,
            control_dt=float(runtime_cfg.get("dt", 0.01)),
            seed=seed,
            enable_avoidance=bool(request.enable_avoidance and avoidance_enabled_by_config),
            desired_target_pose=self._resolve_desired_target_pose(resolved_config),
        )

    def _build_runtime_pipeline(
        self,
        request: PBVSAvoidanceExecutionRequest,
    ) -> RuntimePipeline:
        # Official scientific pipeline for the application layer:
        # robot state -> camera frame -> detection -> pose estimation -> tracking
        # -> PBVS -> obstacle avoidance -> joint command -> metrics
        steps = [
            *([SimulatorStep(simulator=self.simulator)] if self.simulator is not None else []),
            SensingStep(robot=self.robot, camera=self.camera),
            PerceptionStep(
                marker_detector=self.marker_detector,
                pose_estimator=self.pose_estimator,
            ),
            EstimationStep(
                person_detector=self.person_detector,
                target_estimator=self.pose_estimator,
                tracker=self.tracker,
            ),
            VisualServoStep(
                pbvs_controller=self.pbvs_controller,
                desired_target_pose=request.desired_target_pose,
                dt=request.control_dt,
            ),
        ]

        if request.enable_avoidance:
            steps.append(
                AvoidanceStep(
                    avoidance_module=self.avoidance_module,
                    obstacle_source=self.obstacle_source,
                )
            )

        steps.append(ControlStep(controller=self.trajectory_follower, dt=request.control_dt))
        steps.append(ActuationStep(robot=self.robot))
        visual_success_threshold = float(
            request.resolved_config.get("visual_servoing", {}).get(
                "success_threshold",
                request.resolved_config.get("visual_servoing", {}).get("convergence_threshold_m", 0.02),
            )
        )
        steps.append(MetricsStep(visual_success_threshold=visual_success_threshold))

        return RuntimePipeline(steps=steps)

    def _resolve_desired_target_pose(self, resolved_config: dict[str, Any]) -> Pose3D:
        target_cfg = resolved_config.get("visual_servoing", {}).get("desired_target_pose", {})

        position = target_cfg.get("position", [0.5, 0.0, 0.5])
        orientation = target_cfg.get("orientation_quat_xyzw", [0.0, 0.0, 0.0, 1.0])

        return Pose3D(
            position=np.asarray(position, dtype=float),
            orientation_quat_xyzw=np.asarray(orientation, dtype=float),
        )
