from datetime import datetime
from typing import Any, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import functions

from windchimes_backend.core.database.models.base import BaseDatabaseModel
from windchimes_backend.core.models.platform import Platform


class ExternalPlaylistReference(BaseDatabaseModel):
    """
    External playlist model that doesn't have playlist data itself, but contains a
    link (external platform ID) to it

    Stored for syncing with in-app playlists
    """

    __tablename__ = "external_playlist_reference"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    last_sync_at: Mapped[datetime]

    platform_id: Mapped[str]
    """External platform id of the playlist that is being referenced"""

    platform: Mapped[Platform]

    parent_playlist_id: Mapped[Optional[int]] = mapped_column(ForeignKey("playlist.id"))
    playlist: Mapped[Any] = relationship(
        "Playlist", back_populates="external_playlist_to_sync_with"
    )
