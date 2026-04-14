from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from ._parsing import parse_gain, parse_vector, parse_vector_with_size
from .controller_config import (
    DEFAULT_PICK_AND_PLACE_DYN_PD_KV,
    DEFAULT_PICK_AND_PLACE_KIN_PI_KI,
    DEFAULT_PICK_AND_PLACE_KIN_PI_KP,
    DEFAULT_PICK_AND_PLACE_TAU_MAX,
    DEFAULT_PICK_AND_PLACE_TAU_MIN,
    GainConfig,
    default_controller_config,
)

DEFAULT_PICK_AND_PLACE_PLACE_POSE: tuple[float, ...] = (
    0.55,
    0.0,
    0.20,
    3.141592653589793,
    0.0,
    0.0,
)
DEFAULT_PICK_AND_PLACE_PRE_GRASP_OFFSET: tuple[float, ...] = (
    0.0,
    0.0,
    0.10,
)
DEFAULT_PICK_AND_PLACE_LIFT_OFFSET: tuple[float, ...] = (
    0.0,
    0.0,
    0.15,
)
DEFAULT_PICK_AND_PLACE_RETREAT_OFFSET: tuple[float, ...] = (
    0.0,
    0.0,
    0.10,
)


@dataclass(slots=True)
class PickAndPlaceConfig:
    kp: GainConfig = DEFAULT_PICK_AND_PLACE_KIN_PI_KP
    ki: GainConfig = DEFAULT_PICK_AND_PLACE_KIN_PI_KI
    kv: GainConfig = DEFAULT_PICK_AND_PLACE_DYN_PD_KV
    tau_min: tuple[float, ...] = DEFAULT_PICK_AND_PLACE_TAU_MIN
    tau_max: tuple[float, ...] = DEFAULT_PICK_AND_PLACE_TAU_MAX
    trajectory_duration_s: float = 1.5
    control_dt_s: float = 0.05
    target_height_offset_m: float = 0.15
    place_pose: tuple[float, ...] = DEFAULT_PICK_AND_PLACE_PLACE_POSE
    pre_grasp_offset: tuple[float, ...] = DEFAULT_PICK_AND_PLACE_PRE_GRASP_OFFSET
    lift_offset: tuple[float, ...] = DEFAULT_PICK_AND_PLACE_LIFT_OFFSET
    retreat_offset: tuple[float, ...] = DEFAULT_PICK_AND_PLACE_RETREAT_OFFSET
    marker_length_m: float = 0.05
    aruco_dictionary: str = "DICT_6X6_250"


def default_pick_and_place_config(experiment: str) -> PickAndPlaceConfig:
    controller = default_controller_config(experiment)
    return PickAndPlaceConfig(
        kp=controller.kp,
        ki=controller.ki,
        kv=controller.kv,
        tau_min=controller.tau_min,
        tau_max=controller.tau_max,
    )


def parse_pick_and_place_config(
    pick_data: Mapping[str, Any],
    *,
    experiment: str,
) -> PickAndPlaceConfig:
    defaults = default_pick_and_place_config(experiment)
    return PickAndPlaceConfig(
        kp=parse_gain(
            pick_data.get("kp", defaults.kp),
            "kp",
        ),
        ki=parse_gain(
            pick_data.get("ki", defaults.ki),
            "ki",
        ),
        kv=parse_gain(
            pick_data.get("kv", defaults.kv),
            "kv",
        ),
        tau_min=parse_vector(
            pick_data.get("tau_min", defaults.tau_min),
            "tau_min",
        ),
        tau_max=parse_vector(
            pick_data.get("tau_max", defaults.tau_max),
            "tau_max",
        ),
        trajectory_duration_s=float(
            pick_data.get("trajectory_duration_s", defaults.trajectory_duration_s)
        ),
        control_dt_s=float(
            pick_data.get("control_dt_s", defaults.control_dt_s)
        ),
        target_height_offset_m=float(
            pick_data.get("target_height_offset_m", defaults.target_height_offset_m)
        ),
        place_pose=parse_vector_with_size(
            pick_data.get("place_pose", defaults.place_pose),
            "place_pose",
            6,
        ),
        pre_grasp_offset=parse_vector_with_size(
            pick_data.get(
                "pre_grasp_offset",
                defaults.pre_grasp_offset,
            ),
            "pre_grasp_offset",
            3,
        ),
        lift_offset=parse_vector_with_size(
            pick_data.get("lift_offset", defaults.lift_offset),
            "lift_offset",
            3,
        ),
        retreat_offset=parse_vector_with_size(
            pick_data.get("retreat_offset", defaults.retreat_offset),
            "retreat_offset",
            3,
        ),
        marker_length_m=float(pick_data.get("marker_length_m", defaults.marker_length_m)),
        aruco_dictionary=str(pick_data.get("aruco_dictionary", defaults.aruco_dictionary)),
    )
