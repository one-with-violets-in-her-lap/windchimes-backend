from datetime import datetime
from typing import Any, Optional

from sqlalchemy import ForeignKey, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from windchimes_backend.core.database.models.base import BaseDatabaseModel


class PlaylistTrack(BaseDatabaseModel):
    __tablename__ = "playlist_track"

    playlist_id: Mapped[int] = mapped_column(
        ForeignKey("playlist.id", ondelete="CASCADE"), primary_key=True
    )

    track_id: Mapped[int] = mapped_column(
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
    # pylint: disable=not-callable
    created_at: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now())

    name: Mapped[str]
    slug: Mapped[str]
    description: Mapped[Optional[str]]
    picture_url: Mapped[Optional[str]]

    owner_user_id: Mapped[str]

    tracks: Mapped[list[Any]] = relationship(
        "TrackReference", secondary="playlist_track", back_populates="playlists"
    )

    def __repr__(self) -> str:
        return f"playlist {self.id} - '{self.name}'"
