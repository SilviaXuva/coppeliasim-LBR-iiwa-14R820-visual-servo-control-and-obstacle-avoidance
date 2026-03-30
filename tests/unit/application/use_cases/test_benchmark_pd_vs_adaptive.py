from __future__ import annotations

from manipulator_framework.core.experiments import (
    BenchmarkComparison,
    ExperimentProtocol,
    RunArtifact,
    RunResult,
    ScenarioDefinition,
)
from manipulator_framework.core.metrics import MetricsSnapshot, ScalarMetric


def make_run_result(method: str, repetition: int, seed: int, rmse: float) -> RunResult:
    metrics = MetricsSnapshot(
        scalar_metrics=(
            ScalarMetric(name="joint_position_rmse", value=rmse, unit="rad"),
            ScalarMetric(name="success_rate", value=1.0, unit="ratio"),
        )
    )

    return RunResult(
        run_id=f"{method}_{repetition}",
        success=True,
        num_cycles=1,
        summary={
            "experiment_name": "pd_vs_adaptive_pd",
            "scenario_name": "synthetic_joint_tracking",
            "backend_name": "mock_backend",
            "method": method,
            "repetition": repetition,
        },
        metrics=metrics,
        artifacts=(
            RunArtifact(
                name="summary",
                path=f"runs/{method}_{repetition}/summary.json",
                kind="json",
            ),
        ),
        resolved_config={"controller": method, "dt": 0.01},
        seed=seed,
        start_time=0.0,
        end_time=5.0,
    )


def test_benchmark_comparison_validates_same_protocol_for_pd_and_adaptive() -> None:
    scenario = ScenarioDefinition(
        name="synthetic_joint_tracking",
        description="Same protocol for PD and adaptive PD.",
        parameters={"reference": "step", "dof": 7},
    )

    protocol = ExperimentProtocol(
        name="benchmark_pd_vs_adaptive_pd",
        scenario=scenario,
        repetitions=2,
        seeds=(101, 202),
        compared_methods=("pd", "adaptive_pd"),
        resolved_config={"dt": 0.01, "duration": 5.0},
    )

    comparison = BenchmarkComparison(
        protocol=protocol,
        method_results={
            "pd": (
                make_run_result("pd", 0, 101, 0.045),
                make_run_result("pd", 1, 202, 0.043),
            ),
            "adaptive_pd": (
                make_run_result("adaptive_pd", 0, 101, 0.031),
                make_run_result("adaptive_pd", 1, 202, 0.030),
            ),
        },
    )

    comparison.validate()

    assert len(comparison.method_results["pd"]) == 2
    assert len(comparison.method_results["adaptive_pd"]) == 2
