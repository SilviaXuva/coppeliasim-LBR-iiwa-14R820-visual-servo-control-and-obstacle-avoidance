from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from manipulator_framework.application.dto.run_requests import (
    BenchmarkControllersRequest,
    RunJointTrajectoryRequest,
    RunPBVSWithAvoidanceRequest,
)


@dataclass(frozen=True)
class RunRequestFactory:
    """
    Build typed application requests from resolved app configuration.
    """

    config: dict[str, Any]

    def build_simulation_request(self) -> RunJointTrajectoryRequest:
        return RunJointTrajectoryRequest(
            run_id=self._build_run_id("simulation"),
            config=deepcopy(self.config),
            seed=int(self.config.get("experiment", {}).get("seed", 0)),
            duration=float(self.config.get("planning", {}).get("duration", 1.0)),
        )

    def build_experiment_request(self) -> RunPBVSWithAvoidanceRequest:
        return RunPBVSWithAvoidanceRequest(
            run_id=self._build_run_id("experiment"),
            config=deepcopy(self.config),
            seed=int(self.config.get("experiment", {}).get("seed", 0)),
            duration=float(self.config.get("planning", {}).get("duration", 1.0)),
        )

    def build_benchmark_request(self) -> BenchmarkControllersRequest:
        benchmark_cfg = self.config.get("benchmark", {})
        compared_methods = tuple(
            benchmark_cfg.get(
                "compared_methods",
                ("joint_pd", "adaptive_joint_pd"),
            )
        )
        repetitions = int(benchmark_cfg.get("repetitions", 2))

        return BenchmarkControllersRequest(
            run_id=self._build_run_id("benchmark"),
            config=deepcopy(self.config),
            seed=int(self.config.get("experiment", {}).get("seed", 0)),
            compared_methods=compared_methods,
            repetitions=repetitions,
        )

    def build_benchmark_run_request(
        self,
        *,
        method_name: str,
        repetition_index: int,
        seed: int,
    ) -> RunJointTrajectoryRequest:
        method_config = deepcopy(self.config)
        method_config.setdefault("controller", {})
        method_config["controller"]["kind"] = method_name

        return RunJointTrajectoryRequest(
            run_id=self._build_run_id(
                f"{method_name}_rep_{repetition_index + 1}",
                seed_override=seed,
            ),
            config=method_config,
            seed=seed,
            duration=float(method_config.get("planning", {}).get("duration", 1.0)),
        )

    def _build_run_id(self, prefix: str, seed_override: int | None = None) -> str:
        experiment_name = str(self.config.get("experiment", {}).get("name", "run")).strip() or "run"
        seed = (
            int(seed_override)
            if seed_override is not None
            else int(self.config.get("experiment", {}).get("seed", 0))
        )
        sanitized_prefix = prefix.replace(" ", "_")
        sanitized_name = experiment_name.replace(" ", "_")
        return f"{sanitized_name}_{sanitized_prefix}_seed_{seed}"
