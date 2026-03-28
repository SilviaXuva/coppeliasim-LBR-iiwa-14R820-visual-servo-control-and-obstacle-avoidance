from __future__ import annotations

from manipulator_framework.core.experiments import RunArtifact, RunResult, RunSchema
from manipulator_framework.core.metrics import MetricsSnapshot, ScalarMetric


def main() -> None:
    run_schema = RunSchema(
        run_id="run_0001",
        experiment_name="minimal_example",
        scenario_name="synthetic_joint_tracking",
        backend_name="mock_backend",
        seed=42,
        resolved_config={"controller": "pd", "dt": 0.01},
        tags=("example",),
    )

    metrics = MetricsSnapshot(
        scalar_metrics=(
            ScalarMetric("joint_position_rmse", 0.021, "rad"),
            ScalarMetric("success_rate", 1.0, "ratio"),
        ),
    )

    result = RunResult(
        run_schema=run_schema,
        metrics=metrics,
        artifacts=(
            RunArtifact(name="summary", path="experiments/runs/run_0001/summary.json", kind="json"),
        ),
        success=True,
        started_at=0.0,
        finished_at=12.5,
        metadata={"note": "minimal logical example"},
    )

    print(result)
    print("Duration:", result.duration)


if __name__ == "__main__":
    main()
