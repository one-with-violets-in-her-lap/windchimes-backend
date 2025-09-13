from typing import Optional

from pydantic import BaseModel

from windchimes_backend.core.models.platform import Platform


class TrackReferenceSchema(BaseModel):
    id: int
    platform: Platform
    platform_id: str


class LoadedTrack(TrackReferenceSchema):
    class TrackOwner(BaseModel):
        name: str

    id: int
    platform_id: str
    platform: Platform

    name: str
    picture_url: Optional[str]
    description: Optional[str]
    seconds_duration: int
    likes_count: Optional[int]

    audio_file_endpoint_url: Optional[str]

    owner: TrackOwner
