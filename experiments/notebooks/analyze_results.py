"""
Sample script to analyze experiment results.
Matches the logic that would be in a Jupyter notebook.
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def analyze_run(run_id: str, runs_root: str = "experiments/runs"):
    run_path = Path(runs_root) / run_id
    metrics_file = run_path / "metrics.json"
    
    if not metrics_file.exists():
        print(f"Metrics not found for {run_id}")
        return

    with open(metrics_file, "r") as f:
        data = json.load(f)
    
    # Simple plot of joint tracking error
    if "tracking_error" in data:
        errors = data["tracking_error"]
        plt.figure(figsize=(10, 6))
        plt.plot(errors)
        plt.title(f"Tracking Error - {run_id}")
        plt.xlabel("Step")
        plt.ylabel("Error [rad]")
        plt.grid(True)
        
        output_fig = Path("experiments/figures") / f"{run_id}_error.png"
        plt.savefig(output_fig)
        print(f"Saved figure to {output_fig}")

if __name__ == "__main__":
    # Example usage
    # analyze_run("sample_run_id")
    pass
