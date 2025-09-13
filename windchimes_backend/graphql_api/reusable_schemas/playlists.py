from datetime import datetime
from typing import Optional

import strawberry

from windchimes_backend.core.models.platform import Platform
from windchimes_backend.graphql_api.reusable_schemas.track_reference import (
    TrackReferenceToReadGraphQL,
)


@strawberry.type
class ExternalPlaylistToReadGraphQL:
    name: str
    description: Optional[str]
    picture_url: Optional[str]
    original_page_url: str


@strawberry.type
class ExternalPlaylistReferenceGraphQL:
    id: int
    last_sync_at: datetime
    platform: Platform
    platform_id: str


@strawberry.type
class PlaylistToReadGraphQL:
    id: int
    created_at: datetime
    name: str
    description: Optional[str]
    picture_url: Optional[str]
    owner_user_id: str
    publicly_available: bool

    track_count: int


@strawberry.type
class PlaylistDetailedGraphQL(PlaylistToReadGraphQL):
    track_references: list[TrackReferenceToReadGraphQL]
    external_playlist_to_sync_with: Optional[ExternalPlaylistReferenceGraphQL]
