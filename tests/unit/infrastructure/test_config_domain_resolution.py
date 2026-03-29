from __future__ import annotations

from pathlib import Path

from manipulator_framework.infrastructure.config import ConfigurationPaths, YAMLConfigurationLoader


def test_loader_resolves_multi_domain_configuration(tmp_path: Path) -> None:
    app_file = tmp_path / "simulation.yaml"
    app_file.write_text(
        """
app:
  mode: simulation
  use_case: run_joint_trajectory

experiment:
  name: simulation_run
  seed: 42
  tags: [simulation]
  notes: "simulation"

scenario:
  name: synthetic_joint_trajectory
""".strip(),
        encoding="utf-8",
    )

    controller_file = tmp_path / "joint_pd.yaml"
    controller_file.write_text(
        """
controller:
  kind: joint_pd
  gains:
    kp: 15.0
    kd: 2.0
    ki: 0.0
""".strip(),
        encoding="utf-8",
    )

    visual_file = tmp_path / "pbvs.yaml"
    visual_file.write_text(
        """
visual_servoing:
  enabled: true
  kind: pbvs
  target_frame: aruco_target
  camera_frame: hand_camera
  gain: 0.75
""".strip(),
        encoding="utf-8",
    )

    perception_file = tmp_path / "aruco_yolo.yaml"
    perception_file.write_text(
        """
perception:
  person_detector:
    enabled: true
    backend: yolo
    model_name: yolo11n
    confidence_threshold: 0.6

  marker_detector:
    enabled: true
    backend: aruco
    dictionary: DICT_4X4_50
    marker_length_m: 0.05
""".strip(),
        encoding="utf-8",
    )

    avoidance_file = tmp_path / "cuckoo.yaml"
    avoidance_file.write_text(
        """
obstacle_avoidance:
  enabled: true
  kind: cuckoo_search
  weight: 2.0
  clearance_m: 0.25
  population_size: 12
  max_iterations: 30
""".strip(),
        encoding="utf-8",
    )

    experiment_file = tmp_path / "experiment.yaml"
    experiment_file.write_text(
        """
planning:
  duration: 2.5

results:
  base_dir: experiments/runs

runtime:
  dt: 0.02
  max_steps: 50
  save_runtime_series: true
""".strip(),
        encoding="utf-8",
    )

    loader = YAMLConfigurationLoader()
    config = loader.resolve_from_paths(
        ConfigurationPaths(
            app_config=app_file,
            controller_config=controller_file,
            visual_servoing_config=visual_file,
            perception_config=perception_file,
            obstacle_avoidance_config=avoidance_file,
            experiment_config=experiment_file,
        )
    )

    assert config["app"]["mode"] == "simulation"
    assert config["app"]["use_case"] == "run_joint_trajectory"
    assert config["controller"]["kind"] == "joint_pd"
    assert config["controller"]["gains"]["kp"] == 15.0
    assert config["visual_servoing"]["enabled"] is True
    assert config["perception"]["person_detector"]["backend"] == "yolo"
    assert config["obstacle_avoidance"]["enabled"] is True
    assert config["planning"]["duration"] == 2.5
    assert config["runtime"]["dt"] == 0.02
