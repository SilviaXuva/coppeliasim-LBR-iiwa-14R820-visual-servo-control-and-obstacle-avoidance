from __future__ import annotations

import argparse
from typing import Sequence

from .application.orchestrators.experiment_runner import ExperimentRunner
from .config.experiment_config import load_experiment_config
from .infrastructure.results_repository import ResultsRepository


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run reproducible experiments for manipulator_framework.",
    )
    parser.add_argument(
        "--experiment",
        choices=["pick_and_place"],
        required=True,
        help="Experiment name to run.",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Optional JSON config path to override defaults.",
    )
    parser.add_argument(
        "--backend",
        choices=["mock", "coppelia"],
        default=None,
        help="Backend used to wire dependencies.",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=None,
        help="Number of experiment cycles.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory where JSON/CSV artifacts are stored.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    config = load_experiment_config(
        experiment=args.experiment,
        config_path=args.config,
    )
    if args.backend is not None:
        config.runtime.backend = args.backend
    if args.cycles is not None:
        config.runtime.cycles = args.cycles
    if args.output_dir is not None:
        config.persistence.output_dir = args.output_dir
    if args.seed is not None:
        config.runtime.random_seed = args.seed

    repository = ResultsRepository(config.persistence.output_dir)
    runner = ExperimentRunner.from_config(
        config=config,
        results_repository=repository,
    )
    execution = runner.run_experiment()

    print(f"Experiment: {execution.experiment}")
    print(f"Run ID: {execution.run_id}")
    print("Metrics:")
    for key, value in execution.metrics.items():
        print(f"  - {key}: {value}")
    if len(execution.artifacts) > 0:
        print("Artifacts:")
        for key, value in execution.artifacts.items():
            print(f"  - {key}: {value}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
