"""add `created_at` column for external playlists references

Revision ID: 6d41fd38df1e
Revises: 228ad52ae4cd
Create Date: 2025-02-14 12:03:52.142177

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6d41fd38df1e"
down_revision: Union[str, None] = "228ad52ae4cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("external_playlist_reference", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.sql.func.now(),
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("external_playlist_reference", schema=None) as batch_op:
        batch_op.drop_column("created_at")
