from datetime import datetime
from typing import Optional

import strawberry

from windchimes_backend.core.services.playlists import (
    FailedToDeletePlaylistError,
    PlaylistToCreate,
)
from windchimes_backend.graphql_api.reusable_schemas.errors import (
    GraphQLApiError,
    UnauthorizedErrorGraphQL,
)
from windchimes_backend.graphql_api.reusable_schemas.playlists import (
    PlaylistToReadGraphQL,
    PlaylistToReadWithTracksGraphQL,
)
from windchimes_backend.graphql_api.utils.dataclasses import convert_to_dataclass
from windchimes_backend.graphql_api.utils.graphql import (
    GraphQLRequestInfo,
)


@strawberry.input
class PlaylistToCreateGraphQL:
    name: str
    slug: str
    description: Optional[str] = None
    picture_url: Optional[str] = None


async def create_playlist(
    info: GraphQLRequestInfo, playlist: PlaylistToCreateGraphQL
) -> PlaylistToReadWithTracksGraphQL | UnauthorizedErrorGraphQL:
    playlists_service = info.context.playlists_service
    current_user = info.context.current_user

    if current_user is None:
        return UnauthorizedErrorGraphQL()

    created_playlist = await playlists_service.create_playlist(
        PlaylistToCreate(**vars(playlist), owner_user_id=current_user.sub)
    )

    return convert_to_dataclass(vars(created_playlist), PlaylistToReadWithTracksGraphQL)


create_playlist_mutation = strawberry.mutation(
    resolver=create_playlist,
)


async def delete_playlist(
    info: GraphQLRequestInfo, playlist_to_delete_id: int
) -> None | GraphQLApiError:
    playlists_service = info.context.playlists_service
    current_user = info.context.current_user

    if current_user is None:
        return UnauthorizedErrorGraphQL()

    try:
        await playlists_service.delete_playlist(playlist_to_delete_id, current_user.sub)
    except FailedToDeletePlaylistError as error:
        return GraphQLApiError(
            name="playlist-deletion-failed-error",
            explanation="Playlist couldn't be deleted because it doesn't exist or you don't have access to it",
            technical_explanation=str(error),
        )


delete_playlist_mutation = strawberry.mutation(
    resolver=delete_playlist,
)
