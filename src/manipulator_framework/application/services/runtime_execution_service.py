from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from manipulator_framework.application.dto.pipeline_execution import ExecutionPlan
from manipulator_framework.application.dto.run_requests import RunRequest
from manipulator_framework.core.contracts import ClockInterface, ExecutionEngineInterface
from manipulator_framework.core.experiments import RunResult


@runtime_checkable
class _SamplingConfigurableEngine(Protocol):
    def set_sampling_period(self, sampling_period_s: float) -> None:
        ...


@dataclass
class RuntimeExecutionService:
    """
    Application-level orchestrator for runtime execution planning and aggregation.
    """
    clock: ClockInterface

    def build_plan(
        self,
        duration: float,
        max_cycles: int | None = None,
    ) -> ExecutionPlan:
        if duration <= 0.0:
            raise ValueError("duration must be greater than zero.")

        dt = float(self.clock.dt())
        if dt <= 0.0:
            raise ValueError("clock.dt() must be greater than zero.")

        if max_cycles is not None:
            if max_cycles <= 0:
                raise ValueError("max_cycles must be greater than zero when provided.")
            num_cycles = int(max_cycles)
        else:
            num_cycles = max(1, int(math.ceil(duration / dt)))

        return ExecutionPlan(
            duration=float(duration),
            dt=dt,
            num_cycles=num_cycles,
        )

    def execute(
        self,
        execution_engine: ExecutionEngineInterface,
        request: RunRequest,
        duration: float,
        max_cycles: int | None = None,
    ) -> RunResult:
        plan = self.build_plan(duration=duration, max_cycles=max_cycles)

        if isinstance(execution_engine, _SamplingConfigurableEngine):
            execution_engine.set_sampling_period(plan.dt)

        execution_engine.reset()
        started_at = self.clock.now()
        finished_at = started_at + (plan.num_cycles * plan.dt)

        run_result = execution_engine.run(
            run_id=request.run_id,
            resolved_config=request.config,
            seed=request.seed,
            num_cycles=plan.num_cycles,
            start_time=started_at,
            end_time=finished_at,
        )

        summary = dict(run_result.summary)
        summary.update(
            {
                "planned_duration": plan.duration,
                "planned_dt": plan.dt,
                "planned_num_cycles": plan.num_cycles,
            }
        )

        from dataclasses import replace

        return replace(run_result, summary=summary)
