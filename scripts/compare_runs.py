from __future__ import annotations

from pathlib import Path
from manipulator_framework.application.use_cases.compare_runs import CompareRuns


def compare_runs(
    run_ids: tuple[str, ...],
    runs_dir: Path = Path("experiments/runs"),
    output_file: Path = Path("experiments/reports/run_comparison.json"),
) -> int:
    use_case = CompareRuns(runs_dir=runs_dir, output_file=output_file)
    result = use_case.execute(run_ids)
    print(f"[OK] Comparison written to {output_file}")
    return result


def main() -> int:
    import sys

    if len(sys.argv) < 3:
        raise SystemExit(
            "Usage: compare-runs <run_id_1> <run_id_2> [<run_id_3> ...]"
        )
    return compare_runs(tuple(sys.argv[1:]))


if __name__ == "__main__":
    raise SystemExit(main())
