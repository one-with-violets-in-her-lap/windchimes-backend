import random
from typing import Optional

from windchimes_backend.core.models.platform_specific_params import (
    PlatformSpecificParams,
)
from windchimes_backend.core.models.playlist import PlaylistToImport
from windchimes_backend.core.services.external_platforms import ExternalPlatformService
from windchimes_backend.utils.lists import set_items_order
from windchimes_backend.core.models.platform import Platform
from windchimes_backend.core.models.external_playlist import (
    ExternalPlaylistToSyncWith,
)
from windchimes_backend.core.models.track import LoadedTrack, TrackReferenceSchema
from windchimes_backend.core.services.external_platforms.soundcloud import (
    SoundcloudService,
)
from windchimes_backend.core.services.external_platforms.youtube_service import (
    YoutubeService,
)


class PlatformAggregatorService:
    """Service that aggregates tracks data from api of external platforms

    Uses its subclasses to communicate with external platforms:
        - `SoundcloudService`
        - `YoutubeService`
    """

    def __init__(
        self, soundcloud_service: SoundcloudService, youtube_service: YoutubeService
    ):
        self.platform_services: dict[Platform, ExternalPlatformService] = {
            Platform.SOUNDCLOUD: soundcloud_service,
            Platform.YOUTUBE: youtube_service,
        }

    async def load_tracks(self, tracks_to_load: list[TrackReferenceSchema]):
        # groups tracks by platform to query them from api in batches
        tracks_grouped_by_platform = {platform: [] for platform in Platform}
        for track_reference in tracks_to_load:
            tracks_grouped_by_platform[track_reference.platform].append(track_reference)

        loaded_tracks: list[Optional[LoadedTrack]] = []

        for platform in tracks_grouped_by_platform:
            platform_service = self.platform_services[platform]
            tracks_to_load_group = tracks_grouped_by_platform[platform]

            loaded_tracks.extend(
                await platform_service.load_tracks(tracks_to_load_group)
            )

        # restores the order
        return set_items_order(
            loaded_tracks,
            [track.id for track in tracks_to_load],
            lambda track: track.id if track is not None else None,
        )

    async def get_track_audio_file_url(
        self,
        track_platform_id: str,
        platform: Platform,
        audio_file_endpoint_url: Optional[str],
    ):
        return await self.platform_services[platform].get_track_audio_file_url(
            track_platform_id, audio_file_endpoint_url
        )

    async def get_playlist_by_url(
        self, platform: Platform, playlist_url: str
    ) -> Optional[ExternalPlaylistToSyncWith]:
        playlist = await self.platform_services[platform].get_playlist_by_url(
            playlist_url
        )

        return playlist

    async def get_playlist_by_id(
        self,
        platform: Platform,
        playlist_id: str,
        platform_specific_params: PlatformSpecificParams,
    ) -> Optional[ExternalPlaylistToSyncWith]:
        return await self.platform_services[platform].get_playlist_by_id(
            playlist_id, platform_specific_params
        )

    async def search_tracks(self, search_query: str) -> list[LoadedTrack]:
        tracks = []

        for _, platform_service in self.platform_services.items():
            tracks.extend(await platform_service.search_tracks(search_query))

        random.shuffle(tracks)
        return tracks
