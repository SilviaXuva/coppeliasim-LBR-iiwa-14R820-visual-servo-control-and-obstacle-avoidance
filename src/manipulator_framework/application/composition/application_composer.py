from __future__ import annotations

from dataclasses import dataclass
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
from manipulator_framework.core.runtime import ExecutionEngine, RuntimePipeline, StepResult
from manipulator_framework.core.runtime.pipeline_step import PipelineStep
from manipulator_framework.core.runtime.runtime_context import RuntimeContext
from manipulator_framework.infrastructure.persistence.filesystem_results_repository import (
    FileSystemResultsRepository,
)
from manipulator_framework.infrastructure.timing.system_clock import SystemClock


@dataclass
class _PassiveStep(PipelineStep):
    step_label: str

    @property
    def name(self) -> str:
        return self.step_label

    def run(self, context: RuntimeContext) -> StepResult:
        context.metadata[self.step_label] = "ok"
        return StepResult(
            step_name=self.step_label,
            success=True,
            message=f"{self.step_label} step completed.",
            timestamp=context.timestamp,
        )


@dataclass
class ApplicationComposer:
    config: dict[str, Any]

    def build_request_factory(self) -> RunRequestFactory:
        return RunRequestFactory(config=self.config)

    def build_clock(self) -> ClockInterface:
        return SystemClock()

    def build_execution_engine(self) -> ExecutionEngineInterface:
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
            run_result_factory=self.build_run_result_factory(),
        )

    def build_run_pbvs(self) -> RunPBVS:
        return RunPBVS(
            execution_engine=self.build_execution_engine(),
            runtime_execution_service=self.build_runtime_execution_service(),
            experiment_service=self.build_experiment_service(),
            run_result_factory=self.build_run_result_factory(),
        )

    def build_run_pbvs_with_tracking(self) -> RunPBVSWithTracking:
        return RunPBVSWithTracking(
            execution_engine=self.build_execution_engine(),
            runtime_execution_service=self.build_runtime_execution_service(),
            experiment_service=self.build_experiment_service(),
            run_result_factory=self.build_run_result_factory(),
        )

    def build_run_pbvs_with_avoidance(self) -> RunPBVSWithAvoidance:
        return RunPBVSWithAvoidance(
            execution_engine=self.build_execution_engine(),
            runtime_execution_service=self.build_runtime_execution_service(),
            experiment_service=self.build_experiment_service(),
            run_result_factory=self.build_run_result_factory(),
        )

    def build_benchmark_controllers(self) -> BenchmarkControllers:
        return BenchmarkControllers(
            benchmark_service=BenchmarkService(),
        )

    def build_benchmark_app_use_case(self) -> RunControllerBenchmarkApp:
        return RunControllerBenchmarkApp(
            request_factory=self.build_request_factory(),
            run_joint_trajectory_builder=self.build_run_joint_trajectory,
            benchmark_use_case=self.build_benchmark_controllers(),
        )
