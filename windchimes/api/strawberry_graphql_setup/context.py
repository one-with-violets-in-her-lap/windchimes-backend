import logging
from typing import Optional, TypedDict

from fastapi import Request

from windchimes.common.api_clients.imagekit_api_client import (
    ImagekitApiClient,
)
from windchimes.common.api_clients.soundcloud import SoundcloudApiClient
from windchimes.common.api_clients.youtube_data_api.youtube_data_api_client import (
    YoutubeDataApiClient,
)
from windchimes.common.api_clients.youtube_internal_api.youtube_internal_api_client import (
    YoutubeInternalApiClient,
)
from windchimes.core.config import app_config
from windchimes.core.database import Database, database
from windchimes.core.models.user import User
from windchimes.core.services.auth_service import AuthService
from windchimes.core.services.external_platform_import.tracks_import import (
    TracksImportService,
)
from windchimes.core.services.external_platform_import.tracks_sync import (
    TracksSyncService,
)
from windchimes.core.services.external_platforms.platform_aggregator import (
    PlatformAggregatorService,
)
from windchimes.core.services.external_platforms.soundcloud import (
    SoundcloudService,
)
from windchimes.core.services.external_platforms.youtube_service import (
    YoutubeService,
)
from windchimes.core.services.picture_storage_service import (
    PictureStorageService,
)
from windchimes.core.services.playlists import PlaylistsService
from windchimes.core.services.playlists.playlists_access_management import (
    PlaylistsAccessManagementService,
)
from windchimes.core.services.tracks_service import TracksService
from windchimes.core.stores.soundcloud_api_client_id_store import (
    get_soundcloud_api_client_id,
)

logger = logging.getLogger(__name__)


class GraphQLRequestContext(TypedDict):
    database: Database

    playlists_service: PlaylistsService

    tracks_service: TracksService

    playlists_access_management_service: PlaylistsAccessManagementService

    tracks_import_service: TracksImportService

    tracks_sync_service: TracksSyncService

    picture_storage_service: PictureStorageService

    platform_aggregator_service: PlatformAggregatorService

    auth_service: AuthService

    current_user: Optional[User]


def get_user_from_request(auth_service: AuthService, request: Request):
    logger.info("Getting current user via auth service")

    if not request:
        return None

    auth_header = request.headers.get("Authorization")

    if auth_header is None:
        return None

    auth_header_parts = auth_header.split(" ")

    if len(auth_header_parts) != 2 or auth_header_parts[0] != "Bearer":
        return None

    token = auth_header_parts[1]

    return auth_service.get_user_from_token(token)


async def get_graphql_context(request: Request):
    soundcloud_service = SoundcloudService(
        SoundcloudApiClient(get_soundcloud_api_client_id())
    )

    youtube_data_api_client = YoutubeDataApiClient(app_config.youtube_data_api.key)
    youtube_internal_api_client = YoutubeInternalApiClient(app_config.proxy.url)
    youtube_service = YoutubeService(
        youtube_data_api_client, youtube_internal_api_client
    )

    platform_aggregator_service = PlatformAggregatorService(
        soundcloud_service, youtube_service
    )

    playlists_service = PlaylistsService(database)

    tracks_import_service = TracksImportService(database, platform_aggregator_service)

    auth_service = AuthService()

    current_user = get_user_from_request(auth_service, request)

    return GraphQLRequestContext(
        database=database,
        playlists_service=playlists_service,
        tracks_service=TracksService(database, platform_aggregator_service),
        playlists_access_management_service=PlaylistsAccessManagementService(
            playlists_service, current_user
        ),
        tracks_import_service=tracks_import_service,
        auth_service=AuthService(),
        picture_storage_service=PictureStorageService(
            ImagekitApiClient(app_config.imagekit_api.private_key)
        ),
        tracks_sync_service=TracksSyncService(
            database, platform_aggregator_service, tracks_import_service
        ),
        platform_aggregator_service=platform_aggregator_service,
        current_user=current_user,
    )
