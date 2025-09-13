"""remove "slug" field for playlists

Revision ID: 2d625cd588c6
Revises: dfb77c6da464
Create Date: 2025-01-06 11:27:51.507083

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2d625cd588c6"
down_revision: Union[str, None] = "dfb77c6da464"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("playlist", schema=None) as batch_op:
        batch_op.drop_column("slug")


def downgrade() -> None:
    with op.batch_alter_table("playlist", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("slug", sa.VARCHAR(), autoincrement=False, nullable=False)
        )
