from typing import Optional

from pydantic import BaseModel

from windchimes_backend.core.models.platform import Platform


class TrackReferenceSchema(BaseModel):
    id: str
    platform: Platform
    platform_id: str


class LoadedTrack(TrackReferenceSchema):
    class TrackOwner(BaseModel):
        name: str

    name: str
    picture_url: Optional[str]
    description: Optional[str]
    seconds_duration: int
    likes_count: Optional[int]

    original_page_url: str
    """Track page on a platform from which the track was loaded

    Examples:
        Soundcloud track origin page url: `https://soundcloud.com/username/track`
        Youtube track origin page url: `https://youtube.com/watch?v=j4_0d7g2vb`
    """

    audio_file_endpoint_url: Optional[str]

    owner: TrackOwner
