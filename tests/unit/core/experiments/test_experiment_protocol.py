from __future__ import annotations

import pytest

from manipulator_framework.core.experiments import (
    ExperimentProtocol,
    ScenarioDefinition,
)


def test_experiment_protocol_accepts_valid_definition() -> None:
    scenario = ScenarioDefinition(
        name="synthetic_tracking",
        description="Synthetic scenario for protocol validation.",
        parameters={"dof": 7},
    )

    protocol = ExperimentProtocol(
        name="protocol_demo",
        scenario=scenario,
        repetitions=2,
        seeds=(123, 456),
        compared_methods=("pd", "adaptive_pd"),
        resolved_config={"dt": 0.01},
    )

    assert protocol.name == "protocol_demo"
    assert protocol.repetitions == 2
    assert protocol.seeds == (123, 456)


def test_experiment_protocol_rejects_seed_mismatch() -> None:
    scenario = ScenarioDefinition(
        name="synthetic_tracking",
        description="Synthetic scenario for protocol validation.",
    )

    with pytest.raises(ValueError, match="seeds length must match repetitions"):
        ExperimentProtocol(
            name="invalid_protocol",
            scenario=scenario,
            repetitions=2,
            seeds=(123,),
            compared_methods=("pd", "adaptive_pd"),
            resolved_config={},
        )
