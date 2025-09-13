from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from windchimes.core.models.external_playlist import (
    ExternalPlaylistReferenceSchema,
)
from windchimes.core.models.track import TrackReferenceSchema


class PlaylistToCreate(BaseModel):
    name: str
    description: Optional[str] = None
    publicly_available: bool
    picture_url: Optional[str] = None


class PlaylistToCreateWithTracks(PlaylistToCreate):
    track_references: list[TrackReferenceSchema]


class PlaylistToImport(BaseModel):
    external_platform_id: str
    name: str
    description: Optional[str]
    picture_url: Optional[str]
    publicly_available: bool
    track_references: list[TrackReferenceSchema]


class PlaylistToRead(BaseModel):
    id: int
    created_at: datetime
    name: str
    description: Optional[str]
    picture_url: Optional[str]

    publicly_available: bool
    owner_user_id: str


class PlaylistToReadWithTrackCount(PlaylistToRead):
    track_count: int


class PlaylistDetailed(PlaylistToReadWithTrackCount):
    track_references: list[TrackReferenceSchema]
    external_playlist_to_sync_with: Optional[ExternalPlaylistReferenceSchema] = None
