from typing import Any, Optional

from pydantic import BaseModel


class SoundcloudTrackTranscoding:
    class SoundcloudTrackFormat:
        protocol: str

    format: SoundcloudTrackFormat
    url: str


class SoundcloudTrackMediaInfo:
    transcodings: list[SoundcloudTrackTranscoding]


class SoundcloudTrack(BaseModel):
    id: int
    title: str
    artwork_url: Optional[str]
    created_at: str
    description: Optional[str]
    full_duration: int
    likes_count: Optional[int]
    permalink_url: str
    media: dict
    user: dict


class SoundcloudPlaylist(BaseModel):
    id: int
    title: str
    description: Optional[str]
    permalink: str
    permalink_url: str
    artwork_url: Optional[str]
    tracks: list[dict[str, Any]]
