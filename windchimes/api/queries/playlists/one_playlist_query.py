from typing import Optional, Sequence

import strawberry

from windchimes.api.reusable_schemas.errors import GraphQLApiError
from windchimes.api.reusable_schemas.playlists import (
    ExternalPlaylistReferenceGraphQL,
    PlaylistDetailedGraphQL,
)
from windchimes.api.reusable_schemas.track_reference import (
    TrackReferenceToReadGraphQL,
)
from windchimes.api.utils.graphql import (
    GraphQLRequestInfo,
)


@strawberry.type
class TrackOwnerGraphQL:
    name: str


@strawberry.type
class LoadedTrackGraphQL(TrackReferenceToReadGraphQL):
    name: str
    picture_url: Optional[str]
    description: Optional[str]
    seconds_duration: int
    likes_count: Optional[int]
    original_page_url: str = strawberry.field(
        description="""Track page on a platform from which the track was loaded

        Examples:
            Soundcloud track origin page url: `https://soundcloud.com/username/track`
            Youtube track origin page url: `https://youtube.com/watch?v=j4_0d7g2vb`
        """
    )
    audio_file_endpoint_url: Optional[str]
    owner: TrackOwnerGraphQL


@strawberry.type
class PlaylistDetailedWithLoadedTracksGraphQL(PlaylistDetailedGraphQL):
    loaded_tracks: list[Optional[LoadedTrackGraphQL]]


async def _get_one_playlist(
    info: GraphQLRequestInfo,
    playlist_id: int,
    tracks_to_load_ids: Optional[list[str]] = None,
    load_first_tracks: bool = False,
) -> Optional[PlaylistDetailedWithLoadedTracksGraphQL] | GraphQLApiError:
    tracks_service = info.context["tracks_service"]
    playlists_service = info.context["playlists_service"]
    playlists_access_management_service = info.context[
        "playlists_access_management_service"
    ]
    platform_aggregator_service = info.context["platform_aggregator_service"]

    playlist = await playlists_service.get_playlist_detailed(playlist_id)

    if playlist is None:
        return None

    current_user_can_view_playlist = (
        len(playlists_access_management_service.get_playlists_user_can_view([playlist]))
        > 0
    )
    if not current_user_can_view_playlist:
        return None

    external_playlist_to_sync_with = (
        ExternalPlaylistReferenceGraphQL(
            **playlist.external_playlist_to_sync_with.model_dump()
        )
        if playlist.external_playlist_to_sync_with is not None
        else None
    )

    if tracks_to_load_ids is None and not load_first_tracks:
        # TODO: refactor duplicate code when converting playlist pydantic model
        # to graphql
        return PlaylistDetailedWithLoadedTracksGraphQL(
            **playlist.model_dump(
                exclude={"track_references", "external_playlist_to_sync_with"}
            ),
            track_references=[
                TrackReferenceToReadGraphQL(**track_reference.model_dump())
                for track_reference in playlist.track_references
            ],
            loaded_tracks=[],
            external_playlist_to_sync_with=external_playlist_to_sync_with,
        )

    track_references_to_load: Sequence = tracks_service.get_track_references_to_load(
        playlist, tracks_to_load_ids, load_first_tracks
    )

    if None in track_references_to_load and tracks_to_load_ids is not None:
        not_found_track_reference_id = tracks_to_load_ids[
            track_references_to_load.index(None)
        ]

        return GraphQLApiError(
            name="playlist-track-not-found",
            technical_explanation="Track with id "
            + f"{not_found_track_reference_id} can't be found "
            + "in requested playlist",
            explanation="Failed to find some tracks in the playlist",
        )

    loaded_tracks = await platform_aggregator_service.load_tracks(
        list(track_references_to_load)
    )

    return PlaylistDetailedWithLoadedTracksGraphQL(
        **playlist.model_dump(
            exclude={"track_references", "external_playlist_to_sync_with"}
        ),
        track_references=[
            TrackReferenceToReadGraphQL(**track_reference.model_dump())
            for track_reference in playlist.track_references
        ],
        loaded_tracks=[
            (
                LoadedTrackGraphQL(
                    **track.model_dump(exclude={"owner": True}),
                    owner=TrackOwnerGraphQL(**track.owner.model_dump()),
                )
                if track is not None
                else None
            )
            for track in loaded_tracks
        ],
        external_playlist_to_sync_with=external_playlist_to_sync_with,
    )


playlist_query = strawberry.field(
    resolver=_get_one_playlist,
    description="""
        Get a single playlist with a maximum of 30 loaded tracks from
        external platforms

        Args:
            playlist_id: id of a playlist to retrieve
            tracks_to_load_ids: ids of tracks which data to load from external platforms
                API. **Prioritized over** `load_first_tracks` flag param
            load_first_tracks: include first tracks in a portion
    """,
)
