from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from manipulator_framework.core.contracts import MarkerDetectorInterface
from manipulator_framework.core.types import CameraFrame, Detection2D, MarkerDetection


@dataclass
class ArucoOpenCVAdapter(MarkerDetectorInterface):
    """
    OpenCV ArUco detector adapter.

    This adapter keeps OpenCV-specific logic entirely in the boundary layer and
    converts detections into internal MarkerDetection objects.
    """
    dictionary_name: str
    detector_parameters: Any | None = None
    cv2_module: Any | None = None

    def detect_markers(self, frame: CameraFrame) -> list[MarkerDetection]:
        raw_detections = self._detect_raw(frame)
        return [
            self._to_marker_detection(
                corners=item["corners"],
                marker_id=item["marker_id"],
                timestamp=frame.timestamp,
                image_shape=frame.image.shape,
            )
            for item in raw_detections
        ]

    def _detect_raw(self, frame: CameraFrame) -> list[dict[str, Any]]:
        cv2 = self._resolve_cv2()
        aruco = self._resolve_aruco(cv2)

        dictionary_id = getattr(aruco, self.dictionary_name, None)
        if dictionary_id is None:
            raise ValueError(f"Unknown ArUco dictionary name: {self.dictionary_name}")

        dictionary = aruco.getPredefinedDictionary(dictionary_id)
        parameters = self.detector_parameters or aruco.DetectorParameters()

        detector = aruco.ArucoDetector(dictionary, parameters)
        image = self._prepare_image(cv2, frame.image)
        corners_list, ids, _ = detector.detectMarkers(image)

        if ids is None or len(ids) == 0:
            return []

        raw_detections: list[dict[str, Any]] = []
        for corners, marker_id in zip(corners_list, ids.flatten()):
            raw_detections.append(
                {
                    "corners": np.asarray(corners, dtype=float).reshape(-1, 2),
                    "marker_id": int(marker_id),
                }
            )
        return raw_detections

    def _to_marker_detection(
        self,
        *,
        corners: np.ndarray,
        marker_id: int,
        timestamp: float,
        image_shape: tuple[int, ...],
    ) -> MarkerDetection:
        corners_uv = tuple((float(x), float(y)) for x, y in corners)
        x_coords = [point[0] for point in corners_uv]
        y_coords = [point[1] for point in corners_uv]

        image_h = int(image_shape[0])
        image_w = int(image_shape[1])

        detection = Detection2D(
            bbox_xyxy=(
                float(min(x_coords)),
                float(min(y_coords)),
                float(max(x_coords)),
                float(max(y_coords)),
            ),
            confidence=1.0,
            class_id=marker_id,
            class_name="aruco_marker",
            image_size_wh=(image_w, image_h),
            timestamp=timestamp,
        )

        return MarkerDetection(
            marker_id=marker_id,
            detection=detection,
            pose_camera_frame=None,
            corners_uv=corners_uv,
            dictionary_name=self.dictionary_name,
            timestamp=timestamp,
        )

    def _prepare_image(self, cv2: Any, image: np.ndarray) -> np.ndarray:
        if image.ndim == 2:
            return image
        if image.ndim == 3 and image.shape[2] == 3:
            return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        raise ValueError("CameraFrame image must be grayscale or RGB for ArUco detection.")

    def _resolve_cv2(self) -> Any:
        if self.cv2_module is not None:
            return self.cv2_module

        try:
            import cv2  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "OpenCV is required for ArucoOpenCVAdapter. Install opencv-contrib-python."
            ) from exc

        return cv2

    def _resolve_aruco(self, cv2: Any) -> Any:
        aruco = getattr(cv2, "aruco", None)
        if aruco is None:
            raise ImportError(
                "cv2.aruco is required for ArucoOpenCVAdapter. "
                "Install opencv-contrib-python."
            )
        return aruco
