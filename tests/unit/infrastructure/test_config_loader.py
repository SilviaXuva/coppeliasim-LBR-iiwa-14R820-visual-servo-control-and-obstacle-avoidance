from __future__ import annotations

from pathlib import Path

from manipulator_framework.infrastructure.config.loader import YAMLConfigurationLoader


def test_config_loader_loads_yaml_file(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
app:
  name: test_app
  mode: simulation
  use_case: run_joint_trajectory

runtime:
  dt: 0.02
  max_steps: 10
  save_runtime_series: true

logging:
  level: INFO
  save_to_file: true

results:
  base_dir: experiments/runs

experiment:
  name: test_experiment
  seed: 123
  tags: [unit, config]
  notes: "loader test"

scenario:
  name: synthetic_joint_trajectory

controller:
  kind: joint_pd
  gains:
    kp: 10.0
    kd: 1.0
    ki: 0.0
  limits:
    max_velocity: 1.0
    max_acceleration: 2.0

planning:
  kind: quintic_joint_trajectory
  duration: 1.0

visual_servoing:
  enabled: false
  kind: pbvs
  target_frame: aruco_target
  camera_frame: camera
  gain: 0.8

perception:
  person_detector:
    enabled: false
    backend: yolo
    model_name: yolo11n
    confidence_threshold: 0.5
  marker_detector:
    enabled: false
    backend: aruco
    dictionary: DICT_4X4_50
    marker_length_m: 0.05

obstacle_avoidance:
  enabled: false
  kind: cuckoo_search
  weight: 1.0
  clearance_m: 0.20
  population_size: 10
  max_iterations: 15
""".strip(),
        encoding="utf-8",
    )

    loader = YAMLConfigurationLoader()
    raw_config = loader.load(str(config_file))

    assert raw_config["app"]["name"] == "test_app"
    assert raw_config["app"]["use_case"] == "run_joint_trajectory"
    assert raw_config["runtime"]["dt"] == 0.02
    assert raw_config["experiment"]["seed"] == 123
