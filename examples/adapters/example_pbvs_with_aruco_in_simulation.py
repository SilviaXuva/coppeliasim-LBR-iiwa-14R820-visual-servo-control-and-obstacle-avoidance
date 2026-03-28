from __future__ import annotations

import numpy as np

from manipulator_framework.adapters.vision.aruco.aruco_opencv_adapter import ArucoOpenCVAdapter
from manipulator_framework.adapters.vision.aruco.opencv_pose_estimator_adapter import OpenCVPoseEstimatorAdapter
from manipulator_framework.core.types import CameraFrame


class FakeArucoAdapter(ArucoOpenCVAdapter):
    def _detect_raw(self, frame: CameraFrame):
        return [{"id": 7, "corners": [[10, 10], [30, 10], [30, 30], [10, 30]]}]

    def _to_marker_detection(self, raw_item, timestamp: float):
        from manipulator_framework.core.types import MarkerDetection

        return MarkerDetection(
            marker_id=int(raw_item["id"]),
            corners_px=tuple(tuple(float(v) for v in corner) for corner in raw_item["corners"]),
            confidence=1.0,
            frame_id="sim_camera",
            timestamp=timestamp,
        )


class FakePoseEstimator(OpenCVPoseEstimatorAdapter):
    def _estimate_raw_pose(self, observation):
        return np.zeros((3, 1)), np.array([[0.1], [0.0], [0.5]])

    def _rvec_to_quaternion(self, rvec: np.ndarray) -> np.ndarray:
        return np.array([0.0, 0.0, 0.0, 1.0], dtype=float)


def main() -> None:
    frame = CameraFrame(
        color=np.zeros((64, 64, 3), dtype=np.uint8),
        depth=None,
        intrinsics={},
        extrinsics=None,
        frame_id="sim_camera",
        timestamp=0.0,
    )

    detector = FakeArucoAdapter(dictionary_name="DICT_4X4_50")
    estimator = FakePoseEstimator(
        camera_matrix=np.eye(3),
        distortion_coeffs=np.zeros((5,)),
        marker_length_m=0.05,
    )

    detections = detector.detect(frame)
    pose = estimator.estimate_pose(detections[0])

    print("Marker detections:", detections)
    print("Estimated pose:", pose)


if __name__ == "__main__":
    main()
