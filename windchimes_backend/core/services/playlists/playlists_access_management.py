from typing import Sequence
from windchimes_backend.core.models.user import User
from windchimes_backend.core.services.playlists import (
    PlaylistToRead,
    PlaylistsFilters,
    PlaylistsService,
)


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
            return False

        playlists_to_check = await self.playlists_service.get_playlists(
            PlaylistsFilters(ids=playlists_ids, owner_user_id=self.current_user.sub)
        )

        if len(playlists_to_check) == 0:
            return False
        else:
            return True

    def get_playlists_user_can_view(self, playlists: Sequence[PlaylistToRead]):
        return [
            playlist
            for playlist in playlists
            if playlist.public
            or (self.current_user is not None and playlist.owner_user_id == self.current_user.sub)
        ]
