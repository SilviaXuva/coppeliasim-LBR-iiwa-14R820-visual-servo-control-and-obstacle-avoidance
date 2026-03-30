from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from manipulator_framework.application.composition.request_factory import RunRequestFactory
from manipulator_framework.application.services.benchmark_service import BenchmarkService
from manipulator_framework.application.services.experiment_service import ExperimentService
from manipulator_framework.application.services.runtime_execution_service import (
    RuntimeExecutionService,
)
from manipulator_framework.application.services.run_result_factory import RunResultFactory
from manipulator_framework.application.use_cases.benchmark_controllers import BenchmarkControllers
from manipulator_framework.application.use_cases.run_controller_benchmark_app import (
    RunControllerBenchmarkApp,
)
from manipulator_framework.application.use_cases.run_joint_trajectory import RunJointTrajectory
from manipulator_framework.application.use_cases.run_pbvs import RunPBVS
from manipulator_framework.application.use_cases.run_pbvs_with_avoidance import RunPBVSWithAvoidance
from manipulator_framework.application.use_cases.run_pbvs_with_tracking import RunPBVSWithTracking
from manipulator_framework.core.contracts import ClockInterface, ExecutionEngineInterface
from manipulator_framework.core.runtime import ExecutionEngine, RuntimePipeline
from manipulator_framework.core.runtime.pipeline_step import PipelineStep
from manipulator_framework.core.runtime.runtime_context import RuntimeContext
from manipulator_framework.core.types import StepResult
from manipulator_framework.infrastructure.persistence.filesystem_results_repository import (
    FileSystemResultsRepository,
)
from manipulator_framework.infrastructure.config.loader import YAMLConfigurationLoader
from manipulator_framework.infrastructure.timing.system_clock import SystemClock


@dataclass(frozen=True)
class _PassiveStep(PipelineStep):
    """Fallback step used by default ApplicationComposer for stub execution."""
    step_label: str

    @property
    def name(self) -> str:
        return self.step_label

    def run(self, context: RuntimeContext) -> StepResult:
        context.metadata[self.step_label] = "passive"
        return StepResult(
            step_name=self.step_label,
            success=True,
            message=f"{self.step_label} step (stub) completed.",
            timestamp=context.timestamp,
        )


@dataclass
class ApplicationComposer:
    """
    Base composition root that builds standard application services and use cases.
    The goal is to maintain a thick application layer where use cases are science-first.
    """
    config: dict[str, Any]

    def build_request_factory(self) -> RunRequestFactory:
        return RunRequestFactory(config=self.config)

    def build_clock(self) -> ClockInterface:
        return SystemClock()

    def build_execution_engine(self) -> ExecutionEngineInterface:
        # Default thin engine with passive steps for testing
        runtime_cfg = self.config.get("runtime", {})
        sampling_period = runtime_cfg.get("dt")
        sampling_period_s = float(sampling_period) if sampling_period is not None else None
        pipeline = RuntimePipeline(
            steps=[
                _PassiveStep("sensing"),
                _PassiveStep("planning"),
                _PassiveStep("control"),
                _PassiveStep("actuation"),
            ]
        )
        return ExecutionEngine(
            clock=self.build_clock(),
            pipeline=pipeline,
            sampling_period_s=sampling_period_s,
        )

    def build_experiment_service(self) -> ExperimentService:
        base_dir = str(self.config.get("results", {}).get("base_dir", "experiments/runs"))
        repository = FileSystemResultsRepository(base_dir=base_dir)
        return ExperimentService(results_repository=repository)

    def build_runtime_execution_service(self) -> RuntimeExecutionService:
        return RuntimeExecutionService(
            clock=self.build_clock(),
        )

    def build_run_result_factory(self) -> RunResultFactory:
        return RunResultFactory()

    def build_run_joint_trajectory(self) -> RunJointTrajectory:
        return RunJointTrajectory(
            execution_engine=self.build_execution_engine(),
            runtime_execution_service=self.build_runtime_execution_service(),
            experiment_service=self.build_experiment_service(),
        )

    def build_run_pbvs_with_avoidance(self) -> RunPBVSWithAvoidance:
        # Note: In specialized composers (like SimulationComposer), 
        # these mocks are replaced with real CoppeliaSim adapters.
        # We provide stubs instead of None to ensure the thick pipeline executes
        from manipulator_framework.adapters.stubs import (
             StubRobot, StubCamera, StubMarkerDetector, StubPoseEstimator,
             StubObstacleSource, StubObstacleAvoidance, StubController
        )
        from manipulator_framework.core.tracking.nearest_neighbor_tracker import NearestNeighborTracker
        from manipulator_framework.adapters.vision.stub_detectors import StubPersonDetector

        from manipulator_framework.core.visual_servoing.pbvs_controller import PBVSController
        from manipulator_framework.core.visual_servoing.reference_generation import PBVSReferenceGenerator

        return RunPBVSWithAvoidance(
            robot=StubRobot(),
            camera=StubCamera(),
            marker_detector=StubMarkerDetector(),
            pose_estimator=StubPoseEstimator(),
            person_detector=StubPersonDetector(),
            tracker=NearestNeighborTracker(),
            pbvs_controller=PBVSController(reference_generator=PBVSReferenceGenerator(gain=0.0)),
            avoidance_module=StubObstacleAvoidance(),
            obstacle_source=StubObstacleSource(),
            trajectory_follower=StubController(),
            config_service=YAMLConfigurationLoader(),
            execution_engine=self.build_execution_engine(),
            runtime_execution_service=self.build_runtime_execution_service(),
            experiment_service=self.build_experiment_service(),
        )

    def build_benchmark_controllers(self) -> BenchmarkControllers:
        return BenchmarkControllers(
            benchmark_service=BenchmarkService(),
        )

    def build_simulation_use_case(self) -> RunPBVSWithAvoidance:
        """App-level alias for the primary simulation use case."""
        return self.build_run_pbvs_with_avoidance()

    def build_experiment_use_case(self) -> RunPBVSWithAvoidance:
        """App-level alias for the primary experimental use case."""
        return self.build_run_pbvs_with_avoidance()

    def build_benchmark_use_case(self) -> RunControllerBenchmarkApp:
        """App-level alias for the controller benchmark orchestrator."""
        return RunControllerBenchmarkApp(
            request_factory=self.build_request_factory(),
            run_joint_trajectory_builder=self.build_run_joint_trajectory,
            benchmark_use_case=self.build_benchmark_controllers(),
        )
