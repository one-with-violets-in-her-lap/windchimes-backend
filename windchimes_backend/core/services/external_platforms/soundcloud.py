import logging

from windchimes_backend.external_api_clients.platform_api_error import PlatformApiError
from windchimes_backend.external_api_clients.soundcloud import SoundcloudApiClient
from windchimes_backend.external_api_clients.soundcloud.models import SoundcloudTrack
from windchimes_backend.core.errors.external_platforms import (
    ExternalPlatformAudioFetchingError,
)
from windchimes_backend.core.models.platform_specific_params import (
    PlatformSpecificParams,
)
from windchimes_backend.core.models.platform import Platform
from windchimes_backend.core.models.external_playlist import (
    ExternalPlaylistInfo,
)
from windchimes_backend.core.models.track import LoadedTrack, TrackReferenceSchema
from windchimes_backend.core.services.external_platforms import ExternalPlatformService


logger = logging.getLogger()


class SoundcloudService(ExternalPlatformService):
    def __init__(self, soundcloud_api_client: SoundcloudApiClient):
        self.soundcloud_api_client = soundcloud_api_client

    async def load_tracks(self, tracks_to_load):
        tracks_ids = [track.id for track in tracks_to_load]
        platform_ids = [int(track.platform_id) for track in tracks_to_load]

        soundcloud_tracks = await self.soundcloud_api_client.get_tracks_by_ids(
            platform_ids
        )

        return [
            (
                self._convert_to_multi_platform_track(track, tracks_ids[index])
                if track is not None
                else None
            )
            for index, track in enumerate(soundcloud_tracks)
        ]

    async def get_track_audio_file_url(
        self, track_platform_id, audio_file_endpoint_url
    ):
        suitable_format_url = audio_file_endpoint_url

        if suitable_format_url is None:
            found_tracks = await self.soundcloud_api_client.get_tracks_by_ids(
                [int(track_platform_id)]
            )

            if len(found_tracks) == 0:
                return None

            track = found_tracks[0]

            if track is None:
                return None

            suitable_format_url = self._get_suitable_format_url(
                track.media["transcodings"]
            )

        format_data = await self.soundcloud_api_client.get_format_data(
            suitable_format_url
        )

        if "url" not in format_data:
            raise ExternalPlatformAudioFetchingError(
                "Couldn't find suitable format for Soundcloud track"
            )

        return format_data["url"]

    async def get_playlist_by_url(self, url: str):
        try:
            soundcloud_playlist = await self.soundcloud_api_client.get_playlist_by_url(
                url
            )
            if soundcloud_playlist is None:
                return None
        except PlatformApiError as error:
            logger.error(str(error))
            return None

        return ExternalPlaylistInfo(
            external_platform_id=str(soundcloud_playlist.id),
            name=soundcloud_playlist.title,
            description=soundcloud_playlist.description,
            picture_url=soundcloud_playlist.artwork_url,
            track_references=[
                TrackReferenceSchema(
                    id=f'{Platform.SOUNDCLOUD.value}/{track["id"]}',
                    platform_id=str(track["id"]),
                    platform=Platform.SOUNDCLOUD,
                )
                for track in soundcloud_playlist.tracks
            ],
            original_page_url=soundcloud_playlist.permalink_url,
            soundcloud_secret_token=soundcloud_playlist.secret_token,
        )

    async def get_playlist_by_id(
        self, playlist_id, platform_specific_params: PlatformSpecificParams
    ):
        try:
            soundcloud_playlist = await self.soundcloud_api_client.get_playlist_by_id(
                playlist_id,
                artwork_in_highest_quality=True,
                secret_token=platform_specific_params.soundcloud_secret_token,
            )

            if soundcloud_playlist is None:
                return None
        except PlatformApiError as error:
            logger.error(str(error))
            return None

        return ExternalPlaylistInfo(
            external_platform_id=str(soundcloud_playlist.id),
            name=soundcloud_playlist.title,
            description=soundcloud_playlist.description,
            picture_url=soundcloud_playlist.artwork_url,
            track_references=[
                TrackReferenceSchema(
                    id=f'{Platform.SOUNDCLOUD.value}/{track["id"]}',
                    platform_id=str(track["id"]),
                    platform=Platform.SOUNDCLOUD,
                )
                for track in soundcloud_playlist.tracks
            ],
            original_page_url=soundcloud_playlist.permalink_url,
        )

    async def search_tracks(self, search_query):
        tracks = await self.soundcloud_api_client.search_tracks(search_query)

        return [
            self._convert_to_multi_platform_track(
                track, f"{Platform.SOUNDCLOUD.value}/{track.id}"
            )
            for track in tracks
        ]

    def _get_suitable_format_url(self, track_transcodings: list[dict]):
        suitable_formats = [
            transcoding
            for transcoding in track_transcodings
            if transcoding["format"]["protocol"] == "hls"
        ]

        if len(suitable_formats) == 0:
            raise ExternalPlatformAudioFetchingError(
                "Couldn't find suitable format for Soundcloud track"
            )

        format_url = suitable_formats[0]["url"]
        return format_url.replace("/preview/", "/stream/")

    def _convert_to_multi_platform_track(
        self, resource_to_convert: SoundcloudTrack, track_id
    ):
        try:
            audio_file_endpoint_url = self._get_suitable_format_url(
                resource_to_convert.media["transcodings"]
            )
        except ExternalPlatformAudioFetchingError:
            audio_file_endpoint_url = None

        return LoadedTrack.model_validate(
            dict(
                id=track_id,
                platform_id=str(resource_to_convert.id),
                platform=Platform.SOUNDCLOUD,
                picture_url=resource_to_convert.artwork_url,
                seconds_duration=round(resource_to_convert.full_duration / 1000),
                likes_count=resource_to_convert.likes_count,
                description=resource_to_convert.description,
                name=resource_to_convert.title,
                audio_file_endpoint_url=audio_file_endpoint_url,
                original_page_url=resource_to_convert.permalink_url,
                owner={"name": resource_to_convert.user["username"]},
            )
        )
