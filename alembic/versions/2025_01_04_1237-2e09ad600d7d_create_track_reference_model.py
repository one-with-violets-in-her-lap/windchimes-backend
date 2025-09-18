"""create track reference model

Revision ID: 2e09ad600d7d
Revises:
Create Date: 2025-01-04 12:37:51.846719

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2e09ad600d7d"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "track_reference",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("platform_id", sa.String(), nullable=False),
        sa.Column(
            "platform",
            sa.Enum("SOUNDCLOUD", "YOUTUBE", name="platform"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_track_reference")),
        sa.UniqueConstraint(
            "platform_id", "platform", name=op.f("uq_track_reference_platform_id")
        ),
    )


def downgrade() -> None:
    op.drop_table("track_reference")
