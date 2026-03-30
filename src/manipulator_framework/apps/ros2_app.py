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

    outputs = ros_runtime.spin(num_cycles=1)

    if outputs["robot_state"] is not None:
        print("[ros2_app] published robot_state")
    if outputs["camera_frame"] is not None:
        print("[ros2_app] published camera_frame")
    if outputs["person_detections"] is not None:
        print("[ros2_app] published person_detections")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
