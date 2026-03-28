from __future__ import annotations

from dataclasses import dataclass, field

from manipulator_framework.core.contracts import ClockInterface, ExecutionEngineInterface
from .cycle_contract import CycleResult
from .pipeline import RuntimePipeline
from .runtime_context import RuntimeContext


@dataclass
class ExecutionEngine(ExecutionEngineInterface):
    """
    Pure step-based execution engine.
    """
    clock: ClockInterface
    pipeline: RuntimePipeline
    _cycle_index: int = field(default=0, init=False, repr=False)

    def step(self) -> CycleResult:
        timestamp = self.clock.now()

        context = RuntimeContext(
            cycle_index=self._cycle_index,
            timestamp=timestamp,
        )

        step_results = self.pipeline.run_cycle(context)
        success = all(result.success for result in step_results)

        cycle_result = CycleResult(
            cycle_index=self._cycle_index,
            success=success,
            step_results=step_results,
            timestamp=timestamp,
            message="Cycle completed." if success else "Cycle failed.",
        )

        self._cycle_index += 1
        return cycle_result

    def run(self, num_cycles: int = 1) -> tuple[CycleResult, ...]:
        """
        Run one or more execution cycles synchronously.
        """
        if num_cycles <= 0:
            raise ValueError("num_cycles must be greater than zero.")

        results = []
        for _ in range(num_cycles):
            results.append(self.step())

        return tuple(results)

    def reset(self) -> None:
        self._cycle_index = 0
