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

runtime:
  dt: 0.02
  max_steps: 10

logging:
  level: INFO
  save_to_file: true

results:
  base_dir: experiments/runs

experiment:
  name: test_experiment
  seed: 123
  tags: [unit, config]
""".strip(),
        encoding="utf-8",
    )

    loader = YAMLConfigurationLoader()
    raw_config = loader.load(str(config_file))

    assert raw_config["app"]["name"] == "test_app"
    assert raw_config["runtime"]["dt"] == 0.02
    assert raw_config["experiment"]["seed"] == 123
