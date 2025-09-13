from datetime import datetime
from typing import Optional

import strawberry

from windchimes_backend.graphql_api.reusable_schemas.track_reference import (
    TrackReferenceToReadGraphQL,
)


@strawberry.type
class PlaylistToReadGraphQL:
    id: int
    created_at: datetime
    name: str
    description: Optional[str]
    picture_url: Optional[str]
    owner_user_id: str
    public: bool

    track_count: int


@strawberry.type
class PlaylistToReadWithTracksGraphQL(PlaylistToReadGraphQL):
    track_references: list[TrackReferenceToReadGraphQL]
