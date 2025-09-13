import logging
from typing import Optional

import httpx


_YOUTUBE_WEBSITE_BASE_URL = "https://www.youtube.com"
_YOUTUBE_INTERNAL_API_BASE_URL = f"{_YOUTUBE_WEBSITE_BASE_URL}/youtubei/v1"

logger = logging.getLogger(__name__)


class YoutubeInternalApiError(Exception):
    def __init__(
        self, status_code: Optional[int] = None, more_info: Optional[str] = None
    ):
        message = "Youtube internal API call failed"

        if status_code:
            message += f". Status code: {status_code}"

        if more_info is not None:
            message += f". More info: {more_info}"

        super().__init__(message)


class YoutubeInternalApiClient:
    def __init__(self, socks_proxy_url: Optional[str] = None):
        self.socks_proxy_url = socks_proxy_url

    async def search_videos_and_get_ids(self, search_query: str) -> list[str]:
        """Searches videos using internal youtube API

        Returns:
            List of ids of the videos found
        """

        body = {
            "context": {
                "client": {
                    "hl": "en",
                    "gl": "AU",
                    "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    + "(KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36,gzip(gfe)",
                    "clientName": "WEB",
                    "clientVersion": "2.20250205.01.00",
                    "osName": "X11",
                    "osVersion": "",
                    "platform": "DESKTOP",
                    "clientFormFactor": "UNKNOWN_FORM_FACTOR",
                    "userInterfaceTheme": "USER_INTERFACE_THEME_LIGHT",
                    "browserName": "Chrome",
                    "browserVersion": "132.0.0.0",
                    "screenWidthPoints": 1699,
                    "screenHeightPoints": 450,
                    "screenPixelDensity": 1,
                    "screenDensityFloat": 1,
                },
            },
            "query": search_query,
        }

        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://www.youtube.com",
            "priority": "u=1, i",
            "referer": f"{_YOUTUBE_WEBSITE_BASE_URL}/results?search_query={search_query}",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            + "(KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        }

        try:
            async with httpx.AsyncClient(
                proxy=self.socks_proxy_url, base_url=_YOUTUBE_INTERNAL_API_BASE_URL
            ) as httpx_client:
                response = await httpx_client.post(
                    url="/search?prettyPrint=false",
                    headers=headers,
                    json=body,
                    timeout=10,
                )

                response.raise_for_status()

                data = response.json()

                renderers = data["contents"]["twoColumnSearchResultsRenderer"][
                    "primaryContents"
                ]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"][
                    "contents"
                ]

                return [
                    renderer["videoRenderer"]["videoId"]
                    for renderer in renderers
                    if "videoRenderer" in renderer
                ]
        except httpx.HTTPStatusError as http_status_error:
            raise YoutubeInternalApiError(
                status_code=http_status_error.response.status_code,
                more_info=http_status_error.response.text,
            ) from http_status_error
        except httpx.HTTPError as http_error:
            raise YoutubeInternalApiError(more_info=str(http_error)) from http_error
