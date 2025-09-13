from pydantic import ValidationError
import strawberry

from windchimes_backend.core.models.platform import Platform
from windchimes_backend.core.services.other_platform_import.tracks_import import (
    PlaylistToImport,
)
from windchimes_backend.graphql_api.reusable_schemas.errors import (
    GraphQLApiError,
    UnauthorizedErrorGraphQL,
    ValidationErrorGraphQL,
)
from windchimes_backend.graphql_api.utils.graphql import (
    GraphQLRequestInfo,
)


@strawberry.input
class PlaylistToImportFromGraphQL:
    platform: Platform
    url: str


async def _import_external_playlist_tracks(
    info: GraphQLRequestInfo,
    playlist_to_import_from: PlaylistToImportFromGraphQL,
    playlist_to_import_to_id: int,
) -> None | ValidationErrorGraphQL | GraphQLApiError:
    try:
        validated_playlist_to_import_from = PlaylistToImport.model_validate(
            {**vars(playlist_to_import_from)}
        )
    except ValidationError as error:
        return ValidationErrorGraphQL.create_from_pydantic_validation_error(
            error, field_prefix="playlist_to_import_from"
        )
    
    current_user = info.context.current_user
    if current_user is None:
        return UnauthorizedErrorGraphQL()

    tracks_import_service = info.context.tracks_import_service
    return await tracks_import_service.import_playlist_tracks(
        validated_playlist_to_import_from, playlist_to_import_to_id
    )


import_external_playlist_tracks_mutation = strawberry.mutation(
    resolver=_import_external_playlist_tracks
)
