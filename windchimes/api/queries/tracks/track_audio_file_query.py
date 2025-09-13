from typing import Optional

import strawberry

from windchimes.core.models.platform import Platform
from windchimes.api.reusable_schemas.errors import GraphQLApiError
from windchimes.api.utils.graphql import GraphQLRequestInfo


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

    return TrackAudioFileGraphQL(url=audio_file_url)


track_audio_file_query = strawberry.field(
    resolver=_get_track_audio_file,
    description="Retrieves mp3 audio file of specified track. Returns `null` if track "
    + "is not found",
)
