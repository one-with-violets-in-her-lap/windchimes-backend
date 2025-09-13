from pydantic import ValidationError
import strawberry

from windchimes_backend.core.models.platform import Platform
from windchimes_backend.core.models.user import User
from windchimes_backend.core.services.external_platform_import.tracks_import import (
    PlaylistToImport,
)
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
) -> PlaylistImportResult | ValidationErrorGraphQL | GraphQLApiError:
    try:
        validated_playlist_to_import_from = PlaylistToImport.model_validate(
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

    if is_playlist_owned_by_user == False:
        return ForbiddenErrorGraphQL()

    tracks_import_service = info.context.tracks_import_service

    imported_track_references = await tracks_import_service.import_playlist_tracks(
        validated_playlist_to_import_from,
        playlist_to_import_to_id,
        replace_existing_tracks,
    )

    return PlaylistImportResult(
        imported_tracks=[
            TrackReferenceToReadGraphQL(**track_reference.model_dump())
            for track_reference in imported_track_references
        ]
    )


import_external_playlist_tracks_mutation = strawberry.mutation(
    resolver=_import_external_playlist_tracks, extensions=[AuthorizedOnlyExtension()]
)
