from windchimes_backend.core.database.models.base import BaseDatabaseModel
from windchimes_backend.core.database.models.track_reference import TrackReference
from windchimes_backend.core.database.models.playlist import Playlist


__all__ = ["BaseDatabaseModel", "TrackReference", "Playlist"]

database_models = [TrackReference, Playlist]
