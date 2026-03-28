from __future__ import annotations

from unittest.mock import MagicMock, patch

from manipulator_framework.apps.ros2_app import main


@patch("manipulator_framework.apps.ros2_app.ROS2Composer")
@patch("manipulator_framework.apps.ros2_app.YAMLConfigurationLoader")
def test_ros2_app_integration_wires_loader_composer_and_runtime(
    loader_cls,
    composer_cls,
) -> None:
    loader = MagicMock()
    loader.load.return_value = {"path": "configs/app/ros2.yaml"}
    loader.resolve.return_value = {"resolved": True}
    loader_cls.return_value = loader

    runtime = MagicMock()
    composer = MagicMock()
    composer.build_ros2_runtime.return_value = runtime
    composer_cls.return_value = composer

    code = main()

    assert code == 0
    loader.load.assert_called_once_with("configs/app/ros2.yaml")
    loader.resolve.assert_called_once_with({"path": "configs/app/ros2.yaml"})
    composer_cls.assert_called_once_with(config={"resolved": True})
    runtime.spin.assert_called_once()
