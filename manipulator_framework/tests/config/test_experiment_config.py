import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from manipulator_framework.config.experiment_config import load_experiment_config


class TestExperimentConfigEnvOverride(unittest.TestCase):
    def test_env_override_applies_without_config_file(self) -> None:
        scene_path = Path("manipulator_framework/tests/config/env_scene.ttt")

        previous = os.environ.get("COPPELIA_SCENE_PATH")
        os.environ["COPPELIA_SCENE_PATH"] = str(scene_path)
        try:
            config = load_experiment_config("pick_and_place")
        finally:
            if previous is None:
                os.environ.pop("COPPELIA_SCENE_PATH", None)
            else:
                os.environ["COPPELIA_SCENE_PATH"] = previous

        assert config.coppelia.scene_path is not None
        self.assertEqual(
            Path(config.coppelia.scene_path).resolve(),
            scene_path.resolve(),
        )

    def test_env_override_has_precedence_over_json_scene_path(self) -> None:
        env_scene = Path("manipulator_framework/tests/config/env_scene.ttt")
        fake_config_path = "manipulator_framework/tests/config/fake_experiment.json"
        fake_json_payload = json.dumps({"coppelia": {"scene_path": "json_scene.ttt"}})

        previous = os.environ.get("COPPELIA_SCENE_PATH")
        os.environ["COPPELIA_SCENE_PATH"] = str(env_scene)
        try:
            with patch("pathlib.Path.read_text", return_value=fake_json_payload):
                config = load_experiment_config(
                    "pick_and_place",
                    config_path=fake_config_path,
                )
        finally:
            if previous is None:
                os.environ.pop("COPPELIA_SCENE_PATH", None)
            else:
                os.environ["COPPELIA_SCENE_PATH"] = previous

        assert config.coppelia.scene_path is not None
        self.assertEqual(
            Path(config.coppelia.scene_path).resolve(),
            env_scene.resolve(),
        )


if __name__ == "__main__":
    unittest.main()
