import logging

from pydantic import BaseModel, HttpUrl

from windchimes_backend.core.models.platform import Platform


logger = logging.getLogger(__name__)


class PlaylistToImport(BaseModel):
    platform: Platform
    url: HttpUrl


class TracksImportService:
    async def import_playlist_tracks(
        self,
        playlist_to_import_from: PlaylistToImport,
        playlist_to_import_to_id: int,
        replace_existing_tracks=False
    ):
        logger.info(
            "Importing tracks from %s playlist - %s to internal playlist with id %s",
            playlist_to_import_from.platform.value,
            playlist_to_import_from.url,
            playlist_to_import_to_id
        )

        
