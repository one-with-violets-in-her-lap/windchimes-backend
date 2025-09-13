"""add external playlist references

Revision ID: 228ad52ae4cd
Revises: b744950fd855
Create Date: 2025-02-09 20:12:16.110462

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "228ad52ae4cd"
down_revision: Union[str, None] = "b744950fd855"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "external_playlist_reference",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("platform_id", sa.String(), nullable=False),
        sa.Column(
            "platform",
            postgresql.ENUM(
                "SOUNDCLOUD", "YOUTUBE", name="platform", create_type=False
            ),
            nullable=False,
        ),
        sa.Column("parent_playlist_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["parent_playlist_id"],
            ["playlist.id"],
            name=op.f("fk_external_playlist_reference_parent_playlist_id_playlist"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_external_playlist_reference")),
    )
    with op.batch_alter_table("playlist", schema=None) as batch_op:
        batch_op.drop_column("sync_platform")
        batch_op.drop_column("sync_playlist_external_platform_id")


def downgrade() -> None:
    with op.batch_alter_table("playlist", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "sync_playlist_external_platform_id",
                sa.VARCHAR(),
                autoincrement=False,
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "sync_platform",
                postgresql.ENUM("SOUNDCLOUD", "YOUTUBE", name="platform"),
                autoincrement=False,
                nullable=True,
            )
        )

    op.drop_table("external_playlist_reference")
