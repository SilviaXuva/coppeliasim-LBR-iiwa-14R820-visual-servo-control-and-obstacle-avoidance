from __future__ import annotations

from collections.abc import Sequence
from time import sleep
from typing import Callable

from ...core.ports.gripper_port import GripperPort


class CoppeliaGripperAdapter(GripperPort):
    """
    Gripper adapter backed by CoppeliaSim Remote API.

    This implementation controls a gripper through one or more gripper joints.
    """

    def __init__(
        self,
        sim: object,
        joints_paths: Sequence[str],
        open_joints_positions: float = 0.04,
        closed_joints_positions: float = 0.0,
        joints_positions_tolerance: float = 0.01,
        settle_steps: int = 5,
        step_callback: Callable[[], None] | None = None,
        poll_interval_s: float = 0.01,
        proximity_sensor_path: str | None = None,
        grasp_object_path: str | None = None,
        proximity_distance_threshold: float = 0.02,
    ) -> None:
        if len(joints_paths) == 0:
            raise ValueError("`joints_paths` must contain at least one joint path.")
        if joints_positions_tolerance < 0.0:
            raise ValueError("`joints_positions_tolerance` must be non-negative.")
        if settle_steps < 0:
            raise ValueError("`settle_steps` must be non-negative.")
        if poll_interval_s < 0.0:
            raise ValueError("`poll_interval_s` must be non-negative.")
        if proximity_distance_threshold < 0.0:
            raise ValueError("`proximity_distance_threshold` must be non-negative.")

        self._sim = sim
        self._joints_handles = tuple(self._sim.getObject(path) for path in joints_paths)
        self._open_joints_positions = float(open_joints_positions)
        self._closed_joints_positions = float(closed_joints_positions)
        self._joints_positions_tolerance = float(joints_positions_tolerance)
        self._settle_steps = int(settle_steps)
        self._step_callback = step_callback
        self._poll_interval_s = float(poll_interval_s)
        self._proximity_distance_threshold = float(proximity_distance_threshold)
        self._proximity_sensor_handle: int | None = None
        self._grasp_object_handle: int | None = None
        if proximity_sensor_path is not None:
            self._proximity_sensor_handle = self._sim.getObject(proximity_sensor_path)
        if grasp_object_path is not None:
            self._grasp_object_handle = self._sim.getObject(grasp_object_path)

    def open(self) -> None:
        self._set_joints_positions(self._open_joints_positions)

    def close(self) -> None:
        self._set_joints_positions(self._closed_joints_positions)

    def grasp(self) -> bool:
        self.close()
        self._advance_steps(self._settle_steps)
        if self._proximity_sensor_handle is not None:
            return self._has_grasp_contact()
        # Fallback heuristic when no sensor is available:
        # report success only when the commanded close target was reached.
        return self._wait_until_near_target(
            joints_target_positions=self._closed_joints_positions,
            max_steps=self._settle_steps,
        )

    def release(self) -> None:
        self.open()
        self._advance_steps(self._settle_steps)

    def _set_joints_positions(self, joints_target_positions: float) -> None:
        for joint_handle in self._joints_handles:
            self._sim.setJointTargetPosition(joint_handle, float(joints_target_positions))

    def _is_near_target(self, joints_target_positions: float) -> bool:
        if len(self._joints_handles) == 0:
            return False
        for joint_handle in self._joints_handles:
            try:
                current = float(self._sim.getJointPosition(joint_handle))
            except Exception:
                return False
            if abs(current - float(joints_target_positions)) > self._joints_positions_tolerance:
                return False
        return True

    def _wait_until_near_target(self, *, joints_target_positions: float, max_steps: int) -> bool:
        if self._is_near_target(joints_target_positions):
            return True
        for _ in range(max(0, max_steps)):
            self._advance_steps(1)
            if self._is_near_target(joints_target_positions):
                return True
        return False

    def _advance_steps(self, steps: int) -> None:
        for _ in range(max(0, steps)):
            if self._step_callback is not None:
                self._step_callback()
                continue
            step_method = getattr(self._sim, "step", None)
            if callable(step_method):
                step_method()
                continue
            if self._poll_interval_s > 0.0:
                sleep(self._poll_interval_s)

    def _has_grasp_contact(self) -> bool:
        if self._proximity_sensor_handle is None:
            return False
        target_handle = self._grasp_object_handle
        if target_handle is None:
            target_handle = getattr(self._sim, "handle_all", -1)
        try:
            proximity = self._sim.checkProximitySensor(
                self._proximity_sensor_handle,
                target_handle,
            )
        except Exception:
            return False
        if not isinstance(proximity, (tuple, list)) or len(proximity) == 0:
            return False
        detected = int(proximity[0]) == 1
        if not detected:
            return False
        if len(proximity) < 2:
            return True
        try:
            distance = float(proximity[1])
        except (TypeError, ValueError):
            return True
        return distance <= self._proximity_distance_threshold
