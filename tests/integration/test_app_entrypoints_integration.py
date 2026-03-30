from __future__ import annotations

from pathlib import Path

from manipulator_framework.apps.benchmark_app import main as benchmark_main
from manipulator_framework.apps.experiment_app import main as experiment_main
from manipulator_framework.apps.simulation_app import main as simulation_main
from manipulator_framework.core.types import PersonDetection


class _FakeConnectedSimClient:
    def __init__(self) -> None:
        self._joint_values = {f"LBR_iiwa_14_R820_joint{i}": 0.0 for i in range(1, 8)}
        self._sim_time = 0.0

    def start_simulation(self) -> None:
        return None

    def step_simulation(self) -> None:
        self._sim_time += 0.05

    def stop_simulation(self) -> None:
        return None

    def get_joint_position(self, *, robot_handle, joint_name: str) -> float:
        return float(self._joint_values.get(joint_name, 0.0))

    def get_joint_velocity(self, *, robot_handle, joint_name: str) -> float:
        return 0.0

    def set_joint_target_position(self, *, robot_handle, joint_name: str, value: float) -> None:
        self._joint_values[joint_name] = float(value)

    def set_joint_torque(self, *, robot_handle, joint_name: str, value: float) -> None:
        return None

    def get_object_position(self, *, handle, reference_frame: str = "world") -> list[float]:
        return [0.5, 0.0, 0.6]

    def get_object_quaternion(self, *, handle, reference_frame: str = "world") -> list[float]:
        return [0.0, 0.0, 0.0, 1.0]

    def get_sim_time(self) -> float:
        return self._sim_time

    def get_camera_rgb(self, *, camera_handle) -> list[list[list[int]]]:
        return [[[0, 0, 0] for _ in range(32)] for _ in range(32)]

    def get_camera_intrinsics(self, *, camera_handle) -> list[list[float]]:
        return [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]


class _NoOpPersonDetector:
    def detect_people(self, frame) -> list[PersonDetection]:
        return []


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
    monkeypatch.setattr(
        "manipulator_framework.apps.simulation_app.CoppeliaSimClient.connect",
        lambda cfg: _FakeConnectedSimClient(),
    )
    monkeypatch.setattr(
        "manipulator_framework.apps.experiment_app.CoppeliaSimClient.connect",
        lambda cfg: _FakeConnectedSimClient(),
    )
    monkeypatch.setattr(
        "manipulator_framework.application.composition.simulation_composer.SimulationComposer.build_person_detector",
        lambda self: _NoOpPersonDetector(),
    )

    assert simulation_main("configs/app/simulation.yaml") == 0
    assert experiment_main() == 0
    assert benchmark_main() == 0

    run_dirs = sorted(path.name for path in results_dir.iterdir() if path.is_dir())

    assert "simulation_case_experiment_seed_11" in run_dirs
    assert "experiment_case_experiment_seed_11" in run_dirs
    assert "benchmark_case_joint_pd_rep_1_seed_11" not in run_dirs
    assert "benchmark_case_joint_pd_rep_1_seed_101" in run_dirs
    assert "benchmark_case_joint_pd_rep_2_seed_102" in run_dirs
    assert "benchmark_case_adaptive_joint_pd_rep_1_seed_101" in run_dirs
    assert "benchmark_case_adaptive_joint_pd_rep_2_seed_102" in run_dirs

    for run_dir in results_dir.iterdir():
        if run_dir.is_dir():
            assert any(item.suffix == ".json" for item in run_dir.iterdir())
