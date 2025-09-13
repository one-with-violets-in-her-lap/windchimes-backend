from typing import Optional

import strawberry

from windchimes_backend.core.constants.external_api_usage_limits import (
    MAXIMUM_TRACKS_TO_LOAD_PER_REQUEST,
)
from windchimes_backend.core.models.track import TrackReferenceSchema
from windchimes_backend.graphql_api.queries.playlists.one_playlist_query import (
    LoadedTrackGraphQL,
    TrackOwnerGraphQL,
)
from windchimes_backend.graphql_api.reusable_schemas.errors import GraphQLApiError
from windchimes_backend.graphql_api.reusable_schemas.track_reference import (
    TrackReferenceToReadGraphQL,
)
from windchimes_backend.graphql_api.utils.graphql import GraphQLRequestInfo


@strawberry.input
class TrackReferenceToLoadGraphQL(TrackReferenceToReadGraphQL):
    pass


@strawberry.type
class LoadedTracksWrapper:
    items: list[Optional[LoadedTrackGraphQL]]


async def _get_loaded_tracks(
    info: GraphQLRequestInfo, track_references: list[TrackReferenceToLoadGraphQL]
) -> LoadedTracksWrapper | GraphQLApiError:
    platform_aggregator_service = info.context.platform_aggregator_service

    if len(track_references) > MAXIMUM_TRACKS_TO_LOAD_PER_REQUEST:
        return GraphQLApiError(
            name="too-many-tracks-to-load-error",
            technical_explanation=f"Cannot load more than {MAXIMUM_TRACKS_TO_LOAD_PER_REQUEST}"
            + "tracks at once",
        )

    loaded_tracks = await platform_aggregator_service.load_tracks(
        [
            TrackReferenceSchema(**vars(track_reference))
            for track_reference in track_references
        ]
    )

    # TODO: move to a utility converter function
    # (loaded track pydantic -> loaded track strawberry graphql object)
    loaded_tracks_to_return_in_graphql = [
        (
            LoadedTrackGraphQL(
                **track.model_dump(exclude={"owner"}),
                owner=TrackOwnerGraphQL(**track.owner.model_dump()),
            )
            if track is not None
            else None
        )
        for track in loaded_tracks
    ]

    return LoadedTracksWrapper(items=loaded_tracks_to_return_in_graphql)


loaded_tracks_query = strawberry.field(resolver=_get_loaded_tracks)
