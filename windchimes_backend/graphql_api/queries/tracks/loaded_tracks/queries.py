from typing import Optional, Sequence

import strawberry

from windchimes_backend.core.constants.external_api_usage_limits import (
    MAXIMUM_TRACKS_TO_LOAD_PER_REQUEST,
)
from windchimes_backend.core.models.track import LoadedTrack, TrackReferenceSchema
from windchimes_backend.graphql_api.queries.playlists.one_playlist_query import (
    LoadedTrackGraphQL,
    TrackOwnerGraphQL,
)
from windchimes_backend.graphql_api.queries.tracks.loaded_tracks.models import (
    LoadedTracksFilter,
    LoadedTracksWrapper,
    TrackReferenceToLoadGraphQL,
)
from windchimes_backend.graphql_api.reusable_schemas.errors import GraphQLApiError
from windchimes_backend.graphql_api.utils.graphql import GraphQLRequestInfo


async def _get_loaded_tracks(
    info: GraphQLRequestInfo, tracks_filter: LoadedTracksFilter
) -> LoadedTracksWrapper | GraphQLApiError:
    platform_aggregator_service = info.context.platform_aggregator_service

    loaded_tracks: Optional[Sequence[LoadedTrack | None]] = None

    if tracks_filter.track_references_to_load is not None:
        if (
            len(tracks_filter.track_references_to_load)
            > MAXIMUM_TRACKS_TO_LOAD_PER_REQUEST
        ):
            return GraphQLApiError(
                name="too-many-tracks-to-load-error",
                technical_explanation="Cannot load more than "
                + f"{MAXIMUM_TRACKS_TO_LOAD_PER_REQUEST} tracks at once",
            )

        loaded_tracks = await platform_aggregator_service.load_tracks(
            [
                TrackReferenceSchema(**vars(track_reference))
                for track_reference in tracks_filter.track_references_to_load
            ]
        )
    elif tracks_filter.search_query is not None:
        loaded_tracks = await platform_aggregator_service.search_tracks(
            tracks_filter.search_query
        )

    if loaded_tracks is None:
        return GraphQLApiError(
            name="no-filter-specified-error",
            technical_explanation="At least one field must be specified "
            + "in `filter` argument",
            explanation="No proper filter condition was specified",
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


async def _get_one_loaded_track(
    info: GraphQLRequestInfo, track_reference: TrackReferenceToLoadGraphQL
) -> Optional[LoadedTrackGraphQL]:
    platform_aggregator_service = info.context.platform_aggregator_service

    loaded_tracks = await platform_aggregator_service.load_tracks(
        [TrackReferenceSchema(**vars(track_reference))]
    )

    loaded_track = loaded_tracks[0]

    if loaded_track is None:
        return None

    return LoadedTrackGraphQL(
        **loaded_track.model_dump(exclude={"owner"}),
        owner=TrackOwnerGraphQL(**loaded_track.owner.model_dump()),
    )


one_loaded_track_query = strawberry.field(resolver=_get_one_loaded_track)
