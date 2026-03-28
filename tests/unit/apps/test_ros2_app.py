from __future__ import annotations

from unittest.mock import MagicMock, patch

from manipulator_framework.apps.ros2_app import main


@patch("manipulator_framework.apps.ros2_app.ROS2Composer")
@patch("manipulator_framework.apps.ros2_app.YAMLConfigurationLoader")
def test_ros2_app_builds_ros_runtime_and_spins(
    loader_cls,
    composer_cls,
) -> None:
    loader = MagicMock()
    loader.load.return_value = {}
    loader.resolve.return_value = {"app": {"name": "ros2"}}
    loader_cls.return_value = loader

    runtime = MagicMock()
    composer = MagicMock()
    composer.build_ros2_runtime.return_value = runtime
    composer_cls.return_value = composer

    exit_code = main()

    assert exit_code == 0
    composer.build_ros2_runtime.assert_called_once()
    runtime.spin.assert_called_once()
