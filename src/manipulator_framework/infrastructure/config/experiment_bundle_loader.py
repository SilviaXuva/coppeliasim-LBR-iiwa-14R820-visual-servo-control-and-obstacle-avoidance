from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from manipulator_framework.core.experiments import ExperimentProtocol, ScenarioDefinition


@dataclass(frozen=True)
class ExperimentBundle:
    """
    External experimental bundle loaded from the experiments/ tree.
    """
    protocol: ExperimentProtocol
    scenario_file: Path
    protocol_file: Path


class ExperimentBundleLoader:
    """
    Load minimal experimental bundles from experiments/configs and experiments/scenarios.
    """

    def load_yaml(self, path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def load_bundle(self, protocol_file: str | Path, scenario_file: str | Path) -> ExperimentBundle:
        protocol_path = Path(protocol_file)
        scenario_path = Path(scenario_file)

        protocol_payload = self.load_yaml(protocol_path)
        scenario_payload = self.load_yaml(scenario_path)

        scenario = self._build_scenario(scenario_payload)
        protocol = self._build_protocol(protocol_payload, scenario)

        return ExperimentBundle(
            protocol=protocol,
            scenario_file=scenario_path,
            protocol_file=protocol_path,
        )

    def _build_scenario(self, payload: dict[str, Any]) -> ScenarioDefinition:
        name = str(payload.get("name", "")).strip()
        description = str(payload.get("description", "")).strip()
        parameters = payload.get("parameters", {})

        if not name:
            raise ValueError("Scenario file must define a non-empty 'name'.")
        if not description:
            raise ValueError("Scenario file must define a non-empty 'description'.")
        if not isinstance(parameters, dict):
            raise ValueError("'parameters' in scenario file must be a mapping.")

        return ScenarioDefinition(
            name=name,
            description=description,
            parameters=parameters,
        )

    def _build_protocol(
        self,
        payload: dict[str, Any],
        scenario: ScenarioDefinition,
    ) -> ExperimentProtocol:
        name = str(payload.get("name", "")).strip()
        repetitions = int(payload.get("repetitions", 0))
        seeds_raw = payload.get("seeds", [])
        compared_methods_raw = payload.get("compared_methods", [])
        resolved_config = payload.get("resolved_config", {})

        if not name:
            raise ValueError("Protocol file must define a non-empty 'name'.")
        if not isinstance(seeds_raw, list):
            raise ValueError("'seeds' in protocol file must be a list.")
        if not isinstance(compared_methods_raw, list):
            raise ValueError("'compared_methods' in protocol file must be a list.")
        if not isinstance(resolved_config, dict):
            raise ValueError("'resolved_config' in protocol file must be a mapping.")

        return ExperimentProtocol(
            name=name,
            scenario=scenario,
            repetitions=repetitions,
            seeds=tuple(int(seed) for seed in seeds_raw),
            compared_methods=tuple(str(method) for method in compared_methods_raw),
            resolved_config=resolved_config,
        )
