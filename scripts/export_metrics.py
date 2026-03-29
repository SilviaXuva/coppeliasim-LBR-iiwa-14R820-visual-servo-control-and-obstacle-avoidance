from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def export_metrics(
    runs_dir: Path = Path("experiments/runs"),
    output_csv: Path = Path("experiments/reports/metrics_overview.csv"),
) -> int:
    rows: list[dict[str, Any]] = []

    if not runs_dir.exists():
        print(f"[WARN] Runs directory not found: {runs_dir}")
        return 1

    for run_dir in sorted(path for path in runs_dir.iterdir() if path.is_dir()):
        summary_file = run_dir / "summary.json"
        metrics_file = run_dir / "metrics.json"
        metadata_file = run_dir / "metadata.json"

        if not summary_file.exists() or not metrics_file.exists():
            continue

        summary = _read_json(summary_file)
        metrics = _read_json(metrics_file)
        metadata = _read_json(metadata_file) if metadata_file.exists() else {}

        scalar_metrics = metrics.get("scalar_metrics", [])
        metric_map = {
            entry.get("name", f"metric_{index}"): entry.get("value")
            for index, entry in enumerate(scalar_metrics)
            if isinstance(entry, dict)
        }

        row = {
            "run_id": summary.get("run_id", run_dir.name),
            "experiment_name": summary.get("experiment_name", ""),
            "scenario_name": summary.get("scenario_name", ""),
            "backend_name": summary.get("backend_name", ""),
            "success": summary.get("success", False),
            "duration": summary.get("duration", 0.0),
            "seed": metadata.get("seed", ""),
        }
        row.update(metric_map)
        rows.append(row)

    output_csv.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        print("[WARN] No run summaries with metrics were found.")
        return 1

    fieldnames: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"[OK] Metrics exported to {output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(export_metrics())
