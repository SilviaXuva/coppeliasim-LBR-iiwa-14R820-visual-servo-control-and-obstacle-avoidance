"""
Target Tracking (Nearest Neighbor) Demo.

This demo demonstrates how to use the NearestNeighborTracker to maintain 
temporal target identities from frame-by-frame 2D or 3D detections.
"""

from __future__ import annotations

import numpy as np

from manipulator_framework.core.tracking.nearest_neighbor_tracker import NearestNeighborTracker
from manipulator_framework.core.types import Detection2D, TrackedTarget
from manipulator_framework.core.types.enums import TargetType, TrackingStatus

def main():
    print("--- Tracking Demo ---")
    
    # Initialize the tracker
    # distance_threshold=50.0 (pixels), max_missed_steps=3
    tracker = NearestNeighborTracker(distance_threshold=50.0, max_missed_steps=3)

    # Frame 1: Detection at (10, 10)
    det1 = Detection2D(
        bbox_xyxy=(10.0, 10.0, 20.0, 20.0),
        confidence=0.9,
        class_id=0,
        class_name="person",
        image_size_wh=(640, 480),
        timestamp=0.0
    )

    print("\nFrame 1: Processing detection at (10, 10)")
    tracks = tracker.update(detections=[det1], timestamp=0.0)
    for track in tracks:
         print(f"  Track ID: {track.target_id}, Status: {track.status.name}, BBox: {track.latest_detection.bbox_xyxy}")

    # Frame 2: Move detection slightly to (12, 12)
    det2 = Detection2D(
        bbox_xyxy=(12.0, 12.0, 22.0, 22.0),
        confidence=0.9,
        class_id=0,
        class_name="person",
        image_size_wh=(640, 480),
        timestamp=0.1
    )

    print("\nFrame 2: Processing detection at (12, 12)")
    tracks = tracker.update(detections=[det2], timestamp=0.1)
    for track in tracks:
         print(f"  Track ID: {track.target_id}, Status: {track.status.name}, BBox: {track.latest_detection.bbox_xyxy}")

    # Frame 3: Missing detection (missed step)
    print("\nFrame 3: No detections")
    tracks = tracker.update(detections=[], timestamp=0.2)
    for track in tracks:
         print(f"  Track ID: {track.target_id}, Status: {track.status.name}, Missed Steps: {track.missed_steps}")

    print("\nDemo finished.")

if __name__ == "__main__":
    main()
