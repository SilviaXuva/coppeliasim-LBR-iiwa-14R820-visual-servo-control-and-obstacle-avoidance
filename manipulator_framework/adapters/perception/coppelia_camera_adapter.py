from __future__ import annotations

from collections.abc import Sequence

import cv2
import numpy as np

from ...core.ports.camera_port import CameraPort, Matrix3x3, Matrix4x4


class CoppeliaCameraAdapter(CameraPort):
    """Implements CameraPort for a CoppeliaSim vision sensor."""

    def __init__(
        self,
        sim: object,
        sensor_path: str,
        distortion_coefficients: Sequence[float] = (),
        frame_rotation: Sequence[Sequence[float]] | None = None,
    ) -> None:
        self._sim = sim
        self._sensor_handle = self._sim.getObject(sensor_path)
        self._distortion_coefficients = tuple(
            float(value) for value in distortion_coefficients
        )
        if frame_rotation is None:
            self._frame_rotation = np.eye(4, dtype=float)
        else:
            self._frame_rotation = np.asarray(frame_rotation, dtype=float)

        self._intrinsic_matrix_np = self._compute_intrinsic_matrix()
        self._extrinsic_matrix_np = self._compute_extrinsic_matrix()

    def capture_frame(self) -> object:
        frame_bytes, res_x, res_y = self._sim.getVisionSensorCharImage(
            self._sensor_handle
        )
        frame = np.frombuffer(frame_bytes, dtype=np.uint8).reshape(res_y, res_x, 3)
        frame = cv2.flip(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), 0)
        return frame

    def get_intrinsic_matrix(self) -> Matrix3x3:
        return self._matrix3_to_tuple(self._intrinsic_matrix_np)

    def get_distortion_coefficients(self) -> tuple[float, ...]:
        return self._distortion_coefficients

    def get_extrinsic_matrix(self) -> Matrix4x4:
        self._extrinsic_matrix_np = self._compute_extrinsic_matrix()
        return self._matrix4_to_tuple(self._extrinsic_matrix_np)

    def _compute_intrinsic_matrix(self) -> np.ndarray:
        res_x, res_y = self._sim.getVisionSensorRes(self._sensor_handle)
        perspective_angle = float(
            self._sim.getObjectFloatParam(
                self._sensor_handle,
                self._sim.visionfloatparam_perspective_angle,
            )
        )
        c_x = res_x / 2.0
        c_y = res_y / 2.0
        f_x = c_x / np.tan(perspective_angle / 2.0)
        f_y = c_y / np.tan(perspective_angle / 2.0)
        return np.array(
            [
                [f_x, 0.0, c_x],
                [0.0, f_y, c_y],
                [0.0, 0.0, 1.0],
            ],
            dtype=float,
        )

    def _compute_extrinsic_matrix(self) -> np.ndarray:
        position = self._sim.getObjectPosition(self._sensor_handle, self._sim.handle_world)
        alpha_beta_gamma = self._sim.getObjectOrientation(
            self._sensor_handle, self._sim.handle_world
        )
        yaw, pitch, roll = self._sim.alphaBetaGammaToYawPitchRoll(
            alpha_beta_gamma[0],
            alpha_beta_gamma[1],
            alpha_beta_gamma[2],
        )
        rotation = self._rotation_matrix_zyx(yaw=yaw, pitch=pitch, roll=roll)

        extrinsic = np.eye(4, dtype=float)
        extrinsic[:3, :3] = rotation
        extrinsic[:3, 3] = np.asarray(position, dtype=float)
        return extrinsic @ self._frame_rotation

    @staticmethod
    def _rotation_matrix_zyx(yaw: float, pitch: float, roll: float) -> np.ndarray:
        c_yaw = np.cos(yaw)
        s_yaw = np.sin(yaw)
        c_pitch = np.cos(pitch)
        s_pitch = np.sin(pitch)
        c_roll = np.cos(roll)
        s_roll = np.sin(roll)

        r_z = np.array(
            [[c_yaw, -s_yaw, 0.0], [s_yaw, c_yaw, 0.0], [0.0, 0.0, 1.0]],
            dtype=float,
        )
        r_y = np.array(
            [[c_pitch, 0.0, s_pitch], [0.0, 1.0, 0.0], [-s_pitch, 0.0, c_pitch]],
            dtype=float,
        )
        r_x = np.array(
            [[1.0, 0.0, 0.0], [0.0, c_roll, -s_roll], [0.0, s_roll, c_roll]],
            dtype=float,
        )
        return r_z @ r_y @ r_x

    @staticmethod
    def _matrix3_to_tuple(matrix: np.ndarray) -> Matrix3x3:
        return (
            (float(matrix[0, 0]), float(matrix[0, 1]), float(matrix[0, 2])),
            (float(matrix[1, 0]), float(matrix[1, 1]), float(matrix[1, 2])),
            (float(matrix[2, 0]), float(matrix[2, 1]), float(matrix[2, 2])),
        )

    @staticmethod
    def _matrix4_to_tuple(matrix: np.ndarray) -> Matrix4x4:
        return (
            (
                float(matrix[0, 0]),
                float(matrix[0, 1]),
                float(matrix[0, 2]),
                float(matrix[0, 3]),
            ),
            (
                float(matrix[1, 0]),
                float(matrix[1, 1]),
                float(matrix[1, 2]),
                float(matrix[1, 3]),
            ),
            (
                float(matrix[2, 0]),
                float(matrix[2, 1]),
                float(matrix[2, 2]),
                float(matrix[2, 3]),
            ),
            (
                float(matrix[3, 0]),
                float(matrix[3, 1]),
                float(matrix[3, 2]),
                float(matrix[3, 3]),
            ),
        )
