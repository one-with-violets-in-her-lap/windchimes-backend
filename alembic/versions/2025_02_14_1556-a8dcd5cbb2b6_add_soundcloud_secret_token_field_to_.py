"""Add `soundcloud_secret_token` field to `external_playlist_reference` table

Revision ID: a8dcd5cbb2b6
Revises: c362467d767d
Create Date: 2025-02-14 15:56:58.395059

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a8dcd5cbb2b6"
down_revision: Union[str, None] = "c362467d767d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("external_playlist_reference", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("soundcloud_secret_token", sa.String(), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("external_playlist_reference", schema=None) as batch_op:
        batch_op.drop_column("soundcloud_secret_token")
