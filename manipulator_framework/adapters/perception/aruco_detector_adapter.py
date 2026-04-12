from __future__ import annotations

from collections.abc import Sequence
from time import time

import cv2
import numpy as np

from ...core.models.marker_state import MarkerState
from ...core.models.person_state import PersonState
from ...core.models.pose import Pose
from ...core.ports.camera_port import CameraPort
from ...core.ports.perception_port import PerceptionPort


class ArucoDetectorAdapter(PerceptionPort):
    """Implements PerceptionPort using OpenCV ArUco."""

    def __init__(
        self,
        camera: CameraPort,
        marker_length_m: float,
        dictionary_name: str = "DICT_6X6_250",
    ) -> None:
        self._camera = camera
        self._marker_length_m = float(marker_length_m)

        aruco = cv2.aruco
        dictionary_id = getattr(aruco, dictionary_name)
        dictionary = aruco.getPredefinedDictionary(dictionary_id)

        if hasattr(aruco, "ArucoDetector"):
            self._detector = aruco.ArucoDetector(dictionary, aruco.DetectorParameters())
            self._detector_parameters = None
            self._dictionary = None
        else:
            self._detector = None
            self._detector_parameters = aruco.DetectorParameters_create()
            self._dictionary = dictionary

    def detect_markers(self, frame: object) -> Sequence[MarkerState]:
        frame_np = np.asarray(frame)
        if frame_np.ndim == 3:
            gray_frame = cv2.cvtColor(frame_np, cv2.COLOR_RGB2GRAY)
        else:
            gray_frame = frame_np

        corners, ids = self._detect(gray_frame)
        if ids is None or len(ids) == 0:
            return ()

        intrinsic = np.asarray(self._camera.get_intrinsic_matrix(), dtype=float)
        distortion = np.asarray(self._camera.get_distortion_coefficients(), dtype=float)
        extrinsic = np.asarray(self._camera.get_extrinsic_matrix(), dtype=float)

        markers: list[MarkerState] = []
        for marker_corners, marker_id in zip(corners, ids.flatten()):
            marker_state = MarkerState(
                marker_id=int(marker_id),
                corners_uv=self._corners_to_tuple(marker_corners),
                confidence=1.0,
                timestamp_s=time(),
            )

            pose_camera_matrix = self._estimate_pose_camera_matrix(
                marker_corners,
                intrinsic,
                distortion,
            )
            if pose_camera_matrix is not None:
                marker_state.pose_camera = self._matrix_to_pose(pose_camera_matrix)
                marker_state.pose_world = self._matrix_to_pose(extrinsic @ pose_camera_matrix)

            markers.append(marker_state)

        return tuple(markers)

    def detect_people(self, frame: object) -> Sequence[PersonState]:
        del frame
        return ()

    def detect_from_camera(self) -> Sequence[MarkerState]:
        return self.detect_markers(self._camera.capture_frame())

    def _detect(self, gray_frame: np.ndarray) -> tuple[list[np.ndarray], np.ndarray | None]:
        if self._detector is not None:
            corners, ids, _rejected = self._detector.detectMarkers(gray_frame)
            return corners, ids
        corners, ids, _rejected = cv2.aruco.detectMarkers(
            gray_frame,
            self._dictionary,
            parameters=self._detector_parameters,
        )
        return corners, ids

    def _estimate_pose_camera_matrix(
        self,
        marker_corners: np.ndarray,
        intrinsic: np.ndarray,
        distortion: np.ndarray,
    ) -> np.ndarray | None:
        if self._marker_length_m <= 0.0:
            return None
        try:
            rvecs, tvecs, _obj_points = cv2.aruco.estimatePoseSingleMarkers(
                marker_corners,
                self._marker_length_m,
                intrinsic,
                distortion,
            )
            rvec = rvecs[0][0]
            tvec = tvecs[0][0]
        except Exception:
            return None

        rotation, _ = cv2.Rodrigues(rvec)
        transform = np.eye(4, dtype=float)
        transform[:3, :3] = rotation
        transform[:3, 3] = tvec
        return transform

    @staticmethod
    def _corners_to_tuple(marker_corners: np.ndarray) -> tuple[tuple[float, float], ...]:
        points = np.asarray(marker_corners, dtype=float).reshape(-1, 2)
        return tuple((float(point[0]), float(point[1])) for point in points)

    @staticmethod
    def _matrix_to_pose(matrix: np.ndarray) -> Pose:
        rotation = matrix[:3, :3]
        translation = matrix[:3, 3]

        # ZYX decomposition: R = Rz(yaw) * Ry(pitch) * Rx(roll)
        if abs(rotation[2, 0]) < 1.0:
            pitch = float(-np.arcsin(rotation[2, 0]))
            roll = float(np.arctan2(rotation[2, 1], rotation[2, 2]))
            yaw = float(np.arctan2(rotation[1, 0], rotation[0, 0]))
        else:
            pitch = float(np.pi / 2.0 if rotation[2, 0] <= -1.0 else -np.pi / 2.0)
            roll = float(np.arctan2(-rotation[0, 1], rotation[1, 1]))
            yaw = 0.0

        return Pose(
            x=float(translation[0]),
            y=float(translation[1]),
            z=float(translation[2]),
            roll=roll,
            pitch=pitch,
            yaw=yaw,
        )
