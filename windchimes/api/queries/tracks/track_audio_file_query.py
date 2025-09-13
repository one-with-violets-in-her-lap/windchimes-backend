from typing import Optional
import urllib.parse

import strawberry
import urllib

from windchimes.core.config import app_config
from windchimes.core.models.platform import Platform
from windchimes.api.reusable_schemas.errors import GraphQLApiError
from windchimes.api.utils.graphql import GraphQLRequestInfo
from windchimes.api.audio_proxy import audio_proxy_router


PLATFORMS_TO_PROXY = [Platform.YOUTUBE]
"""Platforms that don't support CORS requests, so a CORS proxy is needed"""


@strawberry.type
class TrackAudioFileGraphQL:
    url: str


async def _get_track_audio_file(
    info: GraphQLRequestInfo,
    platform: Platform,
    platform_id: str,
    audio_file_endpoint_url: Optional[str] = None,
) -> Optional[TrackAudioFileGraphQL] | GraphQLApiError:
    tracks_service = info.context.tracks_service

    audio_file_url = await tracks_service.get_track_audio_file_url(
        platform_id,
        platform,
        audio_file_endpoint_url,
    )

    if audio_file_url is None:
        return None

    if platform in PLATFORMS_TO_PROXY:
        print(audio_proxy_router.prefix)
        audio_file_url = (
            f"{str(app_config.api.public_base_url).rstrip('/')}{audio_proxy_router.prefix}"
            + f"?url={urllib.parse.quote(audio_file_url)}"
        )

    return TrackAudioFileGraphQL(url=audio_file_url)


track_audio_file_query = strawberry.field(
    resolver=_get_track_audio_file,
    description="Retrieves mp3 audio file of specified track. Returns `null` if track "
    + "is not found",
)
