from __future__ import annotations

from pathlib import Path

from manipulator_framework.infrastructure.config import ExperimentBundleLoader


def test_experiment_bundle_loader_builds_protocol_and_scenario(tmp_path: Path) -> None:
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
name: person_in_workspace
description: PBVS scenario with one person in workspace.
parameters:
  obstacle:
    type: person
    safety_radius_m: 0.25
""".strip(),
        encoding="utf-8",
    )

    protocol_file = tmp_path / "protocol.yaml"
    protocol_file.write_text(
        """
name: pbvs_with_avoidance_protocol
repetitions: 2
seeds: [11, 12]
compared_methods:
  - pbvs_baseline
  - pbvs_with_avoidance
resolved_config:
  backend_name: coppeliasim
  scenario_name: person_in_workspace
""".strip(),
        encoding="utf-8",
    )

    loader = ExperimentBundleLoader()
    bundle = loader.load_bundle(protocol_file=protocol_file, scenario_file=scenario_file)

    assert bundle.protocol.name == "pbvs_with_avoidance_protocol"
    assert bundle.protocol.repetitions == 2
    assert bundle.protocol.seeds == (11, 12)
    assert bundle.protocol.compared_methods == ("pbvs_baseline", "pbvs_with_avoidance")
    assert bundle.protocol.scenario.name == "person_in_workspace"
    assert bundle.protocol.scenario.parameters["obstacle"]["type"] == "person"
