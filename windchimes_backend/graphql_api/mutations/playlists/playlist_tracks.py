import strawberry

from windchimes_backend.core.services.playlists import (
    PlaylistsFilters,
    TrackToAddToPlaylists,
)
from windchimes_backend.graphql_api.mutations.playlists import TrackToAddGraphQL
from windchimes_backend.graphql_api.reusable_schemas.errors import (
    ForbiddenErrorGraphQL,
    GraphQLApiError,
    UnauthorizedErrorGraphQL,
)
from windchimes_backend.graphql_api.utils.graphql import (
    GraphQLRequestInfo,
)


async def __add_tracks_to_playlists(
    info: GraphQLRequestInfo, tracks: list[TrackToAddGraphQL]
) -> None | GraphQLApiError:
    if len(tracks) == 0:
        return GraphQLApiError(
            name="empty-playlist-tracks-list-specified-error",
            explanation="You must specify what tracks to add to a playlist",
            technical_explanation="`tracks` param must not be empty",
        )

    playlists_service = info.context.playlists_service
    current_user = info.context.current_user

    if current_user is None:
        return UnauthorizedErrorGraphQL()

    playlists_ids_to_update = []
    for track in tracks:
        playlists_ids_to_update.extend(track.playlists_ids_to_add_to)

    playlists_to_update = await playlists_service.get_playlists(
        PlaylistsFilters(ids=playlists_ids_to_update)
    )

    for playlist_to_update in playlists_to_update:
        if playlist_to_update.owner_user_id != current_user.sub:
            return ForbiddenErrorGraphQL(
                explanation="You don't have access to playlists you want to add tracks to",
                technical_explanation="You don't have access to some playlists you want to add tracks to",
            )

    await playlists_service.add_tracks_to_playlists(
        [TrackToAddToPlaylists.model_validate(vars(track)) for track in tracks]
    )


add_tracks_to_playlists_mutation = strawberry.mutation(
    resolver=__add_tracks_to_playlists,
)
