from windchimes.core.database.models.base import BaseDatabaseModel
from windchimes.core.database.models.track_reference import TrackReference
from windchimes.core.database.models.playlist import Playlist


__all__ = ["BaseDatabaseModel", "TrackReference", "Playlist"]

database_models = [TrackReference, Playlist]
