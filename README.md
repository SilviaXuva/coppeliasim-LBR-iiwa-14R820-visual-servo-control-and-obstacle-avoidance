# coppeliasim-LBR-iiwa-14R820-visual-servo-control-and-obstacle-avoidance
This repository contains a Python-based implementation of visual servo control for Collaborative Robotic Manipulator KUKA LBR iiwa 14R820 to perform pick-and-place tasks with obstacle avoidance, simulated in CoppeliaSim.

# Manipulator Framework

Scientific robotics framework for the Kuka LBR iiwa 14R820, designed for:

- robot modeling
- kinematics
- joint-space control
- visual servoing
- perception
- tracking
- obstacle avoidance
- reproducible experiments

## Architectural principles

- domain-centered core
- explicit application layer
- interface-based boundaries
- adapters for simulation, vision, ROS 2 and hardware
- ROS 2 only at the edge
- experiments are artifacts, not the architectural center

## Repository structure

- `src/manipulator_framework/core/`: domain and scientific logic
- `src/manipulator_framework/application/`: use cases and orchestration
- `src/manipulator_framework/adapters/`: concrete integrations
- `src/manipulator_framework/infrastructure/`: operational support
- `src/manipulator_framework/apps/`: executable entrypoints
- `tests/`: software validation
- `configs/`: versioned configuration
- `experiments/`: scientific runs and reports

## Installation profiles

### Base
Use when working only with the package core and infrastructure helpers:

```bash
pip install -e .
````

### Development

Use for local development, linting and test execution:

```bash
pip install -e ".[dev]"
```

### Robotics / kinematics

Use when running the kinematics layer backed by Robotics Toolbox and SpatialMath:

```bash
pip install -e ".[robotics]"
```

### Vision

Use when running ArUco / OpenCV adapters:

```bash
pip install -e ".[vision]"
```

### YOLO

Use when running Ultralytics-based detectors:

```bash
pip install -e ".[yolo]"
```

### Full local environment

Use when you want the broadest local setup for current simulation, vision and testing workflows:

```bash
pip install -e ".[full]"
```

## Notes about optional dependencies

* `PyYAML` is part of the base dependencies because configuration loading is used directly by the framework apps.
* `spatialmath-python` stays in the `robotics` extra together with `roboticstoolbox-python`, matching the current kinematics implementation.
* `opencv-contrib-python` is used instead of `opencv-python` because ArUco requires `cv2.aruco`.
* ROS 2 dependencies are intentionally **not** declared here as normal pip dependencies, because they are typically managed by the ROS 2 environment itself and must remain isolated at the framework edge.

## Current packaging limitation

The package metadata is now aligned with the code dependencies, but the current apps still resolve YAML files from the repository tree such as `configs/app/*.yaml`.

That means the cleanest supported workflow for now is:

* editable install
* execution from the repository root

Example:

```bash
pip install -e ".[full]"
python -m manipulator_framework.apps.simulation_app
```

Packaging config files as package resources can be treated later as an app/composition hardening step, but it is intentionally not mixed into this dependency correction stage.
