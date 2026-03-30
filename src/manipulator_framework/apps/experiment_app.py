from __future__ import annotations

from manipulator_framework.application.composition.simulation_composer import (
    SimulationComposer,
)
from manipulator_framework.infrastructure.config.loader import YAMLConfigurationLoader


def main(config_path: str = "configs/app/experiment.yaml") -> int:
    """Run the experiment app entrypoint."""
    loader = YAMLConfigurationLoader()
    raw_config = loader.load(config_path)
    config = loader.resolve(raw_config)

    composer = SimulationComposer(config=config)
    request_factory = composer.build_request_factory()
    use_case = composer.build_experiment_use_case()

    request = request_factory.build_experiment_request()
    response = use_case.execute(request)

    print(f"Experiment finished. run_id={response.run_result.run_schema.run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
