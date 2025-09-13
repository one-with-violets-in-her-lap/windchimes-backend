"""add `public` bool field

Revision ID: 2ae4b1e89376
Revises: 680a5a951f85
Create Date: 2025-01-19 15:28:30.894874

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2ae4b1e89376"
down_revision: Union[str, None] = "680a5a951f85"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("playlist", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("public", sa.Boolean(), nullable=False, server_default="False")
        )


def downgrade() -> None:
    with op.batch_alter_table("playlist", schema=None) as batch_op:
        batch_op.drop_column("public")
