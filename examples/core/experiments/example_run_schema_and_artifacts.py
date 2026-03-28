from __future__ import annotations

from manipulator_framework.core.experiments import RunArtifact, RunSchema


def main() -> None:
    run_schema = RunSchema(
        run_id="run_schema_demo",
        experiment_name="pbvs_with_avoidance",
        scenario_name="person_in_workspace",
        backend_name="simulation",
        seed=123,
        resolved_config={
            "controller": "adaptive_pd",
            "tracking": {"enabled": True},
            "avoidance": {"enabled": True},
        },
        tags=("benchmark", "demo"),
        notes="Logical run schema example.",
    )

    artifacts = (
        RunArtifact("config", "experiments/runs/run_schema_demo/config.yaml", "config"),
        RunArtifact("metrics", "experiments/runs/run_schema_demo/metrics.csv", "metrics"),
        RunArtifact("summary", "experiments/runs/run_schema_demo/summary.json", "summary"),
    )

    print(run_schema)
    print(artifacts)


if __name__ == "__main__":
    main()
