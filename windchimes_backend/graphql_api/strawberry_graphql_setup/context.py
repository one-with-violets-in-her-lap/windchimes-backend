from functools import cached_property
import logging

from strawberry.fastapi import BaseContext

from windchimes_backend.core.api_clients.soundcloud import SoundcloudApiClient
from windchimes_backend.core.database import database
from windchimes_backend.core.services.auth import AuthService
from windchimes_backend.core.services.external_platform_import.tracks_import import (
    TracksImportService,
)
from windchimes_backend.core.services.external_platforms.platform_aggregator import (
    PlatformAggregatorService,
)
from windchimes_backend.core.services.external_platforms.soundcloud import (
    SoundcloudService,
)
from windchimes_backend.core.services.playlists import PlaylistsService
from windchimes_backend.core.services.playlists.playlists_access_management import (
    PlaylistsAccessManagementService,
)


logger = logging.getLogger(__name__)


class GraphQLRequestContext(BaseContext):
    @cached_property
    def database(self):
        return database

    @cached_property
    def playlists_service(self):
        return PlaylistsService(self.database)

    @cached_property
    def playlists_access_management_service(self):
        return PlaylistsAccessManagementService(
            self.playlists_service, self.current_user
        )

    @cached_property
    def tracks_import_service(self):
        return TracksImportService(self.database, self.platform_aggregator_service)

    @cached_property
    def soundcloud_integration(self):
        soundcloud_api_client = SoundcloudApiClient()
        soundcloud_service = SoundcloudService(soundcloud_api_client)

        return {"api_client": soundcloud_api_client, "service": soundcloud_service}

    @cached_property
    def platform_aggregator_service(self):
        return PlatformAggregatorService(
            soundcloud_service=self.soundcloud_integration["service"]
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
