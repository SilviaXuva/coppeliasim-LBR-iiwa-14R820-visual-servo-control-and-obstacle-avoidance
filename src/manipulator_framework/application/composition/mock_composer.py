from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.application.services.benchmark_service import BenchmarkService
from manipulator_framework.application.services.experiment_service import ExperimentService
from manipulator_framework.application.services.runtime_execution_service import (
    RuntimeExecutionService,
)
from manipulator_framework.application.services.run_result_factory import RunResultFactory
from manipulator_framework.application.use_cases.benchmark_controllers import BenchmarkControllers
from manipulator_framework.application.use_cases.run_joint_trajectory import RunJointTrajectory
from manipulator_framework.application.use_cases.run_pbvs import RunPBVS
from manipulator_framework.application.use_cases.run_pbvs_with_avoidance import RunPBVSWithAvoidance
from manipulator_framework.application.use_cases.run_pbvs_with_tracking import RunPBVSWithTracking
from manipulator_framework.core.contracts import (
    ClockInterface,
    ExecutionEngineInterface,
    ResultsRepositoryInterface,
)


@dataclass
class MockApplicationComposer:
    clock: ClockInterface
    execution_engine: ExecutionEngineInterface
    results_repository: ResultsRepositoryInterface

    def build_experiment_service(self) -> ExperimentService:
        return ExperimentService(self.results_repository)

    def build_runtime_execution_service(self) -> RuntimeExecutionService:
        return RuntimeExecutionService(
            clock=self.clock,
        )

    def build_run_result_factory(self) -> RunResultFactory:
        return RunResultFactory()

    def build_run_joint_trajectory(self) -> RunJointTrajectory:
        return RunJointTrajectory(
            execution_engine=self.execution_engine,
            runtime_execution_service=self.build_runtime_execution_service(),
            experiment_service=self.build_experiment_service(),
            run_result_factory=self.build_run_result_factory(),
        )

    def build_run_pbvs(self) -> RunPBVS:
        return RunPBVS(
            execution_engine=self.execution_engine,
            runtime_execution_service=self.build_runtime_execution_service(),
            experiment_service=self.build_experiment_service(),
            run_result_factory=self.build_run_result_factory(),
        )

    def build_run_pbvs_with_tracking(self) -> RunPBVSWithTracking:
        return RunPBVSWithTracking(
            execution_engine=self.execution_engine,
            runtime_execution_service=self.build_runtime_execution_service(),
            experiment_service=self.build_experiment_service(),
            run_result_factory=self.build_run_result_factory(),
        )

    def build_run_pbvs_with_avoidance(self) -> RunPBVSWithAvoidance:
        return RunPBVSWithAvoidance(
            execution_engine=self.execution_engine,
            runtime_execution_service=self.build_runtime_execution_service(),
            experiment_service=self.build_experiment_service(),
            run_result_factory=self.build_run_result_factory(),
        )

    def build_benchmark_controllers(self) -> BenchmarkControllers:
        return BenchmarkControllers(
            benchmark_service=BenchmarkService(),
        )
