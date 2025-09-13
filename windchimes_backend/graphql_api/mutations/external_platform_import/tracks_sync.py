from pydantic import ValidationError
import strawberry

from windchimes_backend.core.errors.external_platform_import import (
    ExternalPlaylistNotFoundError,
)
from windchimes_backend.core.models.platform import Platform
from windchimes_backend.core.models.external_playlist import ExternalPlaylistToLink
from windchimes_backend.core.services.external_platform_import.tracks_sync import (
    ExternalPlaylistNotLinkedError,
)
from windchimes_backend.graphql_api.reusable_schemas.errors import (
    ForbiddenErrorGraphQL,
    GraphQLApiError,
    NotFoundErrorGraphQL,
    ValidationErrorGraphQL,
)
from windchimes_backend.graphql_api.reusable_schemas.playlists import (
    ExternalPlaylistToReadGraphQL,
)
from windchimes_backend.graphql_api.reusable_schemas.track_reference import (
    TrackReferenceToReadGraphQL,
)
from windchimes_backend.graphql_api.strawberry_graphql_setup.auth import (
    AuthorizedOnlyExtension,
)
from windchimes_backend.graphql_api.utils.graphql import GraphQLRequestInfo


@strawberry.type
class ExternalPlaylistNotAvailableErrorGraphQL(GraphQLApiError):
    def __init__(self):
        super().__init__(
            name="external-playlist-not-available-error",
            explanation="Playlist to sync with is not available",
            technical_explanation="Failed to retrieve external playlist data, "
            + "perhaps it's not available anymore",
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
    | ExternalPlaylistNotAvailableErrorGraphQL
):
    tracks_sync_service = info.context.tracks_sync_service
    playlist_access_management_service = (
        info.context.playlists_access_management_service
    )

    try:
        external_playlist_reference = ExternalPlaylistToLink.model_validate(
            {"platform": external_playlist_platform, "url": external_playlist_url}
        )
    except ValidationError as validation_error:
        return ValidationErrorGraphQL.create_from_pydantic_validation_error(
            validation_error
        )

    access_check_result = (
        await playlist_access_management_service.check_if_user_owns_the_playlists(
            [playlist_to_link_to_id]
        )
    )

    if not access_check_result.user_owns_all_playlists:
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
                    exclude={
                        "external_platform_id",
                        "track_references",
                        "publicly_available",
                        "soundcloud_secret_token",
                    }
                )
            )
        )
    except ExternalPlaylistNotFoundError:
        return ExternalPlaylistNotAvailableErrorGraphQL()


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

    access_check_result = (
        await playlist_access_management_service.check_if_user_owns_the_playlists(
            [playlist_id]
        )
    )

    if not access_check_result.user_owns_all_playlists:
        return ForbiddenErrorGraphQL()

    await tracks_sync_service.disable_external_playlist_sync(playlist_id)


disable_playlist_sync_mutation = strawberry.mutation(
    resolver=_disable_tracks_sync,
    extensions=[AuthorizedOnlyExtension()],
)


@strawberry.type
class TracksSyncResult:
    updated_track_references: list[TrackReferenceToReadGraphQL]


async def _sync_playlist_tracks_with_external_playlist(
    info: GraphQLRequestInfo, playlist_id: int
) -> (
    TracksSyncResult
    | NotFoundErrorGraphQL
    | GraphQLApiError
    | ExternalPlaylistNotAvailableErrorGraphQL
):
    playlist_access_management_service = (
        info.context.playlists_access_management_service
    )
    tracks_sync_service = info.context.tracks_sync_service

    access_check_result = (
        await playlist_access_management_service.check_if_user_owns_the_playlists(
            [playlist_id]
        )
    )

    if (
        not access_check_result.user_owns_all_playlists
        or access_check_result.loaded_playlists is None
        or len(access_check_result.loaded_playlists) == 0
    ):
        return ForbiddenErrorGraphQL()

    try:
        updated_track_list = await tracks_sync_service.sync_playlist_tracks(
            access_check_result.loaded_playlists[0]
        )

        return TracksSyncResult(
            updated_track_references=[
                TrackReferenceToReadGraphQL(**track_reference.model_dump())
                for track_reference in updated_track_list
            ]
        )
    except (ExternalPlaylistNotFoundError, ExternalPlaylistNotLinkedError):
        return ExternalPlaylistNotAvailableErrorGraphQL()


sync_playlist_tracks_with_external_playlist_mutation = strawberry.mutation(
    resolver=_sync_playlist_tracks_with_external_playlist,
    description="Replaces playlist tracks with tracks from external playlist linked "
    + "to it via `set_playlist_for_tracks_sync_mutation` mutation. Returns list "
    + "of updated playlist tracks",
    extensions=[AuthorizedOnlyExtension()],
)
