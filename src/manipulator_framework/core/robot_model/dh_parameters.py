from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .constants import DEG_TO_RAD


@dataclass(frozen=True)
class DHRow:
    """Standard DH row for one revolute joint."""
    d: float
    a: float
    alpha_rad: float


def get_iiwa14r820_dh_parameters() -> tuple[DHRow, ...]:
    """
    Return the canonical standard DH parameter set for the KUKA LBR iiwa 14R820.

    Notes:
        This keeps only the geometric information required for kinematics.
    """
    return (
        DHRow(d=0.360, a=0.0, alpha_rad=90.0 * DEG_TO_RAD),
        DHRow(d=0.000, a=0.0, alpha_rad=-90.0 * DEG_TO_RAD),
        DHRow(d=0.420, a=0.0, alpha_rad=-90.0 * DEG_TO_RAD),
        DHRow(d=0.000, a=0.0, alpha_rad=90.0 * DEG_TO_RAD),
        DHRow(d=0.400, a=0.0, alpha_rad=90.0 * DEG_TO_RAD),
        DHRow(d=0.000, a=0.0, alpha_rad=-90.0 * DEG_TO_RAD),
        DHRow(d=0.230, a=0.0, alpha_rad=0.0 * DEG_TO_RAD),
    )
