"""replace `created_at` col with `last_sync_at` col

Revision ID: c362467d767d
Revises: 6d41fd38df1e
Create Date: 2025-02-14 12:10:33.927446

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c362467d767d"
down_revision: Union[str, None] = "6d41fd38df1e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("external_playlist_reference", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "last_sync_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.sql.func.now(),
            )
        )
        batch_op.drop_column("created_at")


def downgrade() -> None:
    with op.batch_alter_table("external_playlist_reference", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "created_at",
                postgresql.TIMESTAMP(),
                server_default=sa.text("now()"),
                autoincrement=False,
                nullable=False,
            )
        )
        batch_op.drop_column("last_sync_at")
