from typing import Optional

import strawberry

from windchimes.api.queries.playlists.one_playlist_query import (
    LoadedTrackGraphQL,
)
from windchimes.api.reusable_schemas.track_reference import (
    TrackReferenceToReadGraphQL,
)


@strawberry.input
class TrackReferenceToLoadGraphQL(TrackReferenceToReadGraphQL):
    pass


@strawberry.type
class LoadedTracksWrapper:
    items: list[Optional[LoadedTrackGraphQL]]


@strawberry.input(
    description="Input type that defines what tracks to load. **At least "
    + "one field must be specified**"
)
class LoadedTracksFilter:
    """Input type that defines what tracks to load

    **At least one field must be specified**
    """

    track_references_to_load: Optional[list[TrackReferenceToLoadGraphQL]] = (
        strawberry.field(
            description="When specified, app returns each loaded track for each "
            + "specified track reference (track reference is combination of id and "
            + "platform to identify the track). Prioritized over `search_query` field",
            default=None,
        )
    )

    search_query: Optional[str] = None
