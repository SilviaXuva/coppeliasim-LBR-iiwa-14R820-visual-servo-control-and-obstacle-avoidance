from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from manipulator_framework.adapters.simulation.coppeliasim import CoppeliaSimClient
from manipulator_framework.application.composition.simulation_composer import SimulationComposer
from manipulator_framework.application.dto.run_requests import (
    RunPBVSProtocolRequest,
    RunPBVSWithAvoidanceRequest,
)
from manipulator_framework.application.dto.run_responses import (
    ProtocolRunSummary,
    RunPBVSProtocolResponse,
)
from manipulator_framework.application.use_cases.compare_runs import CompareRuns
from manipulator_framework.infrastructure.config.loader import YAMLConfigurationLoader, deep_merge


@dataclass
class RunPBVSProtocol:
    config_loader: YAMLConfigurationLoader = field(default_factory=YAMLConfigurationLoader)
    compare_runs_use_case: CompareRuns = field(default_factory=CompareRuns)
    sim_client_factory: Callable[[dict[str, Any]], Any] = CoppeliaSimClient.connect
    composer_factory: Callable[..., SimulationComposer] = SimulationComposer

    def execute(self, request: RunPBVSProtocolRequest) -> RunPBVSProtocolResponse:
        protocol_file = Path(request.protocol_path)
        if not protocol_file.exists():
            raise FileNotFoundError(f"Protocol file not found: {protocol_file}")

        protocol = self.config_loader.load(str(protocol_file))
        repetitions = int(protocol.get("repetitions", 0))
        seeds = [int(seed) for seed in protocol.get("seeds", ())]
        if repetitions <= 0:
            raise ValueError("Protocol repetitions must be positive.")
        if len(seeds) != repetitions:
            raise ValueError("Protocol seeds length must match repetitions.")

        app_config_path = Path(str(protocol.get("app_config", "configs/app/pbvs_official.yaml")))
        if not app_config_path.exists():
            raise FileNotFoundError(f"App config file not found: {app_config_path}")

        app_config = self.config_loader.load_and_resolve(str(app_config_path))
        protocol_overrides = dict(protocol.get("resolved_config", {}))
        merged_config = deep_merge(app_config, protocol_overrides)
        merged_config.setdefault("experiment", {})
        protocol_name = str(protocol.get("name", "pbvs_protocol"))
        merged_config["experiment"].setdefault("name", protocol_name)

        run_ids: list[str] = []
        run_summaries: list[ProtocolRunSummary] = []
        for repetition_index, seed in enumerate(seeds, start=1):
            run_config = deepcopy(merged_config)
            run_config.setdefault("experiment", {})
            run_config["experiment"]["seed"] = int(seed)

            run_id = (
                f"{run_config['experiment']['name']}"
                f"_rep_{repetition_index}"
                f"_seed_{seed}"
            )

            simulation_cfg = run_config.get("simulation", {})
            backend_name = str(simulation_cfg.get("backend", "coppeliasim")).lower()
            sim_client = (
                self.sim_client_factory(simulation_cfg)
                if backend_name == "coppeliasim"
                else None
            )
            composer = self.composer_factory(config=run_config, sim_client=sim_client)
            use_case = composer.build_run_pbvs_with_avoidance()

            response = use_case.execute(
                RunPBVSWithAvoidanceRequest(
                    run_id=run_id,
                    config=run_config,
                    seed=int(seed),
                    duration=float(run_config.get("planning", {}).get("duration", 1.0)),
                    enable_avoidance=bool(
                        run_config.get("planning", {}).get("enable_avoidance", True)
                    ),
                )
            )

            run_ids.append(run_id)
            run_summaries.append(
                ProtocolRunSummary(
                    run_id=run_id,
                    success=bool(response.run_result.success),
                    final_visual_error=_as_optional_float(
                        response.run_result.summary.get("final_visual_error")
                    ),
                    minimum_clearance=_as_optional_float(
                        response.run_result.summary.get("minimum_clearance")
                    ),
                )
            )

        self.compare_runs_use_case.execute(tuple(run_ids))
        return RunPBVSProtocolResponse(
            protocol_name=protocol_name,
            repetitions=repetitions,
            run_ids=tuple(run_ids),
            runs=tuple(run_summaries),
        )


def _as_optional_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None
