from __future__ import annotations

from dataclasses import dataclass

GainConfig = float | tuple[float, ...]

DEFAULT_PICK_AND_PLACE_KIN_PI_KP: tuple[float, ...] = (
    1.64725,
    1.40056,
    1.40056,
    1.33690,
    1.36873,
    1.40056,
    1.36873,
)
DEFAULT_PICK_AND_PLACE_KIN_PI_KI: tuple[float, ...] = (
    1.23544,
    0.93371,
    0.93371,
    0.89127,
    0.91249,
    0.93371,
    0.91249,
)
DEFAULT_PICK_AND_PLACE_DYN_PD_KP: tuple[float, ...] = (
    80.00,
    85.00,
    25.00,
    19.00,
    10.00,
    20.00,
    5.00,
)
DEFAULT_PICK_AND_PLACE_DYN_PD_KV: tuple[float, ...] = (
    1.000,
    10.50,
    1.000,
    3.000,
    1.000,
    1.500,
    0.25,
)
DEFAULT_PICK_AND_PLACE_TAU_MIN: tuple[float, ...] = (
    -176.00,
    -176.00,
    -100.00,
    -100.00,
    -100.00,
    -38.00,
    -38.00,
)
DEFAULT_PICK_AND_PLACE_TAU_MAX: tuple[float, ...] = (
    176.00,
    176.00,
    100.00,
    100.00,
    100.00,
    38.00,
    38.00,
)


@dataclass(slots=True)
class ControllerConfig:
    kp: GainConfig = DEFAULT_PICK_AND_PLACE_KIN_PI_KP
    ki: GainConfig = DEFAULT_PICK_AND_PLACE_KIN_PI_KI
    kv: GainConfig = DEFAULT_PICK_AND_PLACE_DYN_PD_KV
    tau_min: tuple[float, ...] = DEFAULT_PICK_AND_PLACE_TAU_MIN
    tau_max: tuple[float, ...] = DEFAULT_PICK_AND_PLACE_TAU_MAX


def default_controller_config(experiment: str) -> ControllerConfig:
    if experiment == "pick_and_place_dyn_pd":
        return ControllerConfig(
            kp=DEFAULT_PICK_AND_PLACE_DYN_PD_KP,
            ki=DEFAULT_PICK_AND_PLACE_KIN_PI_KI,
            kv=DEFAULT_PICK_AND_PLACE_DYN_PD_KV,
            tau_min=DEFAULT_PICK_AND_PLACE_TAU_MIN,
            tau_max=DEFAULT_PICK_AND_PLACE_TAU_MAX,
        )
    return ControllerConfig(
        kp=DEFAULT_PICK_AND_PLACE_KIN_PI_KP,
        ki=DEFAULT_PICK_AND_PLACE_KIN_PI_KI,
        kv=DEFAULT_PICK_AND_PLACE_DYN_PD_KV,
        tau_min=DEFAULT_PICK_AND_PLACE_TAU_MIN,
        tau_max=DEFAULT_PICK_AND_PLACE_TAU_MAX,
    )
