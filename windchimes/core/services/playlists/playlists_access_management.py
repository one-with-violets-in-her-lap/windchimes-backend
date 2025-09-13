from typing import Optional, Sequence

from pydantic import BaseModel

from windchimes.core.models.playlist import (
    PlaylistToRead,
    PlaylistToReadWithTrackCount,
)
from windchimes.core.models.user import User
from windchimes.core.services.playlists import (
    PlaylistsFilters,
    PlaylistsService,
)


class PlaylistsAccessCheckResult(BaseModel):
    user_owns_all_playlists: bool
    loaded_playlists: Optional[list[PlaylistToReadWithTrackCount]]


class PlaylistsAccessManagementService:
    def __init__(self, playlists_service: PlaylistsService, current_user: User | None):
        self.playlists_service = playlists_service
        self.current_user = current_user

    async def check_if_user_owns_the_playlists(self, playlists_ids: list[int]):
        """Checks if user owns **all** the playlists with specified ids

        Returns:
            If the `current_user` is `None`, immediately returns `False`.
            If requested playlists' owner user id matches current user's
            (`current_user` constructor param) id, returns `True`
        """

        if self.current_user is None:
            return PlaylistsAccessCheckResult(
                user_owns_all_playlists=False, loaded_playlists=None
            )

        playlists_to_check = await self.playlists_service.get_playlists(
            PlaylistsFilters(ids=playlists_ids, owner_user_id=self.current_user.sub)
        )

        if len(playlists_to_check) == 0:
            return PlaylistsAccessCheckResult(
                user_owns_all_playlists=False, loaded_playlists=playlists_to_check
            )
        else:
            return PlaylistsAccessCheckResult(
                user_owns_all_playlists=True, loaded_playlists=playlists_to_check
            )

    def get_playlists_user_can_view(self, playlists: Sequence[PlaylistToRead]):
        return [
            playlist
            for playlist in playlists
            if playlist.publicly_available
            or (
                self.current_user is not None
                and playlist.owner_user_id == self.current_user.sub
            )
        ]
