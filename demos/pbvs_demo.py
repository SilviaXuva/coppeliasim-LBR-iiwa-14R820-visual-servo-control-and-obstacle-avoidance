"""
Position-Based Visual Servoing (PBVS) Demo.

This demo illustrates the use of the PBVS controller to compute movement 
references from estimated target and camera states.
"""

from __future__ import annotations

import numpy as np

from manipulator_framework.core.visual_servoing.pbvs_controller import PBVSController
from manipulator_framework.core.types import Pose3D, CameraFrame

def main():
    print("--- PBVS Demo ---")
    
    # Define a target pose relative to the world
    target_pose = Pose3D(
        position=np.array([0.5, 0.0, 0.2]),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
        frame_id="world"
    )

    # Define the current camera pose in the world
    camera_pose = Pose3D(
        position=np.array([0.0, 0.0, 0.0]),
        orientation_quat_xyzw=np.array([0.0, 0.0, 0.0, 1.0]),
        frame_id="world"
    )

    # Initialize the PBVS controller
    # Gain lambda=1.0 by default
    controller = PBVSController(gain=1.0)

    print(f"Target Pose: {target_pose.position}")
    print(f"Camera Pose: {camera_pose.position}")

    # Compute move reference (velocity twist)
    twist = controller.compute_velocity_reference(
        camera_pose_world=camera_pose,
        target_pose_world=target_pose
    )

    print("-" * 20)
    print(f"Computed Twist (Camera Frame):")
    print(f"  Linear:  {twist.linear}")
    print(f"  Angular: {twist.angular}")
    print("-" * 20)
    print("Demo finished.")

if __name__ == "__main__":
    main()
