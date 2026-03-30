from __future__ import annotations

import os

from manipulator_framework.adapters.simulation.coppeliasim import CoppeliaSimClient
from manipulator_framework.application.composition.simulation_composer import (
    SimulationComposer,
)
from manipulator_framework.infrastructure.config.loader import YAMLConfigurationLoader


def main(config_path: str = "configs/app/pbvs_official.yaml") -> int:
    """Run the official simulation pipeline entrypoint."""
    if not os.path.exists(config_path):
        print(f"Config not found at {config_path}")
        return 1

    loader = YAMLConfigurationLoader()
    raw_config = loader.load(config_path)
    config = loader.resolve(raw_config)
    simulation_cfg = config.get("simulation", {})
    backend = str(simulation_cfg.get("backend", "coppeliasim")).lower()
    sim_client = None
    if backend == "coppeliasim":
        sim_client = CoppeliaSimClient.connect(simulation_cfg)

    composer = SimulationComposer(config=config, sim_client=sim_client)
    request_factory = composer.build_request_factory()
    use_case = composer.build_run_pbvs_with_avoidance()
    request = request_factory.build_experiment_request()
    response = use_case.execute(request)

    print(response.run_result.summary)
    return 0


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "configs/app/pbvs_official.yaml"
    raise SystemExit(main(path))
