from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from manipulator_framework.application.composition.application_composer import ApplicationComposer
from manipulator_framework.application.use_cases.run_controller_benchmark_app import (
    RunControllerBenchmarkApp,
)
from manipulator_framework.application.use_cases.run_joint_trajectory import RunJointTrajectory
from manipulator_framework.application.use_cases.run_pbvs_with_avoidance import (
    RunPBVSWithAvoidance,
)


@dataclass
class SimulationComposer(ApplicationComposer):
    """
    Real app-facing composition root for simulation, experiment and benchmark apps.

    This stage closes app composition, not the full concrete simulation/hardware
    orchestration. The app layer remains thin and delegates to typed requests and
    application use cases.
    """

    config: dict[str, Any]
    sim_client: object | None = None
    pyplot_backend: object | None = None

    def build_simulation_use_case(self) -> RunJointTrajectory:
        return self.build_run_joint_trajectory()

    def build_experiment_use_case(self) -> RunPBVSWithAvoidance:
        return self.build_run_pbvs_with_avoidance()

    def build_benchmark_use_case(self) -> RunControllerBenchmarkApp:
        return self.build_benchmark_app_use_case()
