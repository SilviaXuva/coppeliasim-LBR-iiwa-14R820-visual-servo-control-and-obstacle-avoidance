from __future__ import annotations

import numpy as np

from manipulator_framework.adapters.vision.aruco.aruco_opencv_adapter import (
    ArucoOpenCVAdapter,
)
from manipulator_framework.core.types import CameraFrame


class FakeArucoModule:
    DICT_4X4_50 = 100

    @staticmethod
    def getPredefinedDictionary(dictionary_id: int):
        return {"dictionary_id": dictionary_id}

    @staticmethod
    def DetectorParameters():
        return {"kind": "params"}

    class ArucoDetector:
        def __init__(self, dictionary, params) -> None:
            self.dictionary = dictionary
            self.params = params

        def detectMarkers(self, image):
            corners = [
                np.array(
                    [[[10.0, 20.0], [30.0, 20.0], [30.0, 40.0], [10.0, 40.0]]],
                    dtype=float,
                )
            ]
            ids = np.array([[7]], dtype=int)
            rejected = []
            return corners, ids, rejected


class FakeCV2:
    aruco = FakeArucoModule()

    @staticmethod
    def cvtColor(image, code):
        return image.mean(axis=2).astype(np.uint8)

    COLOR_RGB2GRAY = 1


def test_aruco_adapter_detects_marker_and_converts_to_internal_type() -> None:
    adapter = ArucoOpenCVAdapter(
        dictionary_name="DICT_4X4_50",
        cv2_module=FakeCV2(),
    )

    frame = CameraFrame(
        image=np.zeros((60, 80, 3), dtype=np.uint8),
        camera_id="cam_01",
        frame_id="camera",
        timestamp=1.5,
    )

    detections = adapter.detect_markers(frame)

    assert len(detections) == 1
    detection = detections[0]
    assert detection.marker_id == 7
    assert detection.timestamp == 1.5
    assert detection.detection.class_name == "aruco_marker"
    assert detection.detection.class_id == 7
    assert detection.detection.image_size_wh == (80, 60)
    assert detection.detection.bbox_xyxy == (10.0, 20.0, 30.0, 40.0)
    assert len(detection.corners_uv) == 4
