from __future__ import annotations

from dataclasses import dataclass, field

from manipulator_framework.core.contracts import TrackerInterface
from manipulator_framework.core.tracking.association import NearestNeighborAssociation
from manipulator_framework.core.tracking.lifecycle import TrackLifecyclePolicy
from manipulator_framework.core.tracking.prediction import ConstantPositionPredictor
from manipulator_framework.core.tracking.track_state import TrackState
from manipulator_framework.core.tracking.update import TrackUpdater
from manipulator_framework.core.types import TrackedTarget


@dataclass
class NearestNeighborTracker(TrackerInterface):
    """
    Pure tracking subsystem with nearest-neighbor association.
    """
    association: NearestNeighborAssociation = field(default_factory=NearestNeighborAssociation)
    predictor: ConstantPositionPredictor = field(default_factory=ConstantPositionPredictor)
    updater: TrackUpdater = field(default_factory=TrackUpdater)
    lifecycle: TrackLifecyclePolicy = field(default_factory=TrackLifecyclePolicy)
    _tracks: list[TrackState] = field(default_factory=list, init=False, repr=False)
    _next_track_index: int = field(default=0, init=False, repr=False)

    def update(self, observations: list[TrackedTarget], timestamp: float) -> list[TrackedTarget]:
        for track in self._tracks:
            self.predictor.predict(track, timestamp)

        matches, unmatched_tracks, unmatched_targets = self.association.match(self._tracks, observations)

        for match in matches:
            track = self._tracks[match.track_index]
            observation = observations[match.target_index]
            self.updater.update(track, observation)

        for track_index in unmatched_tracks:
            self.lifecycle.mark_missed(self._tracks[track_index], timestamp)

        for target_index in unmatched_targets:
            new_track_id = f"track_{self._next_track_index:04d}"
            self._next_track_index += 1
            new_track = self.lifecycle.create_track(new_track_id, observations[target_index])
            self._tracks.append(new_track)

        self._tracks = [track for track in self._tracks if not self.lifecycle.is_dead(track)]

        return [track.to_tracked_target() for track in self._tracks]

    def reset(self) -> None:
        self._tracks.clear()
        self._next_track_index = 0
