"""replace sync playlist url with an external platform id

Revision ID: b744950fd855
Revises: da548534cd50
Create Date: 2025-02-09 15:54:55.044559

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b744950fd855"
down_revision: Union[str, None] = "da548534cd50"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("playlist", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("sync_playlist_external_platform_id", sa.String(), nullable=True)
        )
        batch_op.drop_column("sync_playlist_url")


def downgrade() -> None:
    with op.batch_alter_table("playlist", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "sync_playlist_url", sa.VARCHAR(), autoincrement=False, nullable=True
            )
        )
        batch_op.drop_column("sync_playlist_external_platform_id")
