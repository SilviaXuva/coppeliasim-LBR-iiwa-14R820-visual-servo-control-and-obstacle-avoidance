from __future__ import annotations

from manipulator_framework.infrastructure.config.loader import YAMLConfigurationLoader


def test_config_loader_resolves_defaults_with_partial_override() -> None:
    loader = YAMLConfigurationLoader()

    resolved = loader.resolve(
        {
            "app": {
                "mode": "experiment",
                "use_case": "run_pbvs_with_avoidance",
            },
            "experiment": {
                "name": "partial_override",
                "seed": 99,
                "tags": ["unit"],
                "notes": "merge test",
            },
            "scenario": {
                "name": "person_in_workspace",
            },
            "visual_servoing": {
                "enabled": True,
            },
            "obstacle_avoidance": {
                "enabled": True,
            },
        }
    )

    assert resolved["app"]["name"] == "manipulator_framework"
    assert resolved["app"]["mode"] == "experiment"
    assert resolved["app"]["use_case"] == "run_pbvs_with_avoidance"
    assert resolved["runtime"]["dt"] == 0.05
    assert resolved["controller"]["kind"] == "joint_pd"
    assert resolved["visual_servoing"]["enabled"] is True
    assert resolved["obstacle_avoidance"]["enabled"] is True
    assert resolved["scenario"]["name"] == "person_in_workspace"
