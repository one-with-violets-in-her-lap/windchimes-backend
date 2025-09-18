from typing import Optional
import strawberry

from windchimes.api.reusable_schemas.errors import (
    ForbiddenErrorGraphQL,
    GraphQLApiError,
)
from windchimes.api.reusable_schemas.playlists import (
    ExternalPlaylistToReadGraphQL,
)
from windchimes.api.strawberry_graphql_setup.auth import (
    AuthorizedOnlyExtension,
)
from windchimes.api.utils.graphql import GraphQLRequestInfo


async def _get_external_playlist_linked_for_sync(
    info: GraphQLRequestInfo, playlist_id: int
) -> GraphQLApiError | Optional[ExternalPlaylistToReadGraphQL]:
    tracks_sync_service = info.context["tracks_sync_service"]
    playlist_access_management_service = info.context[
        "playlists_access_management_service"
    ]

    playlist_access_check_result = (
        await playlist_access_management_service.check_if_user_owns_the_playlists(
            [playlist_id]
        )
    )

    if not playlist_access_check_result.user_owns_all_playlists:
        return ForbiddenErrorGraphQL()

    external_playlist = await tracks_sync_service.get_external_playlist_linked(
        playlist_id
    )

    if external_playlist is None:
        return None

    return ExternalPlaylistToReadGraphQL(
        **external_playlist.model_dump(
            exclude={
                "external_platform_id",
                "track_references",
                "publicly_available",
                "soundcloud_secret_token",
            }
        )
    )


external_playlist_linked_query = strawberry.field(
    resolver=_get_external_playlist_linked_for_sync,
    extensions=[AuthorizedOnlyExtension()],
)
