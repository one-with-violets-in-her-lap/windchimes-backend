import logging
from typing import Annotated, Optional
import timeit

from annotated_types import Len
from pydantic import BaseModel
from sqlalchemy import and_, delete, desc, not_, select, update
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import functions

from windchimes.core.database import Database
from windchimes.core.database.models.playlist import Playlist, PlaylistTrack
from windchimes.core.database.models.track_reference import TrackReference
from windchimes.core.models.playlist import (
    ExternalPlaylistReferenceSchema,
    PlaylistToCreate,
    PlaylistToReadWithTrackCount,
    PlaylistDetailed,
)
from windchimes.core.models.track import TrackReferenceSchema


logger = logging.getLogger(__name__)


class PlaylistsFilters(BaseModel):
    owner_user_id: Optional[str] = None
    exclude_owner_user_id: Optional[str] = None
    ids: Optional[list[int]] = None

    exclude_containing_track_reference_id: Optional[str] = None
    """
    If specified, playlists that contain track reference with
    specified id are excluded from the output
    """

    containing_track_reference_id: Optional[str] = None
    """
    If specified, ONLY the playlists that contain track reference with
    specified id are included in the output
    """


class PlaylistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    picture_url: Optional[str] = None
    publicly_available: Optional[bool] = None


class PlaylistDeleteOrUpdateFailed(Exception):
    def __init__(self):
        super().__init__(
            "Deletion or update failed because the playlist with specified id does "
            + "not exist or current user doesn't have access to that playlist"
        )


class TracksToAddToPlaylistsWrapper(BaseModel):
    class TrackToAddToPlaylist(BaseModel):
        id: str
        playlists_ids_to_add_to: Annotated[list[int], Len(min_length=1)]

    tracks: list[TrackToAddToPlaylist]


class TrackToDeleteFromPlaylists(BaseModel):
    track_id: str
    playlists_ids: Annotated[list[int], Len(min_length=1)]


class PlaylistsService:
    def __init__(self, database: Database):
        self._database = database

    # TODO: optimize, do not query all of playlists' tracks just to count them
    async def get_playlists(
        self,
        filters: PlaylistsFilters = PlaylistsFilters(),
        limit: Optional[int] = None,
    ):
        async with self._database.create_session() as database_session:
            start_time_seconds = timeit.default_timer()

            statement = (
                select(
                    Playlist,
                    functions.count(PlaylistTrack.playlist_id).label("track_count"),
                )
                .outerjoin(PlaylistTrack)
                .group_by(Playlist.id)
            )

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

            if filters.containing_track_reference_id is not None:
                statement = statement.where(
                    Playlist.track_references.any(
                        TrackReference.id == filters.containing_track_reference_id
                    )
                )

            if filters.exclude_containing_track_reference_id is not None:
                statement = statement.where(
                    not_(
                        Playlist.track_references.any(
                            TrackReference.id
                            == filters.exclude_containing_track_reference_id
                        )
                    )
                )

            if limit is not None:
                statement = statement.limit(limit)

            statement = statement.order_by(desc(Playlist.created_at))

            playlists_result = await database_session.execute(statement)

            logger.info(
                "Fetched the playlists from DB in %s seconds",
                timeit.default_timer() - start_time_seconds,
            )

            return [
                PlaylistToReadWithTrackCount(
                    **vars(playlist_and_track_count[0]),
                    track_count=playlist_and_track_count[1],
                )
                for playlist_and_track_count in playlists_result.unique().all()
            ]

    async def get_playlist_detailed(self, playlist_id: int):
        async with self._database.create_session() as database_session:
            playlist = await database_session.get(
                Playlist,
                playlist_id,
                options=[
                    joinedload(Playlist.track_references),
                    joinedload(Playlist.external_playlist_to_sync_with),
                ],
            )

            if playlist is None:
                return None

            external_playlist_to_sync_with = (
                ExternalPlaylistReferenceSchema.model_validate(
                    vars(playlist.external_playlist_to_sync_with)
                )
                if playlist.external_playlist_to_sync_with is not None
                else None
            )

            return PlaylistDetailed.model_validate(
                {
                    **vars(playlist),
                    "external_playlist_to_sync_with": external_playlist_to_sync_with,
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

            return PlaylistDetailed(
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
                .values(new_playlist_data.model_dump(exclude_unset=True))
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

    async def delete_track_from_playlists(
        self, track_to_delete_from_playlists: TrackToDeleteFromPlaylists
    ):
        """
        Deletes track from playlists with specified ids
        (`track_to_delete_from_playlist.playlists_ids` param)

        Returns:
            Ids of the playlist from which the track was deleted
        """

        async with self._database.create_session() as database_session:
            statement = delete(PlaylistTrack).where(
                and_(
                    PlaylistTrack.playlist_id.in_(
                        track_to_delete_from_playlists.playlists_ids
                    ),
                    PlaylistTrack.track_id == track_to_delete_from_playlists.track_id,
                )
            )

            await database_session.execute(statement)
            await database_session.commit()

            return track_to_delete_from_playlists.playlists_ids
