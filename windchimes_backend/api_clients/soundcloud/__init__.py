from functools import reduce
import logging

import aiohttp

from windchimes_backend.core.config import app_config
from windchimes_backend.api_clients.platform_api_error import PlatformApiError
from windchimes_backend.api_clients.soundcloud.models import (
    SoundcloudPlaylist,
    SoundcloudTrack,
)
from windchimes_backend.utils.lists import set_items_order


_SOUNDCLOUD_API_BASE_URL = "https://api-v2.soundcloud.com"
_NO_REDIRECT_ERROR_MESSAGE = (
    '"on.soundcloud.com/..." url has not been redirected. '
    + "Cannot get playlist data without original url"
)


logger = logging.getLogger(__name__)


class SoundcloudApiClient:
    def __init__(self, client_id: str):
        """
        Creates soundcloud api client object for interacting
        with private SoundCloud API v2

        Args:
            client_id: API key to use for Soundcloud API access. Can be scraped
                from soundcloud website
        """

        self.client_id = client_id

    async def get_tracks_by_ids(self, ids: list[int]):
        """Fetches soundcloud tracks by list of ids

        Returns:
            list of tracks in soundcloud's format
        """

        async with aiohttp.ClientSession() as aiohttp_session:
            if len(ids) == 0:
                return []

            ids_as_strings = [str(track_id) for track_id in ids]
            comma_separated_ids = reduce(
                lambda result, id: f"{result},{id}", ids_as_strings
            )

            async with aiohttp_session.get(
                _SOUNDCLOUD_API_BASE_URL
                + f"/tracks?ids={comma_separated_ids}"
                + f"&client_id={self.client_id}"
            ) as response:
                return set_items_order(
                    [
                        SoundcloudTrack(**track_dict)
                        for track_dict in await response.json()
                    ],
                    ids,
                    lambda track: track.id,
                )

    async def get_format_data(self, format_url: str) -> dict[str, str]:
        """
        Retrieves audio file url of the format from specified url

        Will try to bypass geo restrictions and paywall in the future
        """

        async with aiohttp.ClientSession() as aiohttp_session:
            async with aiohttp_session.get(
                format_url, params={"client_id": self.client_id}
            ) as format_data_response:
                format_data = await format_data_response.json()
                return format_data

    async def get_playlist_by_url(self, url: str):
        """Fetches playlist data, supports `on.soundcloud.com/..` shortened links

        Raises:
            PlatformApiError: if soundcloud api returned an error
        """

        async with aiohttp.ClientSession() as aiohttp_session:
            if "on.soundcloud.com" in url:
                async with aiohttp_session.get(url, allow_redirects=False) as response:
                    redirect_url = response.headers.get("Location")
                    if redirect_url is None:
                        logger.error(_NO_REDIRECT_ERROR_MESSAGE)
                        raise PlatformApiError(_NO_REDIRECT_ERROR_MESSAGE)

                    url = str(redirect_url)

            async with aiohttp_session.get(
                f"{_SOUNDCLOUD_API_BASE_URL}/resolve?url={url}"
                + f"&client_id={self.client_id}",
            ) as response:
                if not response.ok:
                    raise PlatformApiError(
                        "Error occurred on soundcloud api request "
                        + f"with status code {response.status}"
                    )

                response_data = await response.json()

                if response_data["kind"] != "playlist":
                    return None

                return SoundcloudPlaylist(**response_data)

    async def search_playlists(self, search_query: str):
        """searches playlists by provided search query

        Returns: maximum of 100 playlists matching the search query
        """

        async with aiohttp.ClientSession(
            base_url=_SOUNDCLOUD_API_BASE_URL
        ) as aiohttp_session:
            async with aiohttp_session.get(
                f"/search/playlists_without_albums?q={search_query}"
                + f"&client_id={self.client_id}&limit=100&offset=0"
            ) as response:
                if not response.ok:
                    raise PlatformApiError(
                        "Error occurred on soundcloud api request "
                        + f"with status code {response.status}"
                    )

                response_data: dict = await response.json()

                return [
                    SoundcloudPlaylist(**playlist_dict)
                    for playlist_dict in response_data["collection"]
                ]
