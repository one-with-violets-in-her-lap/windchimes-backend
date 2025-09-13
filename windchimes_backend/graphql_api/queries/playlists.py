from datetime import datetime
from typing import Optional

import strawberry

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


async def get_playlists(info: GraphQLRequestInfo):
    playlists_service = info.context.playlists_service
    return await playlists_service.get_playlists()


playlists_query = strawberry.field(
    resolver=get_playlists, graphql_type=list[PlaylistToRead]
)
