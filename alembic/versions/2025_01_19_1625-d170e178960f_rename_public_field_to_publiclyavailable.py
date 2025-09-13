"""rename `public` field to `publiclyAvailable`

Revision ID: d170e178960f
Revises: 2ae4b1e89376
Create Date: 2025-01-19 16:25:39.511357

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d170e178960f"
down_revision: Union[str, None] = "2ae4b1e89376"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("playlist", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "publiclyAvailable",
                sa.Boolean(),
                nullable=False,
                server_default="False",
            )
        )
        batch_op.drop_column("public")


def downgrade() -> None:
    with op.batch_alter_table("playlist", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "public",
                sa.BOOLEAN(),
                server_default=sa.text("false"),
                autoincrement=False,
                nullable=False,
            )
        )
        batch_op.drop_column("publiclyAvailable")
