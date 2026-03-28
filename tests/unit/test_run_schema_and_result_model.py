from __future__ import annotations

from manipulator_framework.core.experiments import RunArtifact, RunResult, RunSchema
from manipulator_framework.core.metrics import MetricsSnapshot, ScalarMetric


def test_run_result_exposes_duration_and_metadata() -> None:
    run_schema = RunSchema(
        run_id="run_001",
        experiment_name="pd_vs_adaptive_pd",
        scenario_name="synthetic_joint_tracking",
        backend_name="mock_backend",
        seed=42,
        resolved_config={"dt": 0.01},
        tags=("benchmark",),
    )

    metrics = MetricsSnapshot(
        scalar_metrics=(
            ScalarMetric(name="joint_position_rmse", value=0.02, unit="rad"),
        )
    )

    result = RunResult(
        run_schema=run_schema,
        metrics=metrics,
        artifacts=(
            RunArtifact(name="summary", path="runs/run_001/summary.json", kind="json"),
        ),
        success=True,
        started_at=1.0,
        finished_at=4.5,
        metadata={"controller": "pd"},
    )

    assert result.duration == 3.5
    assert result.success is True
    assert result.run_schema.seed == 42
    assert result.artifacts[0].name == "summary"
