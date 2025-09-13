from enum import Enum

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from windchimes_backend.core.database.models.base import BaseDatabaseModel


class Platform(Enum):
    SOUNDCLOUD = "SOUNDCLOUD"
    YOUTUBE = "YOUTUBE"


class TrackReference(BaseDatabaseModel):
    """
    external track model that doesnt have track data itself, but contains a
    link (external platform ID) to it
    """

    __tablename__ = "track_reference"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    platform_id: Mapped[str]
    """external platform id of the track that is being referenced"""

    platform: Mapped[Platform]

    __table_args__ = (
        UniqueConstraint(
            "platform_id",
            "platform",
        ),
    )

    def __repr__(self) -> str:
        return f"track {self.platform_id} on {self.platform.value.lower()}"
