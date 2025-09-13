from pydantic import ValidationError
import strawberry

from windchimes_backend.core.services.playlists import (
    TracksToAddToPlaylistsWrapper,
)
from windchimes_backend.graphql_api.mutations.playlists import TrackToAddGraphQL
from windchimes_backend.graphql_api.reusable_schemas.errors import (
    ForbiddenErrorGraphQL,
    GraphQLApiError,
    UnauthorizedErrorGraphQL,
    ValidationErrorGraphQL,
)
from windchimes_backend.graphql_api.utils.dictionaries import convert_to_dictionary
from windchimes_backend.graphql_api.utils.graphql import (
    GraphQLRequestInfo,
)


async def _add_tracks_to_playlists(
    info: GraphQLRequestInfo, tracks: list[TrackToAddGraphQL]
) -> None | ValidationErrorGraphQL | GraphQLApiError:
    if len(tracks) == 0:
        return GraphQLApiError(
            name="empty-playlist-tracks-list-specified-error",
            explanation="You must specify what tracks to add to a playlist",
            technical_explanation="`tracks` param must not be empty",
        )

    current_user = info.context.current_user
    playlists_service = info.context.playlists_service
    playlists_access_management_service = (
        info.context.playlists_access_management_service
    )

    if current_user is None:
        return UnauthorizedErrorGraphQL()

    try:
        validated_tracks = TracksToAddToPlaylistsWrapper.model_validate(
            {"tracks": convert_to_dictionary(tracks)}
        )
    except ValidationError as error:
        return ValidationErrorGraphQL.create_from_pydantic_validation_error(error)

    playlists_ids_to_update = []
    for track in tracks:
        playlists_ids_to_update.extend(track.playlists_ids_to_add_to)

    user_owns_all_playlists = (
        await playlists_access_management_service.check_if_user_owns_the_playlists(
            playlists_ids_to_update
        )
    )
    if not user_owns_all_playlists:
        return ForbiddenErrorGraphQL(
            explanation="You don't have access to playlists you want to add "
            + "tracks to",
            technical_explanation="You don't have access to some playlists "
            + "you want to add tracks to",
        )

    await playlists_service.add_tracks_to_playlists(validated_tracks)


add_tracks_to_playlists_mutation = strawberry.mutation(
    resolver=_add_tracks_to_playlists,
)
