"""add playlist sync fields

Revision ID: da548534cd50
Revises: 8c420ef7e3ad
Create Date: 2025-02-09 14:55:33.636003

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "da548534cd50"
down_revision: Union[str, None] = "8c420ef7e3ad"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("playlist", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "sync_platform",
                sa.Enum("SOUNDCLOUD", "YOUTUBE", name="platform"),
                nullable=True,
            )
        )
        batch_op.add_column(sa.Column("sync_playlist_url", sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("playlist", schema=None) as batch_op:
        batch_op.drop_column("sync_playlist_url")
        batch_op.drop_column("sync_platform")
