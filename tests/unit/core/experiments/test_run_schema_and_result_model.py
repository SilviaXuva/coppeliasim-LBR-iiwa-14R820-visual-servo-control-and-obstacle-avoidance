from __future__ import annotations

from manipulator_framework.core.experiments import RunArtifact, RunResult
from manipulator_framework.core.metrics import MetricsSnapshot, ScalarMetric


def test_run_result_exposes_duration_and_metadata() -> None:
    metrics = MetricsSnapshot(
        scalar_metrics=(
            ScalarMetric(name="joint_position_rmse", value=0.02, unit="rad"),
        )
    )

    result = RunResult(
        run_id="run_001",
        success=True,
        num_cycles=5,
        summary={
            "experiment_name": "pd_vs_adaptive_pd",
            "scenario_name": "synthetic_joint_tracking",
            "backend_name": "mock_backend",
            "controller": "pd",
        },
        metrics=metrics,
        artifacts=(
            RunArtifact(name="summary", path="runs/run_001/summary.json", kind="json"),
        ),
        resolved_config={"dt": 0.01},
        seed=42,
        start_time=1.0,
        end_time=4.5,
    )

    assert result.duration == 3.5
    assert result.success is True
    assert result.seed == 42
    assert result.artifacts[0].name == "summary"
