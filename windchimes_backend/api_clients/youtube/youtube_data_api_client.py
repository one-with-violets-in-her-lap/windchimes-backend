from functools import reduce
from typing import Optional

import aiohttp
from pydantic import BaseModel

from windchimes_backend.api_clients.platform_api_error import PlatformApiError
from windchimes_backend.api_clients.youtube.models import (
    YoutubePlaylist,
    YoutubePlaylistVideo,
    YoutubeVideo,
)
from windchimes_backend.utils.dictionaries import convert_keys_to_snake_case


MAX_YOUTUBE_TRACKS_PER_REQUEST = 50

_YOUTUBE_DATA_API_BASE_URL = "https://www.googleapis.com"


class YoutubePageInfo(BaseModel):
    total_results: int


class YoutubePlaylistVideosResult(BaseModel):
    items: list[YoutubePlaylistVideo]
    next_page_token: Optional[str] = None
    page_info: YoutubePageInfo


class YoutubeDataApiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_videos_by_ids(self, ids: list[str]) -> list[Optional[YoutubeVideo]]:
        if len(ids) == 0:
            return []

        comma_separated_ids = reduce(lambda result, id: f"{result},{id}", ids)

        async with aiohttp.ClientSession(
            base_url=_YOUTUBE_DATA_API_BASE_URL
        ) as aiohttp_session:
            async with aiohttp_session.get(
                f"/youtube/v3/videos?id={comma_separated_ids}"
                + f"&key={self.api_key}&part=snippet,contentDetails"
            ) as response:
                raw_videos = (await response.json())["items"]

                return [
                    YoutubeVideo(**convert_keys_to_snake_case(raw_video))
                    for raw_video in raw_videos
                ]

    async def get_playlist_by_id(self, playlist_id: str):
        async with aiohttp.ClientSession(
            base_url=_YOUTUBE_DATA_API_BASE_URL
        ) as aiohttp_session:
            async with aiohttp_session.get(
                f"/youtube/v3/playlists?id={playlist_id}"
                + f"&key={self.api_key}&part=snippet,contentDetails,id"
            ) as response:
                raw_playlists = (await response.json())["items"]

                if len(raw_playlists) == 0:
                    return None

                return YoutubePlaylist(**convert_keys_to_snake_case(raw_playlists[0]))

    async def get_playlist_videos_portion(
        self, playlist_id: str, next_page_token: Optional[str] = None
    ) -> YoutubePlaylistVideosResult:
        """fetches 50 videos (first 50 by default) from a playlist

        Args:
            next_page_token: token that can be used to fetch another portion of
                tracks. can be obtained after request of the first portion
        """

        query_params = {
            "playlistId": playlist_id,
            "key": self.api_key,
            "part": "snippet,contentDetails",
            "maxResults": MAX_YOUTUBE_TRACKS_PER_REQUEST,
        }
        if next_page_token is not None:
            query_params["page_token"] = next_page_token

        async with aiohttp.ClientSession(
            base_url=_YOUTUBE_DATA_API_BASE_URL
        ) as aiohttp_session:
            async with aiohttp_session.get(
                "/youtube/v3/playlistItems",
                params=query_params,
            ) as response:
                if not response.ok:
                    raise PlatformApiError(
                        "Error occurred on youtube api request "
                        + f"with status code {response.status}"
                    )

                response_data = convert_keys_to_snake_case(await response.json())
                response_data["items"] = [
                    YoutubePlaylistVideo(**video_dict)
                    for video_dict in response_data["items"]
                ]

                return YoutubePlaylistVideosResult(**response_data)
