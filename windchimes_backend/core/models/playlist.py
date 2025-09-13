from typing import Optional

from pydantic import BaseModel

from windchimes_backend.core.models.track import TrackReferenceSchema


class PlaylistToCreate(BaseModel):
    name: str
    description: Optional[str] = None
    publicly_available: bool
    picture_url: Optional[str] = None


class PlaylistToCreateWithTracks(PlaylistToCreate):
    track_references: list[TrackReferenceSchema]


class PlaylistToImport(BaseModel):
    name: str
    description: Optional[str]
    picture_url: Optional[str]
    publicly_available: bool
    track_references: list[TrackReferenceSchema]
