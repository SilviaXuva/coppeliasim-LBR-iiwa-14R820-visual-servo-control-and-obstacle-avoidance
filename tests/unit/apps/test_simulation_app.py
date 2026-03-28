from __future__ import annotations

from unittest.mock import MagicMock, patch

from manipulator_framework.apps.simulation_app import main


@patch("manipulator_framework.apps.simulation_app.SimulationComposer")
@patch("manipulator_framework.apps.simulation_app.YAMLConfigurationLoader")
def test_simulation_app_loads_config_builds_use_case_and_executes(
    loader_cls,
    composer_cls,
) -> None:
    loader = MagicMock()
    loader.load.return_value = {"raw": True}
    loader.resolve.return_value = {"app": {"name": "simulation"}}
    loader_cls.return_value = loader

    use_case = MagicMock()
    use_case.execute.return_value = MagicMock(run_id="run_sim")

    composer = MagicMock()
    composer.build_simulation_use_case.return_value = use_case
    composer_cls.return_value = composer

    exit_code = main()

    assert exit_code == 0
    loader.load.assert_called_once()
    loader.resolve.assert_called_once()
    composer.build_simulation_use_case.assert_called_once()
    use_case.execute.assert_called_once()
