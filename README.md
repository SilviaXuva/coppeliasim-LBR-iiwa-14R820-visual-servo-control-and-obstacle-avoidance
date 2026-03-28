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
