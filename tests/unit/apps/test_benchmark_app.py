from __future__ import annotations

from unittest.mock import MagicMock, patch

from manipulator_framework.apps.benchmark_app import main


@patch("manipulator_framework.apps.benchmark_app.SimulationComposer")
@patch("manipulator_framework.apps.benchmark_app.YAMLConfigurationLoader")
def test_benchmark_app_executes_benchmark_use_case(
    loader_cls,
    composer_cls,
) -> None:
    loader = MagicMock()
    loader.load.return_value = {}
    loader.resolve.return_value = {"app": {"name": "benchmark"}}
    loader_cls.return_value = loader

    use_case = MagicMock()
    use_case.execute.return_value = MagicMock(run_id="run_bench")

    composer = MagicMock()
    composer.build_benchmark_use_case.return_value = use_case
    composer_cls.return_value = composer

    exit_code = main()

    assert exit_code == 0
    composer.build_benchmark_use_case.assert_called_once()
    use_case.execute.assert_called_once()
