from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import func, select

from windchimes_backend.core.database import Database
from windchimes_backend.core.database.models.playlist import Playlist
from windchimes_backend.core.database.models.track_reference import TrackReference


class PlaylistsFilters(BaseModel):
    owner_user_id: Optional[str] = None
    exclude_owner_user_id: Optional[str] = None


class PlaylistWithTrackCount(BaseModel):
    id: int
    created_at: datetime
    name: str
    slug: str
    description: Optional[str]
    picture_url: Optional[str]
    owner_user_id: str

    track_count: int


class PlaylistsService:
    def __init__(self, database: Database):
        self._database = database

    async def get_playlists(self, filters: PlaylistsFilters = PlaylistsFilters()):
        async with self._database.create_session() as database_session:
            statement = select(Playlist, func.count(TrackReference.id)).select_from(
                Playlist
            )

            if filters.exclude_owner_user_id is not None:
                statement = statement.where(
                    Playlist.owner_user_id != filters.exclude_owner_user_id
                )

            if filters.owner_user_id is not None:
                statement = statement.where(
                    Playlist.owner_user_id == filters.owner_user_id
                )

            statement = statement.join(Playlist.track_references).group_by(Playlist.id)

            result = await database_session.execute(statement)

            playlists_with_track_count = result.fetchall()

            return [
                PlaylistWithTrackCount(
                    **vars(playlist_and_track_count[0]),
                    track_count=playlist_and_track_count[1]
                )
                for playlist_and_track_count in playlists_with_track_count
            ]
