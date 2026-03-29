from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.application.dto.run_requests import RunJointTrajectoryRequest
from manipulator_framework.application.dto.run_responses import RunResponse
from manipulator_framework.application.services.experiment_service import ExperimentService
from manipulator_framework.application.services.run_result_factory import RunResultFactory
from manipulator_framework.application.services.runtime_execution_service import RuntimeExecutionService
from manipulator_framework.core.contracts import ExecutionEngineInterface
from manipulator_framework.core.experiments import RunArtifact


@dataclass
class RunJointTrajectory:
    """
    Application use case for joint trajectory execution.
    Explicitly orchestrates runtime execution, result assembly and persistence.
    """
    execution_engine: ExecutionEngineInterface
    runtime_execution_service: RuntimeExecutionService
    run_result_factory: RunResultFactory
    experiment_service: ExperimentService

    def execute(self, request: RunJointTrajectoryRequest) -> RunResponse:
        execution_summary = self.runtime_execution_service.execute(
            execution_engine=self.execution_engine,
            duration=request.duration,
            max_cycles=request.max_cycles,
        )

        run_result = self.run_result_factory.build(
            request=request,
            experiment_name="run_joint_trajectory",
            default_scenario_name="synthetic_joint_trajectory",
            execution_summary=execution_summary,
            artifacts=(
                RunArtifact(
                    name="cycle_result",
                    path=f"experiments/runs/{request.run_id}/cycle_result.json",
                    kind="json",
                ),
            ),
            extra_metadata={
                "pipeline_kind": "joint_trajectory",
                "pipeline_stages": (
                    "planning",
                    "control",
                    "actuation",
                ),
            },
        )

        self.experiment_service.persist(
            result=run_result,
            cycle_results=execution_summary.cycle_results,
        )

        return RunResponse(
            execution_plan=execution_summary.plan,
            cycle_results=execution_summary.cycle_results,
            cycle_result=execution_summary.final_cycle_result,
            run_result=run_result,
        )
