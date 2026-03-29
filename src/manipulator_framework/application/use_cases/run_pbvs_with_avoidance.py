from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.application.dto.run_requests import RunPBVSWithAvoidanceRequest
from manipulator_framework.application.dto.run_responses import RunResponse
from manipulator_framework.application.services.experiment_service import ExperimentService
from manipulator_framework.core.contracts import ClockInterface, ExecutionEngineInterface
from manipulator_framework.core.experiments import RunArtifact, RunResult, RunSchema
from manipulator_framework.core.metrics import MetricsSnapshot, ScalarMetric


@dataclass
class RunPBVSWithAvoidance:
    """
    Application use case for PBVS + obstacle avoidance execution.
    """
    execution_engine: ExecutionEngineInterface
    clock: ClockInterface
    experiment_service: ExperimentService

    def execute(self, request: RunPBVSWithAvoidanceRequest) -> RunResponse:
        started_at = self.clock.now()
        cycle_result = self.execution_engine.step()
        cycle_success = cycle_result.success
        cycle_index = cycle_result.cycle_index
        finished_at = self.clock.now()

        result = RunResult(
            run_schema=RunSchema(
                run_id=request.run_id,
                experiment_name="run_pbvs_with_avoidance",
                scenario_name=request.config.get("scenario_name", "pbvs_with_avoidance"),
                backend_name=request.config.get("backend_name", "mock"),
                seed=request.seed,
                resolved_config=request.config,
            ),
            metrics=MetricsSnapshot(
                scalar_metrics=(
                    ScalarMetric("success_rate", 1.0 if cycle_success else 0.0, "ratio"),
                ),
            ),
            artifacts=(
                RunArtifact(
                    name="avoidance_summary",
                    path=f"experiments/runs/{request.run_id}/avoidance_summary.json",
                    kind="json",
                ),
            ),
            success=cycle_success,
            started_at=started_at,
            finished_at=finished_at,
            metadata={"cycle_index": cycle_index},
        )

        self.experiment_service.persist(result)
        return RunResponse(run_result=result)
