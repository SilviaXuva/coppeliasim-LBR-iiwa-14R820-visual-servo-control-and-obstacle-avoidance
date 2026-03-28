from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np

from .aliases import FrameName, Timestamp
from .geometry import Pose3D
from .mixins import SerializableMixin


@dataclass(frozen=True)
class CameraFrame(SerializableMixin):
    image: np.ndarray
    camera_id: str
    frame_id: FrameName = "camera"
    timestamp: Timestamp = 0.0
    intrinsics: np.ndarray | None = None
    extrinsics: Pose3D | None = None

    def __post_init__(self) -> None:
        image = np.asarray(self.image)
        if image.ndim not in (2, 3):
            raise ValueError("image must be 2D or 3D numpy array.")
        object.__setattr__(self, "image", image)

        if self.intrinsics is not None:
            intrinsics = np.asarray(self.intrinsics, dtype=float)
            if intrinsics.shape != (3, 3):
                raise ValueError("intrinsics must have shape (3, 3).")
            object.__setattr__(self, "intrinsics", intrinsics)


@dataclass(frozen=True)
class Detection2D(SerializableMixin):
    bbox_xyxy: tuple[float, float, float, float]
    confidence: float
    class_id: int | None = None
    class_name: str | None = None
    image_size_wh: tuple[int, int] | None = None
    timestamp: Timestamp = 0.0

    def __post_init__(self) -> None:
        x1, y1, x2, y2 = self.bbox_xyxy
        if x2 < x1 or y2 < y1:
            raise ValueError("bbox_xyxy must satisfy x2 >= x1 and y2 >= y1.")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence must be in [0, 1].")


@dataclass(frozen=True)
class MarkerDetection(SerializableMixin):
    marker_id: int
    detection: Detection2D
    pose_camera_frame: Pose3D | None = None
    corners_uv: tuple[tuple[float, float], ...] = field(default_factory=tuple)
    dictionary_name: str | None = None
    timestamp: Timestamp = 0.0


@dataclass(frozen=True)
class PersonDetection(SerializableMixin):
    detection: Detection2D
    keypoints_uv: tuple[tuple[float, float], ...] = field(default_factory=tuple)
    person_id_hint: str | None = None
    timestamp: Timestamp = 0.0
