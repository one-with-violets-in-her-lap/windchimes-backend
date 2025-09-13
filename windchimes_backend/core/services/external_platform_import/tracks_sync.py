import logging

from sqlalchemy import update
from windchimes_backend.core.database import Database
from windchimes_backend.core.database.models.playlist import Playlist
from windchimes_backend.core.errors.external_platform_import import (
    ExternalPlaylistNotFoundError,
)
from windchimes_backend.core.models.platform import Platform
from windchimes_backend.core.models.playlist import ExternalPlaylistReference
from windchimes_backend.core.services.external_platforms.platform_aggregator import (
    PlatformAggregatorService,
)


logger = logging.getLogger(__name__)


class TracksSyncService:
    def __init__(
        self, database: Database, platform_aggregator_service: PlatformAggregatorService
    ) -> None:
        self.database = database
        self.platform_aggregator_service = platform_aggregator_service

    async def link_external_playlist_for_sync(
        self,
        playlist_to_link_to_id: int,
        external_playlist_to_link: ExternalPlaylistReference,
    ):
        logger.info(
            "Setting up sync for playlist %s with external %s playlist - %s",
            playlist_to_link_to_id,
            external_playlist_to_link.platform.value,
            str(external_playlist_to_link.url),
        )

        external_playlist_data = (
            await self.platform_aggregator_service.get_playlist_by_url(
                external_playlist_to_link.platform,
                str(external_playlist_to_link.url),
            )
        )

        if external_playlist_data is None:
            raise ExternalPlaylistNotFoundError()

        async with self.database.create_session() as database_session:
            statement = (
                update(Playlist)
                .where(
                    Playlist.id == playlist_to_link_to_id,
                )
                .values(
                    sync_platform=external_playlist_to_link.platform,
                    sync_playlist_external_platform_id=external_playlist_data.external_platform_id,
                )
            )

            await database_session.execute(statement)
            await database_session.commit()

    async def disable_external_playlist_sync(self, playlist_id: int):
        logger.info("Disabling sync for playlist %s", playlist_id)

        async with self.database.create_session() as database_session:
            statement = (
                update(Playlist)
                .where(
                    Playlist.id == playlist_id,
                )
                .values(sync_platform=None, sync_playlist_external_platform_id=None)
            )

            await database_session.execute(statement)
            await database_session.commit()

    async def sync_playlist_tracks(self, playlist_to_sync_id: int):
        async with self.database.create_session() as database_session:
            pass
