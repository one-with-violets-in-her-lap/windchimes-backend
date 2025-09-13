from datetime import datetime
from typing import Any, Optional

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import functions

from windchimes_backend.core.database.models.base import BaseDatabaseModel
from windchimes_backend.core.models.platform import Platform


class PlaylistTrack(BaseDatabaseModel):
    __tablename__ = "playlist_track"

    playlist_id: Mapped[int] = mapped_column(
        ForeignKey("playlist.id", ondelete="CASCADE"), primary_key=True
    )

    track_id: Mapped[str] = mapped_column(
        ForeignKey("track_reference.id", ondelete="CASCADE"), primary_key=True
    )


class Playlist(BaseDatabaseModel):
    """model of a playlist used for database operations

    Attributes:
        owner_user_id: id of the user that owns a playlist. for now it's provided by
            auth0, an external service
    """

    __tablename__ = "playlist"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(), server_default=functions.now()
    )

    name: Mapped[str]
    description: Mapped[Optional[str]]
    picture_url: Mapped[Optional[str]]

    publicly_available: Mapped[bool] = mapped_column(default=False)
    owner_user_id: Mapped[str]

    track_references: Mapped[list[Any]] = relationship(
        "TrackReference", secondary="playlist_track", back_populates="playlists"
    )

    sync_platform: Mapped[Optional[Platform]]
    sync_playlist_url: Mapped[Optional[str]]

    def __repr__(self) -> str:
        return f"playlist {self.id} - '{self.name}'"
