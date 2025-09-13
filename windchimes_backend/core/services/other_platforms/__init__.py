from abc import ABC, abstractmethod
from typing import Optional

from windchimes_backend.core.database.models.playlist import Playlist
from windchimes_backend.core.models.track import LoadedTrack, TrackReferenceSchema


class ProviderPlatformService(ABC):
    """
    Base class for services that provide methods to access data from
    external platforms like Youtube and Soundcloud
    """

    @abstractmethod
    async def load_tracks(
        self, tracks_to_load: list[TrackReferenceSchema]
    ) -> list[Optional[LoadedTrack]]:
        """
        fetches tracks from external platform and converts them to a common
        multi-platform format

        Args:
            tracks_to_load: list of track entities that act as references to
                external platform tracks
        """
        pass

    @abstractmethod
    async def get_track_audio_file_url(
        self, track_platform_id: str, audio_file_endpoint_url: Optional[str]
    ) -> Optional[str]:
        """fetches the track data and searches for mp3 audio file

        Raises:
            NoSuitableFormatError: if failed to find suitable file format

        Args:
            track_platform_id: id to use to get data track data from external platform
            audio_file_endpoint_url: endpoint where to find audio file url on platforms
                where it can't be found with track platform id
                for example, on soundcloud -
                https://api-v2.soundcloud.com/media/soundcloud:tracks:.../.../stream/progressive
        """
        pass

    @abstractmethod
    async def get_playlist_by_url(
        self, url: str, user_id_to_assign_as_owner: str
    ) -> Optional[Playlist]:
        pass

    @abstractmethod
    def _convert_to_multi_platform_track(
        self, resource_to_convert, track_id: int
    ) -> LoadedTrack:
        pass
