from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@dataclass
class CompareRuns:
    runs_dir: Path = Path("experiments/runs")
    output_file: Path = Path("experiments/reports/run_comparison.json")

    def execute(self, run_ids: tuple[str, ...]) -> int:
        if len(run_ids) < 2:
            raise ValueError("compare_runs requires at least two run ids.")

        comparison: dict[str, Any] = {
            "run_ids": list(run_ids),
            "runs": [],
        }

        for run_id in run_ids:
            run_dir = self.runs_dir / run_id
            summary_file = run_dir / "summary.json"
            metrics_file = run_dir / "metrics.json"
            metadata_file = run_dir / "metadata.json"

            if not summary_file.exists() or not metrics_file.exists():
                raise FileNotFoundError(
                    f"Missing summary.json or metrics.json for run '{run_id}'."
                )

            summary = _read_json(summary_file)
            metrics = _read_json(metrics_file)
            metadata = _read_json(metadata_file) if metadata_file.exists() else {}

            comparison["runs"].append(
                {
                    "run_id": run_id,
                    "summary": summary,
                    "metrics": metrics,
                    "metadata": metadata,
                }
            )

        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with self.output_file.open("w", encoding="utf-8") as handle:
            json.dump(comparison, handle, indent=2, ensure_ascii=False)

        return 0

