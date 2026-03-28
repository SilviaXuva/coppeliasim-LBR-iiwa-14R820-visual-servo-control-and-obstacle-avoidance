from __future__ import annotations

from manipulator_framework.adapters.simulation.coppeliasim.camera_adapter import CoppeliaSimCameraAdapter
from manipulator_framework.core.contracts import CameraInterface


def test_coppeliasim_camera_adapter_implements_camera_interface() -> None:
    adapter = CoppeliaSimCameraAdapter(
        sim_client=object(),
        camera_handle=object(),
    )

    assert isinstance(adapter, CameraInterface)
