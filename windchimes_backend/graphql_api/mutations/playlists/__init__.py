from typing import Optional

import strawberry

from windchimes_backend.core.services.playlists import (
    PlaylistDeleteOrUpdateFailed,
    PlaylistToCreate,
    PlaylistUpdate,
)
from windchimes_backend.graphql_api.reusable_schemas.errors import (
    GraphQLApiError,
    UnauthorizedErrorGraphQL,
)
from windchimes_backend.graphql_api.reusable_schemas.playlists import (
    PlaylistToReadWithTracksGraphQL,
)
from windchimes_backend.graphql_api.utils.dataclasses import convert_to_dataclass
from windchimes_backend.graphql_api.utils.graphql import (
    GraphQLRequestInfo,
)


@strawberry.input
class PlaylistToCreateGraphQL:
    name: str
    description: Optional[str] = None
    picture_url: Optional[str] = None
    public: bool = False


@strawberry.input
class PlaylistUpdateGraphQL:
    name: Optional[str] = None
    description: Optional[str] = None
    picture_url: Optional[str] = None
    public: Optional[bool] = None


@strawberry.input
class TrackToAddGraphQL:
    id: str
    playlists_ids_to_add_to: list[int]


async def _create_playlist(
    info: GraphQLRequestInfo, playlist: PlaylistToCreateGraphQL
) -> PlaylistToReadWithTracksGraphQL | UnauthorizedErrorGraphQL:
    playlists_service = info.context.playlists_service
    current_user = info.context.current_user

    if current_user is None:
        return UnauthorizedErrorGraphQL()

    created_playlist = await playlists_service.create_playlist(
        PlaylistToCreate(**vars(playlist)), owner_user_id=current_user.sub
    )

    return convert_to_dataclass(vars(created_playlist), PlaylistToReadWithTracksGraphQL)


create_playlist_mutation = strawberry.mutation(
    resolver=_create_playlist,
)


async def _delete_playlist(
    info: GraphQLRequestInfo, playlist_to_delete_id: int
) -> None | GraphQLApiError:
    playlists_service = info.context.playlists_service
    current_user = info.context.current_user

    if current_user is None:
        return UnauthorizedErrorGraphQL()

    try:
        await playlists_service.delete_playlist(playlist_to_delete_id, current_user.sub)
    except PlaylistDeleteOrUpdateFailed as error:
        return GraphQLApiError(
            name="playlist-deletion-failed-error",
            explanation="Playlist couldn't be deleted because it doesn't exist or "
            + "you don't have access to it",
            technical_explanation=str(error),
        )


delete_playlist_mutation = strawberry.mutation(
    resolver=_delete_playlist,
)


async def _update_playlist(
    info: GraphQLRequestInfo,
    playlist_to_update_id: int,
    playlist_data_to_update: PlaylistUpdateGraphQL,
) -> None | GraphQLApiError:
    playlists_service = info.context.playlists_service
    current_user = info.context.current_user

    if current_user is None:
        return UnauthorizedErrorGraphQL()

    try:
        await playlists_service.update_playlist(
            playlist_to_update_id,
            current_user.sub,
            PlaylistUpdate.model_validate(vars(playlist_data_to_update)),
        )
    except PlaylistDeleteOrUpdateFailed as error:
        return GraphQLApiError(
            name="playlist-update-failed-error",
            explanation="Playlist couldn't be updated because it doesn't "
            + "exist or you don't have access to it",
            technical_explanation=str(error),
        )


update_playlist_mutation = strawberry.mutation(
    resolver=_update_playlist,
)
