from datetime import datetime
from typing import Annotated, Optional

from annotated_types import Len
from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.sql import functions
from sqlalchemy.orm import joinedload

from windchimes_backend.core.database import Database
from windchimes_backend.core.database.models.playlist import Playlist, PlaylistTrack
from windchimes_backend.core.database.models.track_reference import TrackReference
from windchimes_backend.core.models.playlist import PlaylistToCreate
from windchimes_backend.core.models.track import TrackReferenceSchema


class PlaylistsFilters(BaseModel):
    owner_user_id: Optional[str] = None
    exclude_owner_user_id: Optional[str] = None
    ids: Optional[list[int]] = None


class PlaylistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    picture_url: Optional[str] = None


class PlaylistToRead(BaseModel):
    id: int
    created_at: datetime
    name: str
    description: Optional[str]
    picture_url: Optional[str]
    owner_user_id: str


class PlaylistToReadWithTrackCount(PlaylistToRead):
    track_count: int


class PlaylistToReadWithTrackReferences(PlaylistToReadWithTrackCount):
    track_references: list[TrackReferenceSchema]


class PlaylistDeleteOrUpdateFailed(Exception):
    def __init__(self):
        super().__init__(
            "Deletion or update failed because the playlist with specified id does "
            + "not exist or current user doesn't have access to that playlist"
        )


class TrackToAddToPlaylist(BaseModel):
    id: str
    playlists_ids_to_add_to: Annotated[list[int], Len(min_length=1)]


class TracksToAddToPlaylistsWrapper(BaseModel):
    tracks: list[TrackToAddToPlaylist]


class PlaylistsService:
    def __init__(self, database: Database):
        self._database = database

    # TODO: optimize, do not query all of playlists' tracks just to count them
    async def get_playlists(self, filters: PlaylistsFilters = PlaylistsFilters()):
        async with self._database.create_session() as database_session:
            statement = select(Playlist).options(joinedload(Playlist.track_references))

            if filters.exclude_owner_user_id is not None:
                statement = statement.where(
                    Playlist.owner_user_id != filters.exclude_owner_user_id
                )

            if filters.owner_user_id is not None:
                statement = statement.where(
                    Playlist.owner_user_id == filters.owner_user_id
                )

            if filters.ids is not None:
                statement = statement.where(Playlist.id.in_(filters.ids))

            playlists_result = await database_session.execute(statement)

            return [
                PlaylistToReadWithTrackCount(
                    **vars(playlist), track_count=len(playlist.track_references)
                )
                for playlist in playlists_result.unique().scalars().all()
            ]

    async def get_playlist_with_track_references(self, playlist_id: int):
        async with self._database.create_session() as database_session:
            playlist = await database_session.get(
                Playlist, playlist_id, options=[joinedload(Playlist.track_references)]
            )

            if playlist is None:
                return None

            return PlaylistToReadWithTrackReferences.model_validate(
                {
                    **vars(playlist),
                    "track_count": len(playlist.track_references),
                    "track_references": [
                        TrackReferenceSchema.model_validate(vars(track_reference))
                        for track_reference in playlist.track_references
                    ],
                }
            )

    async def create_playlist(self, playlist: PlaylistToCreate, owner_user_id: str):
        async with self._database.create_session() as database_session:
            new_playlist = Playlist(
                **playlist.model_dump(), owner_user_id=owner_user_id
            )
            database_session.add(new_playlist)
            await database_session.commit()

            return PlaylistToReadWithTrackReferences(
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
            PlaylistDeleteOrUpdateFailed: Deletion failed because the playlist with
                specified id does not exist or current user doesn't have access to that
                playlist
        """

        async with self._database.create_session() as database_session:
            statement = delete(Playlist).where(
                Playlist.id == playlist_to_delete_id,
                Playlist.owner_user_id == owner_user_id,
            )

            result = await database_session.execute(statement)

            await database_session.commit()

            if result.rowcount == 0:
                raise PlaylistDeleteOrUpdateFailed()

    # TODO: move to separate `auth/playlists.py` service
    async def update_playlist(
        self,
        playlist_to_update_id: int,
        owner_user_id: str,
        new_playlist_data: PlaylistUpdate,
    ):
        """
        Updates a playlist by its id. Owner user id is also needed for access management

        Args:
            playlist_to_update: Id of a playlist to update
            owner_user_id: Id of the playlist owner user. It's needed to ensure user
                with id that does not match the owner user id of a playlist
                cannot update it
            new_playlist_data: Fields to update in playlist

        Raises:
            PlaylistDeleteOrUpdateFailed: Update failed because the playlist with
                specified id does not exist or current user doesn't have access to that
                playlist
        """

        async with self._database.create_session() as database_session:
            statement = (
                update(Playlist)
                .where(
                    Playlist.id == playlist_to_update_id,
                    Playlist.owner_user_id == owner_user_id,
                )
                .values(new_playlist_data.model_dump(exclude_none=True))
            )

            result = await database_session.execute(statement)

            await database_session.commit()

            if result.rowcount == 0:
                raise PlaylistDeleteOrUpdateFailed()

    async def add_tracks_to_playlists(
        self, tracks_to_add_wrapper: TracksToAddToPlaylistsWrapper
    ):
        async with self._database.create_session() as database_session:
            new_playlist_tracks_associations: list[PlaylistTrack] = []

            for track in tracks_to_add_wrapper.tracks:
                new_playlist_tracks_associations.extend(
                    [
                        PlaylistTrack(playlist_id=playlist_id, track_id=track.id)
                        for playlist_id in track.playlists_ids_to_add_to
                    ]
                )

            database_session.add_all(new_playlist_tracks_associations)

            await database_session.commit()
