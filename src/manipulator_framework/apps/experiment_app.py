from __future__ import annotations

import argparse
import os
from manipulator_framework.adapters.simulation.coppeliasim import CoppeliaSimClient
from manipulator_framework.application.composition.application_composer import (
    ApplicationComposer,
)
from manipulator_framework.application.composition.simulation_composer import (
    SimulationComposer,
)
from manipulator_framework.infrastructure.config.loader import YAMLConfigurationLoader


def main(config_path: str = "configs/app/experiment.yaml") -> int:
    """Run the scientific experiment pipeline in simulation."""
    if not os.path.exists(config_path):
        print(f"Config not found at {config_path}")
        return 1

    loader = YAMLConfigurationLoader()
    raw_config = loader.load(config_path)
    config = loader.resolve(raw_config)

    simulation_cfg = config.get("simulation", {})
    if isinstance(simulation_cfg, dict) and simulation_cfg:
        backend = str(simulation_cfg.get("backend", "coppeliasim")).lower()
        sim_client = CoppeliaSimClient.connect(simulation_cfg) if backend == "coppeliasim" else None
        composer = SimulationComposer(config=config, sim_client=sim_client)
    else:
        composer = ApplicationComposer(config=config)
    
    request_factory = composer.build_request_factory()
    use_case = composer.build_experiment_use_case()

    # Build the specific experiment request
    request = request_factory.build_experiment_request()
    
    print(f"--- Starting Experiment: {request.run_id} ---")
    print(f"Scenario: {request.config.get('experiment', {}).get('name')}")
    
    # Execute the thickened scientific pipeline
    response = use_case.execute(request)

    print(f"--- Finished ---")
    print(f"Status: {'SUCCESS' if response.run_result.success else 'FAILED'}")
    print(f"Persistence Path: {response.run_result.run_id}")
    
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run experiment application pipeline.")
    parser.add_argument(
        "--config",
        default="configs/app/experiment.yaml",
        help="Path to YAML config file.",
    )
    args = parser.parse_args()
    raise SystemExit(main(args.config))
