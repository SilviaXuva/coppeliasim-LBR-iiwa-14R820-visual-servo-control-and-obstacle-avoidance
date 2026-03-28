from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from manipulator_framework.core.tracking.track_state import TrackState
from manipulator_framework.core.types import TrackedTarget


def _bbox_center_xy(detection) -> np.ndarray:
    x1, y1, x2, y2 = detection.bbox_xyxy
    return np.array([(x1 + x2) / 2.0, (y1 + y2) / 2.0], dtype=float)


@dataclass(frozen=True)
class AssociationMatch:
    track_index: int
    target_index: int
    distance: float


@dataclass
class NearestNeighborAssociation:
    """
    Minimal association policy based on 2D detection center distance.
    """
    max_distance: float = 80.0

    def match(
        self,
        tracks: list[TrackState],
        observations: list[TrackedTarget],
    ) -> tuple[list[AssociationMatch], list[int], list[int]]:
        matches: list[AssociationMatch] = []
        used_tracks: set[int] = set()
        used_targets: set[int] = set()

        for target_index, target in enumerate(observations):
            if target.latest_detection is None:
                continue

            best_track_index: int | None = None
            best_distance = float("inf")
            target_center = _bbox_center_xy(target.latest_detection)

            for track_index, track in enumerate(tracks):
                if track_index in used_tracks:
                    continue
                if track.latest_detection is None:
                    continue
                if track.target_type != target.target_type:
                    continue

                track_center = _bbox_center_xy(track.latest_detection)
                distance = float(np.linalg.norm(target_center - track_center))

                if distance < best_distance and distance <= self.max_distance:
                    best_distance = distance
                    best_track_index = track_index

            if best_track_index is not None:
                matches.append(
                    AssociationMatch(
                        track_index=best_track_index,
                        target_index=target_index,
                        distance=best_distance,
                    )
                )
                used_tracks.add(best_track_index)
                used_targets.add(target_index)

        unmatched_tracks = [i for i in range(len(tracks)) if i not in used_tracks]
        unmatched_targets = [i for i in range(len(observations)) if i not in used_targets]

        return matches, unmatched_tracks, unmatched_targets
