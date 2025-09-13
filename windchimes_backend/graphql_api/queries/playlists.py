from datetime import datetime
from typing import Optional

import strawberry

from windchimes_backend.core.services.playlists import PlaylistsFilters
from windchimes_backend.graphql_api.reusable_schemas.track_reference import (
    TrackReferenceToRead,
)
from windchimes_backend.graphql_api.utils.graphql import (
    GraphQLRequestInfo,
)


@strawberry.type
class PlaylistToRead:
    id: int
    created_at: datetime
    name: str
    slug: str
    description: Optional[str]
    picture_url: Optional[str]
    owner_user_id: str

    track_count: int


@strawberry.type
class PlaylistToReadWithTracks(PlaylistToRead):
    track_references: list[TrackReferenceToRead]


@strawberry.input
class PlaylistsQueryFilters:
    owner_user_id: Optional[str] = strawberry.field(
        description="If specified, only playlists owned by user with specified id are returned",
        default=None,
    )

    exclude_owner_user_id: Optional[str] = strawberry.field(
        description="If specified, playlists owned by user with specified id are excluded from the output",
        default=None,
    )


async def get_playlists(info: GraphQLRequestInfo, filters: PlaylistsQueryFilters):
    playlists_service = info.context.playlists_service
    return await playlists_service.get_playlists(PlaylistsFilters(**vars(filters)))


playlists_query = strawberry.field(
    resolver=get_playlists, graphql_type=list[PlaylistToRead]
)


async def get_one_playlist(info: GraphQLRequestInfo, playlist_id: int):
    playlists_service = info.context.playlists_service
    return await playlists_service.get_playlist_with_track_references(playlist_id)


playlist_query = strawberry.field(
    resolver=get_one_playlist, graphql_type=PlaylistToReadWithTracks
)
