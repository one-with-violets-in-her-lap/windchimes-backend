"""fix `publiclyAvailable` field name case (rename to snake_case)

Revision ID: 8c420ef7e3ad
Revises: d170e178960f
Create Date: 2025-01-19 16:59:27.393647

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8c420ef7e3ad"
down_revision: Union[str, None] = "d170e178960f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("playlist", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "publicly_available",
                sa.Boolean(),
                nullable=False,
                server_default="false",
            )
        )
        batch_op.drop_column("publiclyAvailable")


def downgrade() -> None:
    with op.batch_alter_table("playlist", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "publiclyAvailable",
                sa.BOOLEAN(),
                server_default=sa.text("false"),
                autoincrement=False,
                nullable=False,
            )
        )
        batch_op.drop_column("publicly_available")
