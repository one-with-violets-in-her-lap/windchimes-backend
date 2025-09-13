from pydantic import ValidationError
import strawberry

from windchimes_backend.core.services.playlists import (
    TrackToDeleteFromPlaylists,
    TracksToAddToPlaylistsWrapper,
)
from windchimes_backend.api.mutations.playlists import TrackToAddGraphQL
from windchimes_backend.api.reusable_schemas.errors import (
    ForbiddenErrorGraphQL,
    GraphQLApiError,
    UnauthorizedErrorGraphQL,
    ValidationErrorGraphQL,
)
from windchimes_backend.api.strawberry_graphql_setup.auth import (
    AuthorizedOnlyExtension,
)
from windchimes_backend.api.utils.dictionaries import convert_to_dictionary
from windchimes_backend.api.utils.graphql import (
    GraphQLRequestInfo,
)


@strawberry.type
class DeleteTrackFromPlaylistsResponse:
    updated_playlists_ids: list[int]


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

    access_check_result = (
        await playlists_access_management_service.check_if_user_owns_the_playlists(
            playlists_ids_to_update
        )
    )
    if not access_check_result.user_owns_all_playlists:
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


async def _delete_track_from_playlists(
    info: GraphQLRequestInfo, track_id: str, playlists_ids: list[int]
) -> DeleteTrackFromPlaylistsResponse | ValidationErrorGraphQL | GraphQLApiError:
    playlists_access_management_service = (
        info.context.playlists_access_management_service
    )
    playlists_service = info.context.playlists_service

    try:
        track_to_delete = TrackToDeleteFromPlaylists.model_validate(
            {"track_id": track_id, "playlists_ids": playlists_ids}
        )
    except ValidationError as error:
        return ValidationErrorGraphQL.create_from_pydantic_validation_error(error)

    access_check_result = (
        await playlists_access_management_service.check_if_user_owns_the_playlists(
            playlists_ids
        )
    )
    if not access_check_result.user_owns_all_playlists:
        return ForbiddenErrorGraphQL(
            explanation="You don't have access to playlists you want to delete "
            + "tracks from",
            technical_explanation="You don't have access to some playlists "
            + "you want to delete tracks from",
        )

    update_playlists_ids = await playlists_service.delete_track_from_playlists(
        track_to_delete
    )

    return DeleteTrackFromPlaylistsResponse(updated_playlists_ids=update_playlists_ids)


delete_track_from_playlists_mutation = strawberry.mutation(
    resolver=_delete_track_from_playlists,
    extensions=[AuthorizedOnlyExtension()],
    description="""
    Deletes track from playlists with specified ids (`track_to_delete_from_playlist.playlists_ids` param)

    Returns:
        Ids of the playlists from which the track was deleted
    """,
)
