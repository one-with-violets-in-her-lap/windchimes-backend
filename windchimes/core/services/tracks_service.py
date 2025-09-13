from typing import Optional, Sequence

from windchimes.core.constants.external_api_usage_limits import (
    MAXIMUM_TRACKS_TO_LOAD_PER_REQUEST,
)
from windchimes.core.database import Database
from windchimes.core.models.platform import Platform
from windchimes.core.models.track import TrackReferenceSchema
from windchimes.core.services.external_platforms.platform_aggregator import (
    PlatformAggregatorService,
)
from windchimes.core.services.playlists import (
    PlaylistDetailed,
)
from windchimes.common.utils.lists import find_item


class TracksService:
    def __init__(
        self, database: Database, platform_aggregator_service: PlatformAggregatorService
    ):
        self.platform_aggregator_service = platform_aggregator_service
        self.database = database

    def get_track_references_to_load(
        self,
        playlist: PlaylistDetailed,
        track_references_ids_to_load: Optional[list[str]] = None,
        load_first_tracks=False,
    ) -> Sequence[Optional[TrackReferenceSchema]]:
        """
        Gets a portion of tracks references from a playlist for further loading from
        external APIs

        What tracks have to be included in a portion can be controlled
        with `tracks_to_load_ids` or `load_first_tracks` parameters

        Args:
            playlist: Playlist from which to read tracks references from
            tracks_to_load_ids: Tracks references ids to include in a portion,
                **prioritized over** `load_first_tracks` flag param
            load_first_tracks: Include first tracks in a portion

        Raises:
            ValueError: `tracks_to_load_ids` exceeds the maximum length (30)

        Returns:
            A list of tracks references from a playlist for further loading from
                external APIs. Returns empty list if neither the `load_first_tracks` mode
                or `tracks_to_load_ids` is specified
        """

        if track_references_ids_to_load is not None:
            if len(track_references_ids_to_load) > MAXIMUM_TRACKS_TO_LOAD_PER_REQUEST:
                raise ValueError(
                    "Cannot retrieve more than "
                    + f"{MAXIMUM_TRACKS_TO_LOAD_PER_REQUEST} tracks"
                )

            return [
                find_item(
                    playlist.track_references,
                    lambda some_track_reference: some_track_reference.id
                    == track_reference_id,
                )
                for track_reference_id in track_references_ids_to_load
            ]
        elif load_first_tracks:
            return playlist.track_references[0:MAXIMUM_TRACKS_TO_LOAD_PER_REQUEST]
        else:
            return []

    async def get_track_audio_file_url(
        self,
        platform_id: str,
        platform: Platform,
        audio_file_endpoint_url: Optional[str],
    ):
        return await self.platform_aggregator_service.get_track_audio_file_url(
            platform_id, platform, audio_file_endpoint_url
        )
