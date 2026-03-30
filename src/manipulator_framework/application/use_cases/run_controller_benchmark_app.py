from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from manipulator_framework.application.composition.request_factory import RunRequestFactory
from manipulator_framework.application.dto.run_responses import BenchmarkResponse
from manipulator_framework.application.use_cases.benchmark_controllers import BenchmarkControllers
from manipulator_framework.application.use_cases.run_joint_trajectory import RunJointTrajectory
from manipulator_framework.core.experiments import RunResult


@dataclass
class RunControllerBenchmarkApp:
    """
    App-level orchestration use case for controller benchmark execution.

    It coordinates:
    - benchmark request materialization
    - repeated execution of the baseline run use case
    - summary aggregation through BenchmarkControllers
    """

    request_factory: RunRequestFactory
    run_joint_trajectory_builder: Callable[[], RunJointTrajectory]
    benchmark_use_case: BenchmarkControllers

    def execute(self, config: dict) -> BenchmarkResponse:
        request = self.request_factory.build_benchmark_request()

        seeds = list(config.get("benchmark", {}).get("seeds", []))
        if not seeds:
            base_seed = int(config.get("experiment", {}).get("seed", 0))
            seeds = [base_seed + index for index in range(request.repetitions)]

        method_results: dict[str, list[RunResult]] = {}

        for method_name in request.compared_methods:
            method_results[method_name] = []

            for repetition_index in range(request.repetitions):
                seed = int(seeds[repetition_index])
                run_request = self.request_factory.build_benchmark_run_request(
                    method_name=method_name,
                    repetition_index=repetition_index,
                    seed=seed,
                )
                run_use_case = self.run_joint_trajectory_builder()
                run_response = run_use_case.execute(run_request)
                method_results[method_name].append(run_response.run_result)

        return self.benchmark_use_case.execute(
            request=request,
            method_results=method_results,
        )
