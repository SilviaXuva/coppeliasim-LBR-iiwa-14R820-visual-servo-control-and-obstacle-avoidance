from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.application.dto.run_requests import BenchmarkControllersRequest
from manipulator_framework.application.dto.run_responses import BenchmarkResponse
from manipulator_framework.application.services.benchmark_service import BenchmarkService
from manipulator_framework.core.experiments import ExperimentProtocol, RunResult, ScenarioDefinition


@dataclass
class BenchmarkControllers:
    """
    Application use case for controller benchmarking.
    """
    benchmark_service: BenchmarkService

    def execute(
        self,
        request: BenchmarkControllersRequest,
        method_results: dict[str, list[RunResult]],
    ) -> BenchmarkResponse:
        protocol = ExperimentProtocol(
            name="benchmark_controllers",
            scenario=ScenarioDefinition(
                name=request.config.get("scenario_name", "controller_benchmark"),
                description="Controller benchmark under common protocol.",
                parameters=request.config,
            ),
            repetitions=request.repetitions,
            seeds=tuple(request.config.get("seeds", tuple(range(request.repetitions)))),
            compared_methods=request.compared_methods,
            resolved_config=request.config,
        )

        summary = self.benchmark_service.build_summary(protocol, method_results)
        return BenchmarkResponse(summary=summary)
