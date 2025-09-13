from typing import Optional

import strawberry

from windchimes_backend.core.services.playlists import PlaylistsFilters
from windchimes_backend.graphql_api.reusable_schemas.playlists import (
    PlaylistToReadGraphQL,
)
from windchimes_backend.graphql_api.utils.graphql import (
    GraphQLRequestInfo,
)


@strawberry.input
class PlaylistsFiltersGraphQL:
    owner_user_id: Optional[str] = strawberry.field(
        description="If specified, only playlists owned by user with specified id "
        + "are returned",
        default=None,
    )

    exclude_owner_user_id: Optional[str] = strawberry.field(
        description="If specified, playlists owned by user with specified id are "
        + "excluded from the output",
        default=None,
    )

    containing_track_reference_id: Optional[str] = strawberry.field(
        description="If specified, ONLY the playlists that contain track reference with "
        + "specified id are included in the output",
        default=None,
    )

    exclude_containing_track_reference_id: Optional[str] = strawberry.field(
        description="If specified, playlists that contain track reference with "
        + "specified id are excluded from the output",
        default=None,
    )


async def _get_playlists(info: GraphQLRequestInfo, filters: PlaylistsFiltersGraphQL):
    playlists_service = info.context.playlists_service
    return await playlists_service.get_playlists(PlaylistsFilters(**vars(filters)))


playlists_query = strawberry.field(
    resolver=_get_playlists, graphql_type=list[PlaylistToReadGraphQL]
)
