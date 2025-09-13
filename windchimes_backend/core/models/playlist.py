from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from windchimes_backend.core.models.track import TrackReferenceSchema


class PlaylistToCreate(BaseModel):
    name: str
    description: Optional[str]
    picture_url: Optional[str]


class PlaylistToCreateWithTracks(PlaylistToCreate):
    track_references: list[TrackReferenceSchema]


class PlaylistSchema(BaseModel):
    id: int
    created_at: datetime

    name: str
    description: Optional[str]
    picture_url: Optional[str]

    owner_user_id: str

    track_references: list[TrackReferenceSchema]
