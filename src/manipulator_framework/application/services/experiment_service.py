from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.contracts import ResultsRepositoryInterface
from manipulator_framework.core.experiments import RunResult
from manipulator_framework.core.runtime import CycleResult


@dataclass
class ExperimentService:
    """
    Application service responsible for persisting canonical run outputs
    and the runtime cycle series associated with the run.
    """
    results_repository: ResultsRepositoryInterface

    def persist(
        self,
        result: RunResult,
        cycle_results: tuple[CycleResult, ...] = (),
    ) -> None:
        self.results_repository.save_result(result)

        if cycle_results:
            samples = []
            for cycle_result in cycle_results:
                samples.append(
                    {
                        "t": cycle_result.timestamp,
                        "cycle_index": cycle_result.cycle_index,
                        "success": 1.0 if cycle_result.success else 0.0,
                        "num_steps": float(len(cycle_result.step_results)),
                        "message": cycle_result.message,
                    }
                )

            self.results_repository.save_timeseries(
                run_id=result.run_id,
                series_name="runtime_cycles",
                samples=samples,
            )
