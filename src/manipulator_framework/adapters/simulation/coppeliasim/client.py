from __future__ import annotations

from dataclasses import dataclass, field
from math import tan
from typing import Any, Mapping

import numpy as np


@dataclass
class CoppeliaSimClient:
    """
    Thin wrapper around CoppeliaSim ZMQ Remote API with a stable project-facing API.
    """

    remote_api_client: Any
    sim: Any
    enable_stepping: bool = False
    _handle_cache: dict[str, int] = field(default_factory=dict, init=False, repr=False)

    @classmethod
    def connect(cls, simulation_config: Mapping[str, Any] | None = None) -> "CoppeliaSimClient":
        cfg = dict(simulation_config or {})
        host = str(cfg.get("host", "127.0.0.1"))
        port = int(cfg.get("port", 23000))
        enable_stepping = bool(cfg.get("synchronous", False))

        remote_api_module_error: Exception | None = None
        remote_api_client_cls: Any | None = None
        try:
            from coppeliasim_zmqremoteapi_client import RemoteAPIClient as _RemoteAPIClient

            remote_api_client_cls = _RemoteAPIClient
        except Exception as exc:  # pragma: no cover - depends on external package
            remote_api_module_error = exc

        if remote_api_client_cls is None:
            raise RuntimeError(
                "Could not import CoppeliaSim ZMQ client. Install "
                "'coppeliasim-zmqremoteapi-client' to run the official simulation app."
            ) from remote_api_module_error

        remote_api_client = remote_api_client_cls(host=host, port=port)
        sim = remote_api_client.require("sim")

        if enable_stepping:
            set_stepping = getattr(sim, "setStepping", None)
            if callable(set_stepping):
                set_stepping(True)

        return cls(
            remote_api_client=remote_api_client,
            sim=sim,
            enable_stepping=enable_stepping,
        )

    def start_simulation(self) -> None:
        starter = getattr(self.sim, "startSimulation", None)
        if callable(starter):
            starter()

    def step_simulation(self) -> None:
        if not self.enable_stepping:
            return
        stepper = getattr(self.sim, "step", None)
        if callable(stepper):
            stepper()

    def stop_simulation(self) -> None:
        stopper = getattr(self.sim, "stopSimulation", None)
        if callable(stopper):
            stopper()

    def get_joint_position(self, *, robot_handle: Any, joint_name: str) -> float:
        joint_handle = self._resolve_handle(joint_name)
        return float(self.sim.getJointPosition(joint_handle))

    def get_joint_velocity(self, *, robot_handle: Any, joint_name: str) -> float:
        joint_handle = self._resolve_handle(joint_name)
        getter = getattr(self.sim, "getJointVelocity", None)
        if callable(getter):
            return float(getter(joint_handle))
        return 0.0

    def set_joint_target_position(self, *, robot_handle: Any, joint_name: str, value: float) -> None:
        joint_handle = self._resolve_handle(joint_name)
        self.sim.setJointTargetPosition(joint_handle, float(value))

    def set_joint_torque(self, *, robot_handle: Any, joint_name: str, value: float) -> None:
        joint_handle = self._resolve_handle(joint_name)
        setter = getattr(self.sim, "setJointTargetForce", None)
        if callable(setter):
            setter(joint_handle, float(value))
            return
        setter = getattr(self.sim, "setJointForce", None)
        if callable(setter):
            setter(joint_handle, float(value))

    def get_object_position(self, *, handle: Any, reference_frame: str = "world") -> list[float]:
        object_handle = self._resolve_handle(handle)
        reference_handle = -1 if reference_frame == "world" else self._resolve_handle(reference_frame)
        return list(self.sim.getObjectPosition(object_handle, reference_handle))

    def get_object_quaternion(self, *, handle: Any, reference_frame: str = "world") -> list[float]:
        object_handle = self._resolve_handle(handle)
        reference_handle = -1 if reference_frame == "world" else self._resolve_handle(reference_frame)
        return list(self.sim.getObjectQuaternion(object_handle, reference_handle))

    def get_sim_time(self) -> float:
        return float(self.sim.getSimulationTime())

    def get_camera_rgb(self, *, camera_handle: Any) -> np.ndarray:
        sensor_handle = self._resolve_handle(camera_handle)

        getter = getattr(self.sim, "getVisionSensorImg", None)
        if callable(getter):
            payload = getter(sensor_handle)
        else:
            getter = getattr(self.sim, "getVisionSensorCharImage", None)
            if not callable(getter):
                raise NotImplementedError("CoppeliaSim 'sim' API does not provide camera RGB image access.")
            payload = getter(sensor_handle)

        image, resolution = payload
        width, height = int(resolution[0]), int(resolution[1])
        if isinstance(image, (bytes, bytearray, memoryview)):
            rgb = np.frombuffer(image, dtype=np.uint8).reshape((height, width, 3))
        else:
            rgb = np.asarray(image, dtype=np.uint8).reshape((height, width, 3))
        return np.flipud(rgb)

    def get_camera_depth(self, *, camera_handle: Any) -> np.ndarray:
        sensor_handle = self._resolve_handle(camera_handle)
        getter = getattr(self.sim, "getVisionSensorDepth", None)
        if not callable(getter):
            raise NotImplementedError("CoppeliaSim 'sim' API does not provide camera depth access.")
        depth, resolution = getter(sensor_handle)
        width, height = int(resolution[0]), int(resolution[1])
        depth_map = np.asarray(depth, dtype=float).reshape((height, width))
        return np.flipud(depth_map)

    def get_camera_intrinsics(self, *, camera_handle: Any) -> np.ndarray:
        sensor_handle = self._resolve_handle(camera_handle)
        resolution_getter = getattr(self.sim, "getVisionSensorRes", None)
        if not callable(resolution_getter):
            return np.eye(3, dtype=float)

        resolution = resolution_getter(sensor_handle)
        width, height = float(resolution[0]), float(resolution[1])

        angle = None
        float_param_getter = getattr(self.sim, "getObjectFloatParam", None)
        perspective_key = getattr(self.sim, "visionfloatparam_perspective_angle", None)
        if callable(float_param_getter) and perspective_key is not None:
            angle = float_param_getter(sensor_handle, perspective_key)

        if angle is None:
            return np.array(
                [
                    [1.0, 0.0, width * 0.5],
                    [0.0, 1.0, height * 0.5],
                    [0.0, 0.0, 1.0],
                ],
                dtype=float,
            )

        fx = (width * 0.5) / tan(float(angle) * 0.5)
        fy = fx
        cx = (width - 1.0) * 0.5
        cy = (height - 1.0) * 0.5
        return np.array([[fx, 0.0, cx], [0.0, fy, cy], [0.0, 0.0, 1.0]], dtype=float)

    def get_camera_extrinsics(self, *, camera_handle: Any) -> dict[str, Any]:
        sensor_handle = self._resolve_handle(camera_handle)
        position = self.get_object_position(handle=sensor_handle, reference_frame="world")
        orientation = self.get_object_quaternion(handle=sensor_handle, reference_frame="world")
        return {
            "position": position,
            "orientation_quat_xyzw": orientation,
            "frame_id": "world",
            "child_frame_id": str(camera_handle),
            "timestamp": self.get_sim_time(),
        }

    def _resolve_handle(self, object_ref: Any) -> int:
        if isinstance(object_ref, int):
            return object_ref

        key = str(object_ref)
        cached = self._handle_cache.get(key)
        if cached is not None:
            return cached

        for candidate in (key, f"/{key}", f"./{key}"):
            try:
                resolved = int(self.sim.getObject(candidate))
                self._handle_cache[key] = resolved
                return resolved
            except Exception:
                continue

        raise ValueError(f"Could not resolve CoppeliaSim object handle from '{key}'.")
