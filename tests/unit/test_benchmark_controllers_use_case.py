from __future__ import annotations

from manipulator_framework.application.composition.mock_composer import MockApplicationComposer
from manipulator_framework.application.dto.run_requests import BenchmarkControllersRequest
from manipulator_framework.core.experiments import RunResult, RunSchema
from manipulator_framework.core.metrics import MetricsSnapshot, ScalarMetric
from tests.fixtures.application_fakes import FakeClock, FakeExecutionEngine, InMemoryResultsRepository


def make_result(method: str, idx: int, seed: int, rmse: float) -> RunResult:
    return RunResult(
        run_schema=RunSchema(
            run_id=f"{method}_{idx}",
            experiment_name="benchmark_controllers",
            scenario_name="controller_benchmark",
            backend_name="mock",
            seed=seed,
            resolved_config={"controller": method},
        ),
        metrics=MetricsSnapshot(
            scalar_metrics=(ScalarMetric("joint_position_rmse", rmse, "rad"),),
        ),
        success=True,
        started_at=0.0,
        finished_at=1.0,
        metadata={},
    )


def test_benchmark_controllers_returns_summary() -> None:
    composer = MockApplicationComposer(
        clock=FakeClock(),
        execution_engine=FakeExecutionEngine(),
        results_repository=InMemoryResultsRepository(),
    )

    use_case = composer.build_benchmark_controllers()
    response = use_case.execute(
        request=BenchmarkControllersRequest(
            run_id="benchmark_001",
            config={"scenario_name": "controller_benchmark", "seeds": (10, 20)},
            seed=0,
            compared_methods=("pd", "adaptive_pd"),
            repetitions=2,
        ),
        method_results={
            "pd": [
                make_result("pd", 0, 10, 0.05),
                make_result("pd", 1, 20, 0.04),
            ],
            "adaptive_pd": [
                make_result("adaptive_pd", 0, 10, 0.03),
                make_result("adaptive_pd", 1, 20, 0.02),
            ],
        },
    )

    assert "pd" in response.summary
    assert "adaptive_pd" in response.summary
    assert len(response.summary["pd"]) == 2
