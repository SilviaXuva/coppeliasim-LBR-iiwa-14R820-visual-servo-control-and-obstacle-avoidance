from __future__ import annotations

from manipulator_framework.adapters.ros2.converters.to_ros_msgs import person_detection_to_ros_dict
from manipulator_framework.core.contracts.camera_interface import CameraInterface
from manipulator_framework.core.contracts.detector_interfaces import PersonDetectorInterface


class ROS2DetectionBridge:
    """
    Bridge between internal perception interfaces and ROS-facing transport payloads.
    """

    def __init__(
        self,
        camera: CameraInterface,
        person_detector: PersonDetectorInterface,
    ) -> None:
        self._camera = camera
        self._person_detector = person_detector

    def read_person_detection_messages(self) -> list[dict]:
        frame = self._camera.get_frame()
        detections = self._person_detector.detect_people(frame)
        return [person_detection_to_ros_dict(item) for item in detections]
