from calendar import c
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl

from windchimes_backend.core.models.platform import Platform
from windchimes_backend.core.models.track import TrackReferenceSchema


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


class ExternalPlaylistToLink(BaseModel):
    platform: Platform
    url: HttpUrl


class ExternalPlaylistReferenceSchema(BaseModel):
    id: int
    platform: Platform
    platform_id: str


class ExternalPlaylistToSyncWith(PlaylistToImport):
    original_page_url: str
    """Playlist page on a platform the playlist is hosted on

    Examples:
        - Soundcloud playlist original page url: `https://soundcloud.com/username/sets/playlist`
        - Youtube playlist original page url:
        `https://www.youtube.com/playlist?list=PLFV2KydlgVPrzJLyCYHLiDE38Z4tconON`
    """


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
    external_playlist_to_sync_with: Optional[ExternalPlaylistReferenceSchema]
