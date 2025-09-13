from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl

from windchimes_backend.core.models.platform import Platform
from windchimes_backend.core.models.track import TrackReferenceSchema


class ExternalPlaylistToLink(BaseModel):
    platform: Platform
    url: HttpUrl


class ExternalPlaylistReferenceSchema(BaseModel):
    id: int
    last_sync_at: datetime
    platform: Platform
    platform_id: str


class ExternalPlaylistToSyncWith(BaseModel):
    external_platform_id: str
    name: str
    description: Optional[str]
    picture_url: Optional[str]

    track_references: list[TrackReferenceSchema]

    original_page_url: str
    """Playlist page on a platform the playlist is hosted on

    Examples:
        - Soundcloud playlist original page url: `https://soundcloud.com/username/sets/playlist`
        - Youtube playlist original page url:
        `https://www.youtube.com/playlist?list=PLFV2KydlgVPrzJLyCYHLiDE38Z4tconON`
    """
