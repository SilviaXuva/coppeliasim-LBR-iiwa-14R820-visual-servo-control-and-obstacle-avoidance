from __future__ import annotations

from dataclasses import dataclass, field

from .protocol import ExperimentProtocol
from .result_model import RunResult


@dataclass(frozen=True)
class BenchmarkComparison:
    protocol: ExperimentProtocol
    method_results: dict[str, tuple[RunResult, ...]]

    def validate(self) -> None:
        for method in self.protocol.compared_methods:
            if method not in self.method_results:
                raise ValueError(f"Missing results for method: {method}")
            if len(self.method_results[method]) != self.protocol.repetitions:
                raise ValueError(
                    f"Method {method} must have {self.protocol.repetitions} run results."
                )
