from math import e
from pydantic import ValidationError
import strawberry

from windchimes_backend.core.errors.external_platform_import import (
    ExternalPlaylistNotFoundError,
)
from windchimes_backend.core.models.platform import Platform
from windchimes_backend.core.models.playlist import ExternalPlaylistReference
from windchimes_backend.graphql_api.reusable_schemas.errors import (
    ForbiddenErrorGraphQL,
    GraphQLApiError,
    ValidationErrorGraphQL,
)
from windchimes_backend.graphql_api.reusable_schemas.playlists import (
    ExternalPlaylistToReadGraphQL,
)
from windchimes_backend.graphql_api.strawberry_graphql_setup.auth import (
    AuthorizedOnlyExtension,
)
from windchimes_backend.graphql_api.utils.graphql import GraphQLRequestInfo


@strawberry.type
class ExternalPlaylistNotFoundErrorGraphQL(GraphQLApiError):
    def __init__(self):
        super().__init__(
            name="external-playlist-not-found-error",
            explanation="Failed to find the playlist you want to sync, perhaps the "
            + "url you specified is invalid",
            technical_explanation="Failed to retrieve external playlist data from "
            + "specified url and platform",
        )


@strawberry.type
class SetPlaylistForTracksSyncMutationResult:
    external_playlist_linked: ExternalPlaylistToReadGraphQL


async def _set_playlist_for_tracks_sync(
    info: GraphQLRequestInfo,
    playlist_to_link_to_id: int,
    external_playlist_platform: Platform,
    external_playlist_url: str,
) -> (
    SetPlaylistForTracksSyncMutationResult
    | ValidationErrorGraphQL
    | GraphQLApiError
    | ExternalPlaylistNotFoundErrorGraphQL
):
    tracks_sync_service = info.context.tracks_sync_service
    playlist_access_management_service = (
        info.context.playlists_access_management_service
    )

    try:
        external_playlist_reference = ExternalPlaylistReference.model_validate(
            {"platform": external_playlist_platform, "url": external_playlist_url}
        )
    except ValidationError as validation_error:
        return ValidationErrorGraphQL.create_from_pydantic_validation_error(
            validation_error
        )

    user_owns_the_playlist = (
        await playlist_access_management_service.check_if_user_owns_the_playlists(
            [playlist_to_link_to_id]
        )
    )

    if not user_owns_the_playlist:
        return ForbiddenErrorGraphQL()

    try:
        external_playlist_linked = (
            await tracks_sync_service.link_external_playlist_for_sync(
                playlist_to_link_to_id, external_playlist_reference
            )
        )

        return SetPlaylistForTracksSyncMutationResult(
            external_playlist_linked=ExternalPlaylistToReadGraphQL(
                **external_playlist_linked.model_dump(
                    exclude={"external_platform_id", "track_references"}
                )
            )
        )
    except ExternalPlaylistNotFoundError:
        return ExternalPlaylistNotFoundErrorGraphQL()


set_playlist_for_tracks_sync_mutation = strawberry.mutation(
    resolver=_set_playlist_for_tracks_sync,
    extensions=[AuthorizedOnlyExtension()],
)


async def _disable_tracks_sync(
    info: GraphQLRequestInfo, playlist_id: int
) -> None | ValidationErrorGraphQL | GraphQLApiError:
    tracks_sync_service = info.context.tracks_sync_service
    playlist_access_management_service = (
        info.context.playlists_access_management_service
    )

    user_owns_the_playlist = (
        await playlist_access_management_service.check_if_user_owns_the_playlists(
            [playlist_id]
        )
    )

    if not user_owns_the_playlist:
        return ForbiddenErrorGraphQL()

    await tracks_sync_service.disable_external_playlist_sync(playlist_id)


disable_playlist_sync_mutation = strawberry.mutation(
    resolver=_disable_tracks_sync,
    extensions=[AuthorizedOnlyExtension()],
)


async def _sync_playlist_tracks_with_external_playlist(
    info: GraphQLRequestInfo, playlist_id: int
):
    playlist_access_management_service = (
        info.context.playlists_access_management_service
    )

    user_owns_the_playlist = (
        await playlist_access_management_service.check_if_user_owns_the_playlists(
            [playlist_id]
        )
    )

    if not user_owns_the_playlist:
        return ForbiddenErrorGraphQL()

    return
