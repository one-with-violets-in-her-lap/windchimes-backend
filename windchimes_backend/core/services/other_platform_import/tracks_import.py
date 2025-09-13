from pydantic import BaseModel, HttpUrl

from windchimes_backend.core.models.platform import Platform


class PlaylistToImport(BaseModel):
    platform: Platform
    url: HttpUrl


class TracksImportService:
    async def import_playlist_tracks(
        self,
        playlist_to_import_from: PlaylistToImport,
        playlist_to_import_to_id: int,
    ):
        # import logic
        print("import")
