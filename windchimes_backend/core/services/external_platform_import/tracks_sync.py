import logging

from sqlalchemy import delete, select

from windchimes_backend.core.database import Database
from windchimes_backend.core.database.models.external_playlist_reference import (
    ExternalPlaylistReference,
)
from windchimes_backend.core.errors.external_platform_import import (
    ExternalPlaylistNotFoundError,
)
from windchimes_backend.core.models.playlist import ExternalPlaylistToLink
from windchimes_backend.core.services.external_platform_import.tracks_import import (
    TracksImportService,
)
from windchimes_backend.core.services.external_platforms.platform_aggregator import (
    PlatformAggregatorService,
)
from windchimes_backend.core.services.playlists import PlaylistToReadWithTrackCount


logger = logging.getLogger(__name__)


class ExternalPlaylistNotLinkedError(Exception):
    def __init__(self):
        super().__init__(
            "Playlist you want to sync does not have external playlist linked to it. "
            + "Playlist must have `external_playlist_reference` table row related to it"
        )


class TracksSyncService:
    def __init__(
        self,
        database: Database,
        platform_aggregator_service: PlatformAggregatorService,
        tracks_import_service: TracksImportService,
    ) -> None:
        self.database = database
        self.platform_aggregator_service = platform_aggregator_service
        self.tracks_import_service = tracks_import_service

    async def link_external_playlist_for_sync(
        self,
        playlist_to_link_to_id: int,
        external_playlist_to_link: ExternalPlaylistToLink,
    ):
        logger.info(
            "Sync setup: starting setup for playlist %s with external %s playlist - %s",
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

        logger.info("Sync setup: Deleting previously linked playlist if exists")
        await self.disable_external_playlist_sync(playlist_to_link_to_id)

        async with self.database.create_session() as database_session:
            external_playlist_reference = ExternalPlaylistReference(
                platform=external_playlist_to_link.platform,
                platform_id=external_playlist_data.external_platform_id,
                parent_playlist_id=playlist_to_link_to_id,
            )

            database_session.add(external_playlist_reference)
            await database_session.commit()

            return external_playlist_data

    async def disable_external_playlist_sync(self, playlist_id: int):
        logger.info("Disabling sync for playlist %s", playlist_id)

        async with self.database.create_session() as database_session:
            statement = delete(ExternalPlaylistReference).where(
                ExternalPlaylistReference.parent_playlist_id == playlist_id
            )

            await database_session.execute(statement)
            await database_session.commit()

    async def sync_playlist_tracks(
        self, playlist_to_sync: PlaylistToReadWithTrackCount
    ):
        external_playlist_data = await self.get_external_playlist_linked(
            playlist_to_sync.id
        )

        if external_playlist_data is None:
            raise ExternalPlaylistNotFoundError()

        logger.info(
            "Syncing %s tracks from external playlist'",
            len(external_playlist_data.track_references),
        )

        await self.tracks_import_service.add_tracks_to_playlist(
            playlist_to_sync.id,
            external_playlist_data.track_references,
            replace_existing_tracks=True,
        )

        return external_playlist_data.track_references

    async def get_external_playlist_linked(self, playlist_id: int):
        async with self.database.create_session() as database_session:
            linked_playlist_query_statement = select(ExternalPlaylistReference).where(
                ExternalPlaylistReference.parent_playlist_id == playlist_id
            )

            result = await database_session.execute(linked_playlist_query_statement)

            external_playlist_to_sync_with_reference = result.scalar()

            if external_playlist_to_sync_with_reference is None:
                return None

            external_playlist_data = (
                await self.platform_aggregator_service.get_playlist_by_id(
                    external_playlist_to_sync_with_reference.platform,
                    external_playlist_to_sync_with_reference.platform_id,
                )
            )

            return external_playlist_data
