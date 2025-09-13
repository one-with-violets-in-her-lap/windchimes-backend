from pydantic import BaseModel

from typing import Literal, Optional


class YoutubeVideoSnippet(BaseModel):
    title: str
    published_at: str
    description: Optional[str]
    thumbnails: dict[str, dict]
    channel_title: str


class YoutubeVideoContentDetails(BaseModel):
    duration: str
    """Video duration in html datetime attribute format, example: `PT15H10M`"""


class YoutubeVideo(BaseModel):
    id: str
    snippet: YoutubeVideoSnippet
    content_details: YoutubeVideoContentDetails


class YoutubePlaylistSnippet(BaseModel):
    published_at: str
    title: str
    description: Optional[str]
    thumbnails: dict[str, dict]


class YoutubePlaylist(BaseModel):
    id: str
    snippet: YoutubePlaylistSnippet


class YoutubePlaylistVideoContentDetails(BaseModel):
    video_id: str


class YoutubePlaylistVideo(BaseModel):
    content_details: YoutubePlaylistVideoContentDetails
