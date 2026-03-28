from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .constants import IIWA_DOF, IIWA_MODEL_NAME
from .default_configurations import get_qr, get_qz
from .dh_parameters import DHRow, get_iiwa14r820_dh_parameters
from .frames import BASE_FRAME, FLANGE_FRAME, TOOL_FRAME
from .joint_limits import JointLimits, TorqueLimits, get_iiwa14r820_joint_limits, get_iiwa14r820_torque_limits


@dataclass(frozen=True)
class Iiwa14R820Model:
    """
    Pure logical robot model for the KUKA LBR iiwa 14R820.

    This class stores the canonical kinematic and nominal limit data,
    but does not perform simulation, actuation, sensing, or middleware integration.
    """

    name: str = IIWA_MODEL_NAME
    dof: int = IIWA_DOF
    base_frame: str = BASE_FRAME
    flange_frame: str = FLANGE_FRAME
    tool_frame: str = TOOL_FRAME

    @property
    def dh_parameters(self) -> tuple[DHRow, ...]:
        return get_iiwa14r820_dh_parameters()

    @property
    def joint_limits(self) -> JointLimits:
        return get_iiwa14r820_joint_limits()

    @property
    def torque_limits(self) -> TorqueLimits:
        return get_iiwa14r820_torque_limits()

    @property
    def qz(self) -> np.ndarray:
        return get_qz()

    @property
    def qr(self) -> np.ndarray:
        return get_qr()

    def validate_configuration(self, q: np.ndarray) -> None:
        q_arr = np.asarray(q, dtype=float).reshape(-1)
        if q_arr.size != self.dof:
            raise ValueError(f"Expected configuration with {self.dof} joints, got {q_arr.size}.")
        if not self.joint_limits.contains(q_arr):
            raise ValueError("Joint configuration is outside joint limits.")
