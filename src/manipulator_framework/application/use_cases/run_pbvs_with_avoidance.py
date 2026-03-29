from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.application.dto.run_requests import RunPBVSWithAvoidanceRequest
from manipulator_framework.application.dto.run_responses import RunResponse
from manipulator_framework.application.services.experiment_service import ExperimentService
from manipulator_framework.application.services.run_result_factory import RunResultFactory
from manipulator_framework.application.services.runtime_execution_service import RuntimeExecutionService
from manipulator_framework.core.contracts import ExecutionEngineInterface
from manipulator_framework.core.experiments import RunArtifact


@dataclass
class RunPBVSWithAvoidance:
    """
    Application use case for PBVS + obstacle avoidance execution.
    """
    execution_engine: ExecutionEngineInterface
    runtime_execution_service: RuntimeExecutionService
    run_result_factory: RunResultFactory
    experiment_service: ExperimentService

    def execute(self, request: RunPBVSWithAvoidanceRequest) -> RunResponse:
        execution_summary = self.runtime_execution_service.execute(
            execution_engine=self.execution_engine,
            duration=request.duration,
            max_cycles=request.max_cycles,
        )

        run_result = self.run_result_factory.build(
            request=request,
            experiment_name="run_pbvs_with_avoidance",
            default_scenario_name="pbvs_with_avoidance",
            execution_summary=execution_summary,
            artifacts=(
                RunArtifact(
                    name="avoidance_summary",
                    path=f"experiments/runs/{request.run_id}/avoidance_summary.json",
                    kind="json",
                ),
            ),
            extra_metadata={
                "pipeline_kind": "pbvs_with_avoidance",
                "pipeline_stages": (
                    "sensing",
                    "estimation",
                    "planning",
                    "control",
                    "actuation",
                ),
                "avoidance_enabled": True,
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
