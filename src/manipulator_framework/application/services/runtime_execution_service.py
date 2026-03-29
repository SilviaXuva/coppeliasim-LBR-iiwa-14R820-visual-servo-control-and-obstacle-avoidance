from __future__ import annotations

import math
from dataclasses import dataclass

from manipulator_framework.application.dto.pipeline_execution import (
    ExecutionPlan,
    PipelineExecutionSummary,
)
from manipulator_framework.core.contracts import ClockInterface, ExecutionEngineInterface


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
        duration: float,
        max_cycles: int | None = None,
    ) -> PipelineExecutionSummary:
        plan = self.build_plan(duration=duration, max_cycles=max_cycles)

        execution_engine.reset()
        started_at = self.clock.now()
        cycle_results = execution_engine.run(num_cycles=plan.num_cycles)
        finished_at = started_at + (plan.num_cycles * plan.dt)

        return PipelineExecutionSummary(
            plan=plan,
            cycle_results=cycle_results,
            started_at=started_at,
            finished_at=finished_at,
        )
