from __future__ import annotations

from collections.abc import Sequence
import math

from ....core.models.pose import Pose
from ....core.ports.drawing_port import DrawingPort


class CoppeliaDrawingAdapter(DrawingPort):
    """
    Drawing adapter backed by CoppeliaSim Remote API.

    Encapsulates drawing object creation, item insertion, and cleanup.
    """

    def __init__(
        self,
        sim: object,
        *,
        max_items: int = 5000,
        frame_axis_length_m: float = 0.05,
    ) -> None:
        self._sim = sim
        self._max_items = int(max_items)
        self._frame_axis_length_m = float(frame_axis_length_m)
        self._handles: dict[str, int] = {}

    def draw_point(self, position: Sequence[float]) -> None:
        x, y, z = self._xyz(position)
        handle = self._ensure_handle(
            key="point",
            draw_type=self._drawing_point_type(),
            size=6.0,
            color=(1.0, 1.0, 0.0),
        )
        self._sim.addDrawingObjectItem(handle, [x, y, z])

    def draw_line(self, start: Sequence[float], end: Sequence[float]) -> None:
        x0, y0, z0 = self._xyz(start)
        x1, y1, z1 = self._xyz(end)
        handle = self._ensure_handle(
            key="line",
            draw_type=self._drawing_line_type(),
            size=2.0,
            color=(0.0, 1.0, 1.0),
        )
        self._sim.addDrawingObjectItem(handle, [x0, y0, z0, x1, y1, z1])

    def draw_path(self, points: Sequence[Sequence[float]]) -> None:
        if len(points) < 2:
            return
        handle = self._ensure_handle(
            key="path",
            draw_type=self._drawing_line_type(),
            size=2.0,
            color=(1.0, 0.5, 0.0),
        )
        previous = self._xyz(points[0])
        for point in points[1:]:
            current = self._xyz(point)
            self._sim.addDrawingObjectItem(
                handle,
                [
                    previous[0],
                    previous[1],
                    previous[2],
                    current[0],
                    current[1],
                    current[2],
                ],
            )
            previous = current

    def draw_frame(self, pose: Pose) -> None:
        origin = (float(pose.x), float(pose.y), float(pose.z))
        rotation = self._rotation_matrix_from_rpy(
            roll=float(pose.roll),
            pitch=float(pose.pitch),
            yaw=float(pose.yaw),
        )
        axis_length = self._frame_axis_length_m

        x_axis = self._transform_axis(
            origin=origin,
            rotation=rotation,
            axis=(axis_length, 0.0, 0.0),
        )
        y_axis = self._transform_axis(
            origin=origin,
            rotation=rotation,
            axis=(0.0, axis_length, 0.0),
        )
        z_axis = self._transform_axis(
            origin=origin,
            rotation=rotation,
            axis=(0.0, 0.0, axis_length),
        )

        handle_x = self._ensure_handle(
            key="frame_x",
            draw_type=self._drawing_line_type(),
            size=2.0,
            color=(1.0, 0.0, 0.0),
        )
        handle_y = self._ensure_handle(
            key="frame_y",
            draw_type=self._drawing_line_type(),
            size=2.0,
            color=(0.0, 1.0, 0.0),
        )
        handle_z = self._ensure_handle(
            key="frame_z",
            draw_type=self._drawing_line_type(),
            size=2.0,
            color=(0.0, 0.0, 1.0),
        )

        self._sim.addDrawingObjectItem(handle_x, [*origin, *x_axis])
        self._sim.addDrawingObjectItem(handle_y, [*origin, *y_axis])
        self._sim.addDrawingObjectItem(handle_z, [*origin, *z_axis])

    def clear(self) -> None:
        for handle in self._handles.values():
            try:
                self._sim.addDrawingObjectItem(handle, None)
            except Exception:
                pass
            try:
                self._sim.removeDrawingObject(handle)
            except Exception:
                try:
                    self._sim.removeDrawingObject(handle, None)
                except Exception:
                    pass
        self._handles.clear()

    def _ensure_handle(
        self,
        *,
        key: str,
        draw_type: int,
        size: float,
        color: Sequence[float],
    ) -> int:
        existing = self._handles.get(key)
        if existing is not None:
            return existing
        handle = int(
            self._sim.addDrawingObject(
                int(draw_type),
                float(size),
                0.0,
                -1,
                self._max_items,
                list(float(value) for value in color),
            )
        )
        self._handles[key] = handle
        return handle

    def _drawing_line_type(self) -> int:
        return int(
            getattr(self._sim, "drawing_lines", 0)
            | getattr(self._sim, "drawing_cyclic", 0)
        )

    def _drawing_point_type(self) -> int:
        point_flag = getattr(self._sim, "drawing_spherepoints", None)
        if point_flag is None:
            point_flag = getattr(self._sim, "drawing_points", None)
        if point_flag is None:
            point_flag = getattr(self._sim, "drawing_lines", 0)
        return int(point_flag | getattr(self._sim, "drawing_cyclic", 0))

    @staticmethod
    def _xyz(values: Sequence[float]) -> tuple[float, float, float]:
        if len(values) < 3:
            raise ValueError("Expected at least 3 coordinates (x, y, z).")
        return (float(values[0]), float(values[1]), float(values[2]))

    @staticmethod
    def _rotation_matrix_from_rpy(
        *,
        roll: float,
        pitch: float,
        yaw: float,
    ) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]:
        sr = math.sin(roll)
        cr = math.cos(roll)
        sp = math.sin(pitch)
        cp = math.cos(pitch)
        sy = math.sin(yaw)
        cy = math.cos(yaw)

        return (
            (cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr),
            (sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr),
            (-sp, cp * sr, cp * cr),
        )

    @staticmethod
    def _transform_axis(
        *,
        origin: tuple[float, float, float],
        rotation: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]],
        axis: tuple[float, float, float],
    ) -> tuple[float, float, float]:
        x = (
            rotation[0][0] * axis[0]
            + rotation[0][1] * axis[1]
            + rotation[0][2] * axis[2]
        )
        y = (
            rotation[1][0] * axis[0]
            + rotation[1][1] * axis[1]
            + rotation[1][2] * axis[2]
        )
        z = (
            rotation[2][0] * axis[0]
            + rotation[2][1] * axis[1]
            + rotation[2][2] * axis[2]
        )
        return (origin[0] + x, origin[1] + y, origin[2] + z)
