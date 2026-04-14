import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from manipulator_framework.config.experiment_config import (
    CoppeliaConfig,
    PickAndPlaceConfig,
    default_experiment_config,
    load_experiment_config,
)


class TestExperimentConfigEnvOverride(unittest.TestCase):
    def test_public_constructors_keep_defaults(self) -> None:
        pick_cfg = PickAndPlaceConfig()
        coppelia_cfg = CoppeliaConfig()
        self.assertEqual(len(pick_cfg.tau_min), 7)
        self.assertEqual(len(pick_cfg.tau_max), 7)
        self.assertEqual(coppelia_cfg.host, "localhost")
        self.assertEqual(coppelia_cfg.port, 23000)

    def test_default_experiment_config_remains_available(self) -> None:
        config = default_experiment_config("pick_and_place_kin_pi")
        self.assertEqual(config.experiment, "pick_and_place_kin_pi")

    def test_supports_dynamic_pd_experiment_name(self) -> None:
        config = load_experiment_config("pick_and_place_dyn_pd")
        self.assertEqual(config.experiment, "pick_and_place_dyn_pd")
        self.assertEqual(len(config.pick_and_place.tau_min), 7)
        self.assertEqual(len(config.pick_and_place.tau_max), 7)

    def test_legacy_experiment_alias_maps_to_kin_pi(self) -> None:
        config = load_experiment_config("pick_and_place")
        self.assertEqual(config.experiment, "pick_and_place_kin_pi")

    def test_default_joint_gains_match_legacy_values(self) -> None:
        config = load_experiment_config("pick_and_place_kin_pi")
        self.assertEqual(
            config.pick_and_place.kp,
            (
                1.64725,
                1.40056,
                1.40056,
                1.33690,
                1.36873,
                1.40056,
                1.36873,
            ),
        )
        self.assertEqual(
            config.pick_and_place.ki,
            (
                1.23544,
                0.93371,
                0.93371,
                0.89127,
                0.91249,
                0.93371,
                0.91249,
            ),
        )

    def test_json_joint_gains_list_are_loaded_as_tuples(self) -> None:
        fake_config_path = "manipulator_framework/tests/config/fake_experiment.json"
        fake_json_payload = json.dumps(
            {
                "pick_and_place": {
                    "kp": [1.0, 2.0, 3.0],
                    "ki": [0.1, 0.2, 0.3],
                }
            }
        )
        with patch("pathlib.Path.read_text", return_value=fake_json_payload):
            config = load_experiment_config(
                "pick_and_place_kin_pi",
                config_path=fake_config_path,
            )

        self.assertEqual(config.pick_and_place.kp, (1.0, 2.0, 3.0))
        self.assertEqual(config.pick_and_place.ki, (0.1, 0.2, 0.3))

    def test_pick_and_place_place_and_offsets_loaded_from_json(self) -> None:
        fake_config_path = "manipulator_framework/tests/config/fake_experiment.json"
        fake_json_payload = json.dumps(
            {
                "pick_and_place": {
                    "place_pose": [0.4, -0.1, 0.3, 3.14, 0.0, 1.57],
                    "pre_grasp_offset": [0.0, 0.0, 0.12],
                    "lift_offset": [0.0, 0.0, 0.2],
                    "retreat_offset": [0.0, 0.0, 0.08],
                }
            }
        )
        with patch("pathlib.Path.read_text", return_value=fake_json_payload):
            config = load_experiment_config(
                "pick_and_place_kin_pi",
                config_path=fake_config_path,
            )

        self.assertEqual(
            config.pick_and_place.place_pose,
            (0.4, -0.1, 0.3, 3.14, 0.0, 1.57),
        )
        self.assertEqual(config.pick_and_place.pre_grasp_offset, (0.0, 0.0, 0.12))
        self.assertEqual(config.pick_and_place.lift_offset, (0.0, 0.0, 0.2))
        self.assertEqual(config.pick_and_place.retreat_offset, (0.0, 0.0, 0.08))

    def test_coppelia_gripper_and_object_paths_loaded_from_json(self) -> None:
        fake_config_path = "manipulator_framework/tests/config/fake_experiment.json"
        fake_json_payload = json.dumps(
            {
                "coppelia": {
                    "gripper_joints_paths": ["./active1", "./active2"],
                    "gripper_proximity_sensor_path": "./attachProxSensor",
                    "gripper_attach_path": "./attachPoint",
                    "grasp_object_path": "./red1",
                    "tracked_object_path": "./red1",
                }
            }
        )
        with patch("pathlib.Path.read_text", return_value=fake_json_payload):
            config = load_experiment_config(
                "pick_and_place_kin_pi",
                config_path=fake_config_path,
            )

        self.assertEqual(
            config.coppelia.gripper_joints_paths,
            ("./active1", "./active2"),
        )
        self.assertEqual(
            config.coppelia.gripper_proximity_sensor_path,
            "./attachProxSensor",
        )
        self.assertEqual(config.coppelia.gripper_attach_path, "./attachPoint")
        self.assertEqual(config.coppelia.grasp_object_path, "./red1")
        self.assertEqual(config.coppelia.tracked_object_path, "./red1")

    def test_camera_frame_rotation_matches_legacy_yaw_180(self) -> None:
        config = load_experiment_config("pick_and_place_kin_pi")
        self.assertEqual(
            config.coppelia.camera_frame_rotation,
            (
                (-1.0, 0.0, 0.0, 0.0),
                (0.0, -1.0, 0.0, 0.0),
                (0.0, 0.0, 1.0, 0.0),
                (0.0, 0.0, 0.0, 1.0),
            ),
        )

    def test_json_camera_frame_rotation_override_is_ignored(self) -> None:
        fake_config_path = "manipulator_framework/tests/config/fake_experiment.json"
        fake_json_payload = json.dumps(
            {
                "coppelia": {
                    "camera_frame_rotation": (
                        (1.0, 0.0, 0.0, 0.0),
                        (0.0, 1.0, 0.0, 0.0),
                        (0.0, 0.0, 1.0, 0.0),
                        (0.0, 0.0, 0.0, 1.0),
                    )
                }
            }
        )
        with patch("pathlib.Path.read_text", return_value=fake_json_payload):
            config = load_experiment_config(
                "pick_and_place_kin_pi",
                config_path=fake_config_path,
            )

        self.assertEqual(
            config.coppelia.camera_frame_rotation,
            (
                (-1.0, 0.0, 0.0, 0.0),
                (0.0, -1.0, 0.0, 0.0),
                (0.0, 0.0, 1.0, 0.0),
                (0.0, 0.0, 0.0, 1.0),
            ),
        )

    def test_env_override_applies_without_config_file(self) -> None:
        scene_path = Path("manipulator_framework/tests/config/env_scene.ttt")

        previous = os.environ.get("COPPELIA_SCENE_PATH")
        os.environ["COPPELIA_SCENE_PATH"] = str(scene_path)
        try:
            config = load_experiment_config("pick_and_place_kin_pi")
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
                    "pick_and_place_kin_pi",
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
