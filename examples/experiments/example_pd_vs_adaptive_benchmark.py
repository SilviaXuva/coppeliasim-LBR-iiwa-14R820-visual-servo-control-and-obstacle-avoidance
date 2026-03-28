from __future__ import annotations

from manipulator_framework.core.experiments import (
    BenchmarkComparison,
    ExperimentProtocol,
    RunArtifact,
    RunResult,
    RunSchema,
    ScenarioDefinition,
)
from manipulator_framework.core.metrics import MetricsSnapshot, ScalarMetric


def make_run_result(method: str, repetition: int, seed: int, rmse: float, latency: float) -> RunResult:
    run_schema = RunSchema(
        run_id=f"{method}_rep_{repetition}",
        experiment_name="pd_vs_adaptive_pd",
        scenario_name="synthetic_joint_tracking",
        backend_name="mock_backend",
        seed=seed,
        resolved_config={
            "controller": method,
            "dt": 0.01,
            "horizon": 5.0,
        },
        tags=("benchmark", method),
    )

    metrics = MetricsSnapshot(
        scalar_metrics=(
            ScalarMetric("joint_position_rmse", rmse, "rad"),
            ScalarMetric("mean_cycle_latency", latency, "s"),
            ScalarMetric("success_rate", 1.0, "ratio"),
        )
    )

    return RunResult(
        run_schema=run_schema,
        metrics=metrics,
        artifacts=(
            RunArtifact(
                name="summary",
                path=f"experiments/runs/{method}_rep_{repetition}/summary.json",
                kind="json",
            ),
        ),
        success=True,
        started_at=0.0,
        finished_at=5.0,
        metadata={"repetition": repetition, "method": method},
    )


def main() -> None:
    scenario = ScenarioDefinition(
        name="synthetic_joint_tracking",
        description="Same synthetic joint tracking reference for controller comparison.",
        parameters={"dof": 7, "reference_type": "step"},
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
                make_run_result("pd", 0, 101, rmse=0.045, latency=0.0012),
                make_run_result("pd", 1, 202, rmse=0.042, latency=0.0011),
            ),
            "adaptive_pd": (
                make_run_result("adaptive_pd", 0, 101, rmse=0.031, latency=0.0015),
                make_run_result("adaptive_pd", 1, 202, rmse=0.029, latency=0.0015),
            ),
        },
    )

    comparison.validate()
    print(comparison)


if __name__ == "__main__":
    main()
