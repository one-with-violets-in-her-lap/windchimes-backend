from datetime import datetime
import stat
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import delete, func, select
from sqlalchemy.orm import joinedload

from windchimes_backend.core.database import Database
from windchimes_backend.core.database.models.playlist import Playlist
from windchimes_backend.core.database.models.track_reference import TrackReference
from windchimes_backend.core.models.track_reference import TrackReferenceSchema


class PlaylistsFilters(BaseModel):
    owner_user_id: Optional[str] = None
    exclude_owner_user_id: Optional[str] = None


class PlaylistToCreate(BaseModel):
    name: str
    description: Optional[str]
    picture_url: Optional[str]
    owner_user_id: str


class PlaylistWithTrackCount(BaseModel):
    id: int
    created_at: datetime
    name: str
    description: Optional[str]
    picture_url: Optional[str]
    owner_user_id: str
    track_count: int


class PlaylistWithTrackReferences(PlaylistWithTrackCount):
    id: int
    created_at: datetime
    name: str
    description: Optional[str]
    picture_url: Optional[str]
    owner_user_id: str

    track_references: list[TrackReferenceSchema]


class FailedToDeletePlaylistError(Exception):
    def __init__(self):
        super().__init__(
            "Deletion failed because the playlist with specified id does not exist "
            + "or current user doesn't have access to that playlist"
        )


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

    async def get_playlist_with_track_references(self, playlist_id: int):
        async with self._database.create_session() as database_session:
            playlist = await database_session.get(
                Playlist, playlist_id, options=[joinedload(Playlist.track_references)]
            )

            if playlist is None:
                return None

            return PlaylistWithTrackReferences.model_validate(
                {
                    **vars(playlist),
                    "track_count": len(playlist.track_references),
                    "track_references": [
                        TrackReferenceSchema.model_validate(vars(track_reference))
                        for track_reference in playlist.track_references
                    ],
                }
            )

    async def create_playlist(self, playlist: PlaylistToCreate):
        async with self._database.create_session() as database_session:
            new_playlist = Playlist(**playlist.model_dump())
            database_session.add(new_playlist)
            await database_session.commit()

            return PlaylistWithTrackReferences(
                **vars(new_playlist), track_count=0, track_references=[]
            )

    # TODO: move to separate `auth/playlists.py` service
    async def delete_playlist(self, playlist_to_delete_id: int, owner_user_id: str):
        """
        Deletes a playlist by its id. Owner user id is also needed for access management

        Args:
            playlist_to_delete_id: Id of a playlist to delete
            owner_user_id: Id of the playlist owner user. It's needed to ensure user
                with id that does not match the owner user id of a playlist
                cannot delete it

        Raises:
            FailedToDeletePlaylistError: Deletion failed because the playlist with
                specified id does not exist or current user doesn't have access to that playlist
        """

        async with self._database.create_session() as database_session:
            statement = delete(Playlist).where(
                Playlist.id == playlist_to_delete_id,
                Playlist.owner_user_id == owner_user_id,
            )

            result = await database_session.execute(statement)

            await database_session.commit()

            if result.rowcount == 0:
                raise FailedToDeletePlaylistError()
