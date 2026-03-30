from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from manipulator_framework.application.dto.pipeline_execution import PipelineExecutionSummary
from manipulator_framework.application.dto.run_requests import RunRequest
from manipulator_framework.core.experiments import RunArtifact, RunResult
from manipulator_framework.core.metrics import MetricsSnapshot, ScalarMetric, compute_success_rate


@dataclass
class RunResultFactory:
    """
    Application factory that converts an execution summary into the canonical RunResult.
    """

    def build(
        self,
        *,
        request: RunRequest,
        experiment_name: str,
        default_scenario_name: str,
        execution_summary: PipelineExecutionSummary,
        artifacts: tuple[RunArtifact, ...] = (),
        extra_scalar_metrics: tuple[ScalarMetric, ...] = (),
        extra_metadata: dict[str, Any] | None = None,
    ) -> RunResult:
        success_metric = compute_success_rate(execution_summary.cycle_success_flags())

        metadata: dict[str, Any] = {
            "num_cycles": execution_summary.plan.num_cycles,
            "dt": execution_summary.plan.dt,
            "duration": execution_summary.plan.duration,
            # Convenience alias for the first cycle (kept for test/backwards compatibility)
            "cycle_index": execution_summary.cycle_results[0].cycle_index if execution_summary.cycle_results else 0,
            "final_cycle_index": execution_summary.final_cycle_result.cycle_index,
            "final_cycle_events": list(execution_summary.final_cycle_result.events),
        }
        if extra_metadata:
            metadata.update(extra_metadata)

        return RunResult(
            run_id=request.run_id,
            success=execution_summary.success,
            num_cycles=execution_summary.plan.num_cycles,
            summary={
                "experiment_name": experiment_name,
                "scenario_name": request.config.get("scenario_name", default_scenario_name),
                "backend_name": request.config.get("backend_name", "mock"),
                **metadata,
            },
            metrics=MetricsSnapshot(
                scalar_metrics=(success_metric, *extra_scalar_metrics),
            ),
            artifacts=artifacts,
            resolved_config=request.config,
            seed=request.seed,
            start_time=execution_summary.started_at,
            end_time=execution_summary.finished_at,
            cycle_results=execution_summary.cycle_results,
        )
