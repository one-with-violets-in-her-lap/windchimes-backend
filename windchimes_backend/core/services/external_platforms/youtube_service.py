import logging
import re
import urllib.parse

from windchimes_backend.api_clients.youtube.models import YoutubeVideo
from windchimes_backend.api_clients.youtube.youtube_data_api_client import (
    MAX_YOUTUBE_TRACKS_PER_REQUEST,
    YoutubeDataApiClient,
)
from windchimes_backend.api_clients.youtube.youtube_downloader import YoutubeDownloader
from windchimes_backend.core.models.platform import Platform
from windchimes_backend.core.models.playlist import (
    PlaylistToCreateWithTracks,
)
from windchimes_backend.core.models.track import LoadedTrack, TrackReferenceSchema
from windchimes_backend.core.services.external_platforms import ExternalPlatformService
from windchimes_backend.core.services.external_platforms.no_suitable_format_error import (
    NoSuitableFormatError,
)


MAX_YOUTUBE_TRACKS_REQUESTS = 4


logger = logging.getLogger()


class YoutubeService(ExternalPlatformService):
    def __init__(
        self,
        youtube_data_api_client: YoutubeDataApiClient,
        downloader: YoutubeDownloader,
    ):
        # self._setup_proxy()
        self.client = youtube_data_api_client
        self.downloader = downloader

    async def load_tracks(self, tracks_to_load):
        tracks_ids = [track.id for track in tracks_to_load]
        platform_ids = [track.platform_id for track in tracks_to_load]

        youtube_tracks = await self.client.get_videos_by_ids(platform_ids)

        return [
            (
                self._convert_to_multi_platform_track(track, tracks_ids[index])
                if track is not None
                else None
            )
            for index, track in enumerate(youtube_tracks)
        ]

    async def get_track_audio_file_url(
        self, track_platform_id, audio_file_endpoint_url
    ):
        if audio_file_endpoint_url is not None:
            logger.warning(
                "`audio_file_endpoint_url` is passed but not used for "
                + "youtube audio file getting"
            )

        audio_file_url = await self.downloader.get_audio_download_url(
            f"http://youtube.com/watch?v={track_platform_id}"
        )

        if audio_file_url is None:
            raise NoSuitableFormatError()

        return audio_file_url

    async def get_playlist_by_url(self, url: str):
        playlist_id_query_param = urllib.parse.parse_qs(
            urllib.parse.urlparse(url).query
        ).get("list")

        if playlist_id_query_param is None:
            return None

        youtube_playlist = await self.client.get_playlist_by_id(
            playlist_id_query_param[0]
        )

        if youtube_playlist is None:
            return None

        tracks_references = await self._fetch_all_videos_as_tracks(
            playlist_id_query_param[0]
        )

        return PlaylistToCreateWithTracks(
            name=youtube_playlist.snippet.title,
            description=youtube_playlist.snippet.description,
            picture_url=youtube_playlist.snippet.thumbnails["default"]["url"],
            publicly_available=False,
            track_references=tracks_references,
        )

    async def _fetch_all_videos_as_tracks(self, playlist_id: str):
        """
        fetches all playlist videos by sending a request for each 50
        videos (maximum per request)

        the maximum of 200 (4 requests for 50 requests) is set to prevent spending
        quota
        """

        current_page = {"token": None, "number": 1, "total": None}

        tracks_references = []

        while current_page["number"] <= MAX_YOUTUBE_TRACKS_REQUESTS:
            logger.info(
                "fetching videos page %s of playlist %s. total videos: %s, "
                + "page token: %s",
                current_page["number"],
                playlist_id,
                current_page["total"] or "unknown",
                current_page["token"] or "missing",
            )

            tracks_fetched_count = (
                current_page["number"] * MAX_YOUTUBE_TRACKS_PER_REQUEST
            )

            if (
                current_page["total"] is not None
                and tracks_fetched_count >= current_page["total"]
            ):
                break

            youtube_videos_result = await self.client.get_playlist_videos_portion(
                playlist_id, current_page["token"]
            )

            tracks_references.extend(
                [
                    TrackReferenceSchema(
                        id=f"{Platform.YOUTUBE.value}/{video.content_details.video_id}",
                        platform_id=video.content_details.video_id,
                        platform=Platform.YOUTUBE,
                    )
                    for video in youtube_videos_result.items
                ]
            )

            # completes the execution if there is only one page of videos
            if youtube_videos_result.next_page_token is None:
                break

            current_page["total"] = youtube_videos_result.page_info.total_results
            current_page["token"] = youtube_videos_result.next_page_token
            current_page["number"] = current_page["number"] + 1

        return tracks_references

    def _convert_to_multi_platform_track(
        self, resource_to_convert: YoutubeVideo, track_id: str
    ):
        duration_string: str = resource_to_convert.content_details.duration

        seconds_symbol_index = duration_string.find("S")
        seconds = (
            int(
                re.sub(
                    r"[^0-9]",
                    "",
                    duration_string[seconds_symbol_index - 2 : seconds_symbol_index],
                )
            )
            if seconds_symbol_index != -1
            else 0
        )

        minutes_symbol_index = duration_string.find("M")
        minutes = (
            int(
                re.sub(
                    r"[^0-9]",
                    "",
                    duration_string[minutes_symbol_index - 2 : minutes_symbol_index],
                )
            )
            if minutes_symbol_index != -1
            else 0
        )

        hours_symbol_index = duration_string.find("H")
        hours = (
            int(
                re.sub(
                    r"[^0-9]",
                    "",
                    duration_string[hours_symbol_index - 2 : hours_symbol_index],
                )
            )
            if hours_symbol_index != -1
            else 0
        )

        return LoadedTrack.model_validate(
            dict(
                platform=Platform.YOUTUBE,
                id=track_id,
                platform_id=resource_to_convert.id,
                name=resource_to_convert.snippet.title,
                description=resource_to_convert.snippet.description,
                likes_count=None,
                picture_url=resource_to_convert.snippet.thumbnails["default"]["url"],
                seconds_duration=seconds + minutes * 60 + hours * 60 * 60,
                original_page_url=f"https://youtube.com/watch?v={resource_to_convert.id}",
                audio_file_endpoint_url=None,
                owner={"name": resource_to_convert.snippet.channel_title},
            )
        )
