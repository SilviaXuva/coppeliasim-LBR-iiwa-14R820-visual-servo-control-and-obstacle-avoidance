from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.application.dto.run_requests import RunJointTrajectoryRequest
from manipulator_framework.application.dto.run_responses import RunResponse
from manipulator_framework.application.services.experiment_service import ExperimentService
from manipulator_framework.core.contracts import ClockInterface, ControllerInterface, ExecutionEngineInterface
from manipulator_framework.core.experiments import RunArtifact, RunResult, RunSchema
from manipulator_framework.core.metrics import MetricsSnapshot, ScalarMetric


@dataclass
class RunJointTrajectory:
    """
    Application use case for joint trajectory execution.
    """
    execution_engine: ExecutionEngineInterface
    clock: ClockInterface
    experiment_service: ExperimentService

    def execute(self, request: RunJointTrajectoryRequest) -> RunResponse:
        started_at = self.clock.now()
        cycle_result = self.execution_engine.step()
        cycle_success = bool(cycle_result["success"])
        cycle_index = int(cycle_result["cycle_index"])
        finished_at = self.clock.now()

        run_result = RunResult(
            run_schema=RunSchema(
                run_id=request.run_id,
                experiment_name="run_joint_trajectory",
                scenario_name=request.config.get("scenario_name", "synthetic_joint_trajectory"),
                backend_name=request.config.get("backend_name", "mock"),
                seed=request.seed,
                resolved_config=request.config,
            ),
            metrics=MetricsSnapshot(
                scalar_metrics=(
                    ScalarMetric(
                        name="success_rate",
                        value=1.0 if cycle_success else 0.0,
                        unit="ratio",
                    ),
                ),
            ),
            artifacts=(
                RunArtifact(
                    name="cycle_result",
                    path=f"experiments/runs/{request.run_id}/cycle_result.json",
                    kind="json",
                ),
            ),
            success=cycle_success,
            started_at=started_at,
            finished_at=finished_at,
            metadata={"cycle_index": cycle_index},
        )

        self.experiment_service.persist(run_result)
        return RunResponse(run_result=run_result)
