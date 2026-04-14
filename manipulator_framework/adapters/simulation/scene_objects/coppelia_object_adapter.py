from __future__ import annotations

from ....core.models.pose import Pose
from ....core.ports.object_port import ObjectPort


class CoppeliaObjectAdapter(ObjectPort):
    """Object adapter backed by CoppeliaSim Remote API."""

    def __init__(
        self,
        sim: object,
        object_path: str,
        *,
        gripper_attach_path: str | None = None,
    ) -> None:
        self._sim = sim
        self._object_handle = self._sim.getObject(object_path)
        self._gripper_attach_handle: int | None = None
        if gripper_attach_path is not None:
            self._gripper_attach_handle = self._sim.getObject(gripper_attach_path)

    def get_pose(self) -> Pose:
        position = self._sim.getObjectPosition(
            self._object_handle,
            self._sim.handle_world,
        )
        alpha_beta_gamma = self._sim.getObjectOrientation(
            self._object_handle,
            self._sim.handle_world,
        )
        yaw, pitch, roll = self._sim.alphaBetaGammaToYawPitchRoll(
            alpha_beta_gamma[0],
            alpha_beta_gamma[1],
            alpha_beta_gamma[2],
        )
        return Pose(
            x=float(position[0]),
            y=float(position[1]),
            z=float(position[2]),
            roll=float(roll),
            pitch=float(pitch),
            yaw=float(yaw),
        )

    def set_pose(self, pose: Pose) -> None:
        self._sim.setObjectPosition(
            self._object_handle,
            self._sim.handle_world,
            (float(pose.x), float(pose.y), float(pose.z)),
        )
        alpha_beta_gamma = self._yaw_pitch_roll_to_alpha_beta_gamma(pose)
        self._sim.setObjectOrientation(
            self._object_handle,
            self._sim.handle_world,
            alpha_beta_gamma,
        )

    def attach_to_gripper(self) -> None:
        if self._gripper_attach_handle is None:
            raise ValueError("`gripper_attach_path` is required to attach object to gripper.")
        self._sim.setObjectParent(
            self._object_handle,
            self._gripper_attach_handle,
            True,
        )

    def detach_from_gripper(self) -> None:
        self._sim.setObjectParent(
            self._object_handle,
            self._sim.handle_world,
            True,
        )

    def _yaw_pitch_roll_to_alpha_beta_gamma(
        self,
        pose: Pose,
    ) -> tuple[float, float, float]:
        try:
            alpha_beta_gamma = self._sim.yawPitchRollToAlphaBetaGamma(
                float(pose.yaw),
                float(pose.pitch),
                float(pose.roll),
            )
            return (
                float(alpha_beta_gamma[0]),
                float(alpha_beta_gamma[1]),
                float(alpha_beta_gamma[2]),
            )
        except Exception:
            # Fallback for environments where conversion helper is unavailable.
            return (
                float(pose.roll),
                float(pose.pitch),
                float(pose.yaw),
            )
