from functools import cached_property
import logging

from strawberry.fastapi import BaseContext

from windchimes_backend.external_api_clients.imagekit_api_client import (
    ImagekitApiClient,
)
from windchimes_backend.external_api_clients.soundcloud import SoundcloudApiClient
from windchimes_backend.external_api_clients.youtube_data_api.youtube_data_api_client import (
    YoutubeDataApiClient,
)
from windchimes_backend.external_api_clients.youtube_internal_api.youtube_internal_api_client import (
    YoutubeInternalApiClient,
)
from windchimes_backend.core.database import database
from windchimes_backend.core.services.auth_service import AuthService
from windchimes_backend.core.services.external_platform_import.tracks_import import (
    TracksImportService,
)
from windchimes_backend.core.services.external_platform_import.tracks_sync import (
    TracksSyncService,
)
from windchimes_backend.core.services.external_platforms.platform_aggregator import (
    PlatformAggregatorService,
)
from windchimes_backend.core.services.external_platforms.soundcloud import (
    SoundcloudService,
)
from windchimes_backend.core.services.external_platforms.youtube_service import (
    YoutubeService,
)
from windchimes_backend.core.services.picture_storage_service import (
    PictureStorageService,
)
from windchimes_backend.core.services.playlists import PlaylistsService
from windchimes_backend.core.services.playlists.playlists_access_management import (
    PlaylistsAccessManagementService,
)
from windchimes_backend.core.services.tracks_service import TracksService
from windchimes_backend.core.stores.soundcloud_api_client_id_store import (
    get_soundcloud_api_client_id,
)
from windchimes_backend.core.config import app_config


logger = logging.getLogger(__name__)


class GraphQLRequestContext(BaseContext):
    @cached_property
    def database(self):
        return database

    @cached_property
    def playlists_service(self):
        return PlaylistsService(self.database)

    @cached_property
    def tracks_service(self):
        return TracksService(self.database, self.platform_aggregator_service)

    @cached_property
    def playlists_access_management_service(self):
        return PlaylistsAccessManagementService(
            self.playlists_service, self.current_user
        )

    @cached_property
    def tracks_import_service(self):
        return TracksImportService(self.database, self.platform_aggregator_service)

    @cached_property
    def tracks_sync_service(self):
        return TracksSyncService(
            self.database, self.platform_aggregator_service, self.tracks_import_service
        )

    @cached_property
    def picture_storage_service(self):
        imagekit_api_client = ImagekitApiClient(app_config.imagekit_api.private_key)
        return PictureStorageService(imagekit_api_client)

    @cached_property
    def soundcloud_service(self):
        soundcloud_api_client = SoundcloudApiClient(get_soundcloud_api_client_id())
        return SoundcloudService(soundcloud_api_client)

    @cached_property
    def youtube_service(self):
        youtube_data_api_client = YoutubeDataApiClient(app_config.youtube_data_api.key)
        youtube_internal_api_client = YoutubeInternalApiClient(app_config.proxy.url)

        return YoutubeService(youtube_data_api_client, youtube_internal_api_client)

    @cached_property
    def platform_aggregator_service(self):
        return PlatformAggregatorService(
            soundcloud_service=self.soundcloud_service,
            youtube_service=self.youtube_service,
        )

    @cached_property
    def auth_service(self):
        return AuthService()

    @cached_property
    def current_user(self):
        logger.info("Getting current user via auth service")

        if not self.request:
            return None

        auth_header = self.request.headers.get("Authorization")

        if auth_header is None:
            return None

        auth_header_parts = auth_header.split(" ")

        if len(auth_header_parts) != 2 or auth_header_parts[0] != "Bearer":
            return None

        token = auth_header_parts[1]

        return self.auth_service.get_user_from_token(token)
