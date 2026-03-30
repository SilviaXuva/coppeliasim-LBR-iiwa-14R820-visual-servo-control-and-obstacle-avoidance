# Experiments

This directory contains experimental artifacts, run results, and analytical tools external to the framework core.

## Structure

- `configs/`: Versioned experimental protocols and factor definitions.
- `scenarios/`: Versioned environment definitions (scenes, targets, obstacles).
- `runs/`: Persistence for all execution outputs, organized by `run_id`.
- `reports/`: Aggregated reports and performance summaries.
- `notebooks/`: Jupyter notebooks for exploratory data analysis and visualization.
- `figures/`: Exported plots, diagrams, and figures for papers/thesis.

## Core Rules

1. **Separation of Concerns**: This directory keeps external definitions and artifacts. The experimental logic (protocol, results model) remains in `src/manipulator_framework/core/experiments/`.
2. **Benchmark != Demo != Test**: Benchmarks are for scientific comparison, demos are for manual validation, and tests are for software correctness.
3. **Traceability**: Every run must persist in `experiments/runs/<run_id>/` with its configuration, metadata, and metric series.

## Maintenance Tools

The framework provides several CLI tools for experimental maintenance:

### Validate Configurations
Ensure your YAML protocols and scenarios are syntactically correct:
```bash
validate-configs
```

### Export Metrics
Consolidate metrics from multiple runs into CSV or Parquet for analysis:
```bash
export-metrics --run-dir experiments/runs --output experiments/reports/summary.csv
```

### Compare Runs
Perform a detailed comparison between specific experimental runs:
```bash
compare-runs run_baseline_pd run_adaptive_pd
```

### Run Base Protocol (Official)
Run the frozen base experiment protocol (3 repetitions with fixed seeds) and generate a comparison report:
```bash
run-base-protocol
```

---

## Sample Protocol
`experiments/configs/pbvs_with_avoidance_protocol.yaml`

```yaml
name: pbvs_with_avoidance_protocol
repetitions: 3
seeds: [2026, 2027, 2028]
compared_methods: [pbvs_with_avoidance_official]
app_config: configs/app/pbvs_official.yaml
metrics:
  - task_success
  - final_visual_error
  - minimum_clearance
  - convergence_time
  - num_cycles_total
  - valid_detection_rate
```
