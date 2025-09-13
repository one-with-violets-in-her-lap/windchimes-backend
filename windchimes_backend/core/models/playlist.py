from typing import Optional

from pydantic import BaseModel

from windchimes_backend.core.models.track import TrackReferenceSchema


class PlaylistToCreate(BaseModel):
    name: str
    description: Optional[str]
    public: bool
    picture_url: Optional[str]


class PlaylistToCreateWithTracks(PlaylistToCreate):
    track_references: list[TrackReferenceSchema]
