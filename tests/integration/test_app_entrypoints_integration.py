from __future__ import annotations

from pathlib import Path

from manipulator_framework.apps.benchmark_app import main as benchmark_main
from manipulator_framework.apps.experiment_app import main as experiment_main
from manipulator_framework.apps.simulation_app import main as simulation_main


def _write_app_config(
    path: Path,
    *,
    mode: str,
    experiment_name: str,
    use_case: str,
    base_dir: str,
    benchmark_block: str = "",
) -> None:
    path.write_text(
        f"""
app:
  name: manipulator_framework
  mode: {mode}
  use_case: {use_case}

runtime:
  dt: 0.05
  max_steps: 5

logging:
  level: INFO
  save_to_file: false

results:
  base_dir: {base_dir}

experiment:
  name: {experiment_name}
  seed: 11
  tags: []

planning:
  duration: 1.0

{benchmark_block}
""".strip(),
        encoding="utf-8",
    )


def test_simulation_experiment_and_benchmark_apps_execute_real_flow(
    tmp_path: Path,
    monkeypatch,
) -> None:
    project_root = tmp_path
    configs_dir = project_root / "configs" / "app"
    results_dir = project_root / "experiments" / "runs"

    configs_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    _write_app_config(
        configs_dir / "simulation.yaml",
        mode="simulation",
        experiment_name="simulation_case",
        use_case="run_joint_trajectory",
        base_dir="experiments/runs",
    )
    _write_app_config(
        configs_dir / "experiment.yaml",
        mode="experiment",
        experiment_name="experiment_case",
        use_case="run_pbvs_with_avoidance",
        base_dir="experiments/runs",
    )
    _write_app_config(
        configs_dir / "benchmark.yaml",
        mode="benchmark",
        experiment_name="benchmark_case",
        use_case="benchmark_controllers",
        base_dir="experiments/runs",
        benchmark_block="""
benchmark:
  compared_methods: [joint_pd, adaptive_joint_pd]
  repetitions: 2
  seeds: [101, 102]
""".strip(),
    )

    monkeypatch.chdir(project_root)

    assert simulation_main() == 0
    assert experiment_main() == 0
    assert benchmark_main() == 0

    run_dirs = sorted(path.name for path in results_dir.iterdir() if path.is_dir())

    assert "simulation_case_simulation_seed_11" in run_dirs
    assert "experiment_case_experiment_seed_11" in run_dirs
    assert "benchmark_case_joint_pd_rep_1_seed_11" not in run_dirs
    assert "benchmark_case_joint_pd_rep_1_seed_101" in run_dirs
    assert "benchmark_case_joint_pd_rep_2_seed_102" in run_dirs
    assert "benchmark_case_adaptive_joint_pd_rep_1_seed_101" in run_dirs
    assert "benchmark_case_adaptive_joint_pd_rep_2_seed_102" in run_dirs

    for run_dir in results_dir.iterdir():
        if run_dir.is_dir():
            assert any(item.suffix == ".json" for item in run_dir.iterdir())
