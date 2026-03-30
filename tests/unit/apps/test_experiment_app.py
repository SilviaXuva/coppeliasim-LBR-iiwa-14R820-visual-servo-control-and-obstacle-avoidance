from __future__ import annotations

from unittest.mock import MagicMock, patch

from manipulator_framework.apps.experiment_app import main


@patch("manipulator_framework.apps.experiment_app.ApplicationComposer")
@patch("manipulator_framework.apps.experiment_app.YAMLConfigurationLoader")
def test_experiment_app_executes_experiment_use_case_without_simulation_section(
    loader_cls,
    composer_cls,
) -> None:
    loader = MagicMock()
    config = {"app": {"name": "experiment"}}
    loader.load.return_value = config
    loader.resolve.return_value = config
    loader_cls.return_value = loader

    use_case = MagicMock()
    use_case.execute.return_value = MagicMock(run_id="run_exp")

    composer = MagicMock()
    composer.build_experiment_use_case.return_value = use_case
    composer_cls.return_value = composer

    exit_code = main()

    assert exit_code == 0
    composer.build_experiment_use_case.assert_called_once()
    use_case.execute.assert_called_once()


@patch("manipulator_framework.apps.experiment_app.SimulationComposer")
@patch("manipulator_framework.apps.experiment_app.CoppeliaSimClient")
@patch("manipulator_framework.apps.experiment_app.YAMLConfigurationLoader")
def test_experiment_app_uses_simulation_composer_when_simulation_section_exists(
    loader_cls,
    sim_client_cls,
    composer_cls,
) -> None:
    loader = MagicMock()
    config = {"app": {"name": "experiment"}, "simulation": {"host": "127.0.0.1"}}
    loader.load.return_value = config
    loader.resolve.return_value = config
    loader_cls.return_value = loader

    use_case = MagicMock()
    use_case.execute.return_value = MagicMock(run_id="run_exp")

    composer = MagicMock()
    composer.build_experiment_use_case.return_value = use_case
    composer_cls.return_value = composer

    exit_code = main()

    assert exit_code == 0
    sim_client_cls.connect.assert_called_once_with(config["simulation"])
    composer.build_experiment_use_case.assert_called_once()
    use_case.execute.assert_called_once()
