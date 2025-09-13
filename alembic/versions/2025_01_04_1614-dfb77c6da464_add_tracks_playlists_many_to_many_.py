"""add tracks -> playlists many-to-many relationship

Revision ID: dfb77c6da464
Revises: 2e09ad600d7d
Create Date: 2025-01-04 16:14:01.291117

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dfb77c6da464"
down_revision: Union[str, None] = "2e09ad600d7d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "playlist",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("picture_url", sa.String(), nullable=True),
        sa.Column("owner_user_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_playlist")),
    )
    op.create_table(
        "playlist_track",
        sa.Column("playlist_id", sa.Integer(), nullable=False),
        sa.Column("track_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["playlist_id"],
            ["playlist.id"],
            name=op.f("fk_playlist_track_playlist_id_playlist"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["track_id"],
            ["track_reference.id"],
            name=op.f("fk_playlist_track_track_id_track_reference"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "playlist_id", "track_id", name=op.f("pk_playlist_track")
        ),
    )


def downgrade() -> None:
    op.drop_table("playlist_track")
    op.drop_table("playlist")
