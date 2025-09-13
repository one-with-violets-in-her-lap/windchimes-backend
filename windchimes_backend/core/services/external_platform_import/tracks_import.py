import logging

from pydantic import BaseModel, HttpUrl
from sqlalchemy import delete, select

from windchimes_backend.core.database import Database
from windchimes_backend.core.database.models.playlist import PlaylistTrack
from windchimes_backend.core.database.models.track_reference import TrackReference
from windchimes_backend.core.models.platform import Platform
from windchimes_backend.core.models.track import TrackReferenceSchema
from windchimes_backend.core.services.external_platforms.platform_aggregator import (
    PlatformAggregatorService,
)


logger = logging.getLogger(__name__)


class PlaylistToImport(BaseModel):
    platform: Platform
    url: HttpUrl


class ExternalPlaylistNotFoundError(Exception):
    def __init__(self):
        super().__init__("External playlist with specified url cannot be found")


class TracksImportService:
    def __init__(
        self,
        database: Database,
        platform_aggregator_service: PlatformAggregatorService,
    ):
        self.database = database
        self.platform_aggregator_service = platform_aggregator_service

    async def import_playlist_tracks(
        self,
        playlist_to_import_from: PlaylistToImport,
        playlist_to_import_to_id: int,
        replace_existing_tracks=False,
    ):
        """
        Adds or replaces tracks in app playlist with tracks from external platform
        (e.g. SoundCloud) playlist

        Args:
            playlist_to_import_from: external playlist platform and url to obtain the
                tracks data
            playlist_to_import_to_id: app (internal) playlist to import tracks to
        """

        logger.info(
            "Importing tracks from %s playlist - %s to internal playlist with id %s. "
            + "Replace existing tracks: %s",
            playlist_to_import_from.platform.value,
            playlist_to_import_from.url,
            playlist_to_import_to_id,
            replace_existing_tracks,
        )

        playlist_to_import_from_data = (
            await self.platform_aggregator_service.get_playlist_by_url(
                playlist_to_import_from.platform,
                str(playlist_to_import_from.url),
            )
        )

        if playlist_to_import_from_data is None:
            raise ExternalPlaylistNotFoundError()

        # if replace_existing_tracks:
        #     async with self.database.create_session() as database_session:
        #         logger.info(
        #             "Deleting existing tracks of playlist %s to replace with imported ones",
        #             playlist_to_import_to.id,
        #         )

        #         delete_existing_tracks_statement = delete(PlaylistTrack).where(
        #             PlaylistTrack.playlist_id == playlist_to_import_to.id
        #         )
        #         await database_session.execute(delete_existing_tracks_statement)
        #         await database_session.commit()

        async with self.database.create_session() as database_session:
            track_references_to_add_to_database = [
                TrackReference(**track_reference.model_dump())
                for track_reference in playlist_to_import_from_data.track_references
            ]

            database_session.add_all(track_references_to_add_to_database)

            await database_session.commit()

            new_playlist_tracks_associations = [
                PlaylistTrack(
                    playlist_id=playlist_to_import_to_id, track_id=track_reference.id
                )
                for track_reference in track_references_to_add_to_database
            ]

            database_session.add_all(new_playlist_tracks_associations)

            await database_session.commit()

    async def _get_already_existing_track_references(
        self,
        track_references: list[TrackReferenceSchema],
    ):
        async with self.database.create_session() as database_session:
            track_references_platform_ids = [
                track_reference.platform_id for track_reference in track_references
            ]

            statement = select(TrackReference).where(TrackReference.platform_id.in_(track_references_platform_ids))
            result = await database_session.execute(statement)
