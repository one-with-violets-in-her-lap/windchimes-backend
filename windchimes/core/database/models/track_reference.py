from typing import Any

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from windchimes.core.database.models.base import BaseDatabaseModel
from windchimes.core.models.platform import Platform


class TrackReference(BaseDatabaseModel):
    """
    external track model that doesnt have track data itself, but contains a
    link (external platform ID) to it
    """

    __tablename__ = "track_reference"

    id: Mapped[str] = mapped_column(primary_key=True)
    """
    Unique track identifier in this format - `PLATFORM/TRACK_PLATFORM_ID`,
    for example `YOUTUBE/vKuKp10LQEM`
    """

    platform_id: Mapped[str]
    """external platform id of the track that is being referenced"""

    platform: Mapped[Platform]

    playlists: Mapped[list[Any]] = relationship(
        "Playlist", secondary="playlist_track", back_populates="track_references"
    )

    __table_args__ = (
        UniqueConstraint(
            "platform_id",
            "platform",
        ),
    )

    def __repr__(self) -> str:
        return f"track {self.platform_id} on {self.platform.value.lower()}"
