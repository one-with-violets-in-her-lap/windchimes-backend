from pydantic import ValidationError
import strawberry

from windchimes_backend.core.models.platform import Platform
from windchimes_backend.core.models.playlist import ExternalPlaylistReference
from windchimes_backend.graphql_api.reusable_schemas.errors import (
    ForbiddenErrorGraphQL,
    GraphQLApiError,
    ValidationErrorGraphQL,
)
from windchimes_backend.graphql_api.reusable_schemas.track_reference import (
    TrackReferenceToReadGraphQL,
)
from windchimes_backend.graphql_api.strawberry_graphql_setup.auth import (
    AuthorizedOnlyExtension,
)
from windchimes_backend.graphql_api.utils.graphql import (
    GraphQLRequestInfo,
)


@strawberry.input
class PlaylistToImportFromGraphQL:
    platform: Platform
    url: str


@strawberry.type
class PlaylistImportResult:
    imported_tracks: list[TrackReferenceToReadGraphQL]


async def _import_external_playlist_tracks(
    info: GraphQLRequestInfo,
    playlist_to_import_from: PlaylistToImportFromGraphQL,
    playlist_to_import_to_id: int,
    replace_existing_tracks: bool = False,
) -> None | ValidationErrorGraphQL | GraphQLApiError:
    try:
        validated_playlist_to_import_from = ExternalPlaylistReference.model_validate(
            {**vars(playlist_to_import_from)}
        )
    except ValidationError as error:
        return ValidationErrorGraphQL.create_from_pydantic_validation_error(
            error, field_prefix="playlist_to_import_from"
        )

    playlists_access_management_service = (
        info.context.playlists_access_management_service
    )

    is_playlist_owned_by_user = (
        await playlists_access_management_service.check_if_user_owns_the_playlists(
            [playlist_to_import_to_id]
        )
    )

    if not is_playlist_owned_by_user:
        return ForbiddenErrorGraphQL()

    tracks_import_service = info.context.tracks_import_service

    await tracks_import_service.import_playlist_tracks(
        validated_playlist_to_import_from,
        playlist_to_import_to_id,
        replace_existing_tracks,
    )


import_external_playlist_tracks_mutation = strawberry.mutation(
    resolver=_import_external_playlist_tracks,
    extensions=[AuthorizedOnlyExtension()],
    description="Imports tracks from external platform playlist (Soundcloud/Youtube"
    + "/etc.) to a playlist in this app\n\nReturns nothing if tracks successfully "
    + "imported (will return the playlist in the future)",
)
