from __future__ import annotations

from unittest.mock import MagicMock, patch

from manipulator_framework.apps.simulation_app import main


@patch("manipulator_framework.apps.simulation_app.os.path.exists", return_value=True)
@patch("manipulator_framework.apps.simulation_app.CoppeliaSimClient")
@patch("manipulator_framework.apps.simulation_app.YAMLConfigurationLoader")
@patch("manipulator_framework.apps.simulation_app.SimulationComposer")
def test_simulation_app_loads_config_builds_use_case_and_executes(
    composer_cls,
    loader_cls,
    sim_client_cls,
    _exists_mock,
) -> None:
    use_case = MagicMock()
    use_case.execute.return_value = MagicMock(run_id="run_sim")

    config = {"simulation": {"host": "127.0.0.1", "port": 23000}}
    loader = MagicMock()
    loader.load.return_value = config
    loader.resolve.return_value = config
    loader_cls.return_value = loader

    composer = MagicMock()
    composer.build_request_factory.return_value = MagicMock(
        build_experiment_request=MagicMock(return_value=MagicMock())
    )
    composer.build_run_pbvs_with_avoidance.return_value = use_case
    composer_cls.return_value = composer

    exit_code = main()

    assert exit_code == 0
    sim_client_cls.connect.assert_called_once_with(config["simulation"])
    composer_cls.assert_called_once()
    composer.build_run_pbvs_with_avoidance.assert_called_once()
    use_case.execute.assert_called_once()


@patch("manipulator_framework.apps.simulation_app.os.path.exists", return_value=True)
@patch("manipulator_framework.apps.simulation_app.CoppeliaSimClient")
@patch("manipulator_framework.apps.simulation_app.YAMLConfigurationLoader")
@patch("manipulator_framework.apps.simulation_app.SimulationComposer")
def test_simulation_app_skips_coppeliasim_connection_when_backend_is_pyplot(
    composer_cls,
    loader_cls,
    sim_client_cls,
    _exists_mock,
) -> None:
    use_case = MagicMock()
    use_case.execute.return_value = MagicMock(run_id="run_sim")

    config = {"simulation": {"backend": "pyplot"}}
    loader = MagicMock()
    loader.load.return_value = config
    loader.resolve.return_value = config
    loader_cls.return_value = loader

    composer = MagicMock()
    composer.build_request_factory.return_value = MagicMock(
        build_experiment_request=MagicMock(return_value=MagicMock())
    )
    composer.build_run_pbvs_with_avoidance.return_value = use_case
    composer_cls.return_value = composer

    exit_code = main()

    assert exit_code == 0
    sim_client_cls.connect.assert_not_called()
    composer_cls.assert_called_once()
    composer.build_run_pbvs_with_avoidance.assert_called_once()
    use_case.execute.assert_called_once()
