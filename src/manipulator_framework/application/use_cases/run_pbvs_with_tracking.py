from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace

from manipulator_framework.application.dto.run_requests import RunPBVSWithTrackingRequest
from manipulator_framework.application.dto.run_responses import RunResponse
from manipulator_framework.application.services.experiment_service import ExperimentService
from manipulator_framework.application.services.runtime_execution_service import RuntimeExecutionService
from manipulator_framework.core.contracts import ExecutionEngineInterface


@dataclass
class RunPBVSWithTracking:
    """
    Application use case for PBVS + tracking execution.
    """
    execution_engine: ExecutionEngineInterface
    runtime_execution_service: RuntimeExecutionService
    experiment_service: ExperimentService

    def execute(self, request: RunPBVSWithTrackingRequest) -> RunResponse:
        run_result = self.runtime_execution_service.execute(
            execution_engine=self.execution_engine,
            request=request,
            duration=request.duration,
            max_cycles=request.max_cycles,
        )

        run_result = replace(
            run_result,
            summary={
                **run_result.summary,
                "experiment_name": "run_pbvs_with_tracking",
                "scenario_name": request.config.get("scenario_name", "pbvs_with_tracking"),
                "backend_name": request.config.get("backend_name", "mock"),
                "pipeline_stages": (
                    "sensing",
                    "estimation",
                    "planning",
                    "control",
                    "actuation",
                ),
            },
        )

        self.experiment_service.persist(result=run_result)

        return RunResponse(run_result=run_result)
