from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.core.experiments import ExperimentProtocol, RunResult


@dataclass
class BenchmarkService:
    """
    Application helper for organizing controller benchmark outputs.
    """

    def build_summary(
        self,
        protocol: ExperimentProtocol,
        method_results: dict[str, list[RunResult]],
    ) -> dict[str, tuple[RunResult, ...]]:
        summary: dict[str, tuple[RunResult, ...]] = {}
        for method in protocol.compared_methods:
            results = method_results.get(method, [])
            if len(results) != protocol.repetitions:
                raise ValueError(
                    f"Method {method} must contain {protocol.repetitions} runs."
                )
            summary[method] = tuple(results)
        return summary
