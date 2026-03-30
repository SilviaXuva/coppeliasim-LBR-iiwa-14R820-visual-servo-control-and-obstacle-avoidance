from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import shutil

import numpy as np

from manipulator_framework.application.composition.simulation_composer import SimulationComposer
from manipulator_framework.core.types import Detection2D, MarkerDetection, Pose3D


class FakeSimClient:
    def __init__(self) -> None:
        self._joint_values = {f"LBR_iiwa_14_R820_joint{i}": 0.0 for i in range(1, 8)}
        self._sim_time = 0.0

    def start_simulation(self) -> None:
        return None

    def step_simulation(self) -> None:
        self._sim_time += 0.05

    def stop_simulation(self) -> None:
        return None

    def get_joint_position(self, *, robot_handle, joint_name: str) -> float:
        return float(self._joint_values.get(joint_name, 0.0))

    def get_joint_velocity(self, *, robot_handle, joint_name: str) -> float:
        return 0.0

    def set_joint_target_position(self, *, robot_handle, joint_name: str, value: float) -> None:
        self._joint_values[joint_name] = float(value)

    def set_joint_torque(self, *, robot_handle, joint_name: str, value: float) -> None:
        return None

    def get_object_position(self, *, handle, reference_frame: str = "world") -> list[float]:
        return [0.5, 0.0, 0.6]

    def get_object_quaternion(self, *, handle, reference_frame: str = "world") -> list[float]:
        return [0.0, 0.0, 0.0, 1.0]

    def get_sim_time(self) -> float:
        return self._sim_time

    def get_camera_rgb(self, *, camera_handle) -> list[list[list[int]]]:
        return [[[0, 0, 0] for _ in range(32)] for _ in range(32)]

    def get_camera_intrinsics(self, *, camera_handle) -> list[list[float]]:
        return [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]


class _ControlledMarkerDetector:
    def detect_markers(self, frame) -> list[MarkerDetection]:
        return [
            MarkerDetection(
                marker_id=10,
                detection=Detection2D(
                    bbox_xyxy=(5.0, 5.0, 20.0, 20.0),
                    confidence=0.99,
                    class_id=10,
                    class_name="aruco",
                    image_size_wh=(32, 32),
                ),
            )
        ]


class _ControlledPoseEstimator:
    def estimate_marker_pose(self, detection: MarkerDetection) -> Pose3D:
        return Pose3D(
            position=np.array([0.5, 0.0, 0.6], dtype=float),
            orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0], dtype=float),
        )

    def estimate_person_target(self, detection):
        return None


class _NoOpPersonDetector:
    def detect_people(self, frame) -> list:
        return []


def test_pbvs_pipeline_runs(monkeypatch) -> None:
    tmp_dir = (Path.cwd() / "experiments" / "runs_e2e_test").resolve()
    shutil.rmtree(tmp_dir, ignore_errors=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "app": {"mode": "experiment", "use_case": "run_pbvs_with_avoidance"},
        "runtime": {"dt": 0.05, "max_steps": 20},
        "planning": {"duration": 1.0},
        "experiment": {"name": "pbvs_pipeline_e2e", "seed": 123},
        "results": {"base_dir": str(tmp_dir).replace("\\", "/")},
    }

    monkeypatch.setattr(
        "manipulator_framework.application.composition.simulation_composer.SimulationComposer.build_person_detector",
        lambda self: _NoOpPersonDetector(),
    )
    monkeypatch.setattr(
        "manipulator_framework.application.composition.simulation_composer.SimulationComposer.build_marker_detector",
        lambda self: _ControlledMarkerDetector(),
    )
    monkeypatch.setattr(
        "manipulator_framework.application.composition.simulation_composer.SimulationComposer.build_pose_estimator",
        lambda self, camera=None: _ControlledPoseEstimator(),
    )

    composer = SimulationComposer(config=config, sim_client=FakeSimClient())
    use_case = composer.build_run_visual_servo()
    request = composer.build_request_factory().build_experiment_request()
    request = replace(request, max_cycles=20, duration=1.0, seed=123)

    response = use_case.execute(request)

    assert response.run_result.success is True
    run_dir = tmp_dir / request.run_id
    assert (run_dir / "metrics.csv").exists()
    assert (run_dir / "summary.json").exists()
