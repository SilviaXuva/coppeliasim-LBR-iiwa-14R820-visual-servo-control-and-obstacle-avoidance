from __future__ import annotations

from manipulator_framework.adapters.vision.aruco.aruco_opencv_adapter import ArucoOpenCVAdapter
from manipulator_framework.core.contracts import MarkerDetectorInterface


def test_aruco_adapter_implements_marker_detector_interface() -> None:
    adapter = ArucoOpenCVAdapter(dictionary_name="DICT_4X4_50")
    assert isinstance(adapter, MarkerDetectorInterface)
