from __future__ import annotations

from manipulator_framework.application.composition.ros2_composer import ROS2Composer
from manipulator_framework.infrastructure.config.loader import YAMLConfigurationLoader


def main() -> int:
    """Run the ROS 2 app entrypoint."""
    loader = YAMLConfigurationLoader()
    raw_config = loader.load("configs/app/ros2.yaml")
    config = loader.resolve(raw_config)

    composer = ROS2Composer(config=config)
    ros_runtime = composer.build_ros2_runtime()

    ros_runtime.spin()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
