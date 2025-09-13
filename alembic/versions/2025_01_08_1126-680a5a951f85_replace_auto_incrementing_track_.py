"""replace auto incrementing track reference id with unique string id

Revision ID: 680a5a951f85
Revises: 2d625cd588c6
Create Date: 2025-01-08 11:26:14.449729

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "680a5a951f85"
down_revision: Union[str, None] = "2d625cd588c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("playlist_track", schema=None) as batch_op:
        batch_op.drop_constraint("fk_playlist_track_track_id_track_reference")

    with op.batch_alter_table("track_reference", schema=None) as batch_op:
        batch_op.alter_column(
            "id", existing_type=sa.INTEGER(), type_=sa.String(), existing_nullable=False
        )

    with op.batch_alter_table("playlist_track", schema=None) as batch_op:
        batch_op.alter_column(
            "track_id",
            existing_type=sa.INTEGER(),
            type_=sa.String(),
            existing_nullable=False,
        )

    with op.batch_alter_table("playlist_track", schema=None) as batch_op:
        batch_op.create_foreign_key(
            constraint_name="fk_playlist_track_track_id_track_reference",
            referent_table="track_reference",
            remote_cols=["id"],
            local_cols=["track_id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    with op.batch_alter_table("playlist_track", schema=None) as batch_op:
        batch_op.drop_constraint("fk_playlist_track_track_id_track_reference")

    with op.batch_alter_table("track_reference", schema=None) as batch_op:
        batch_op.alter_column(
            "id", existing_type=sa.String(), type_=sa.INTEGER(), existing_nullable=False
        )

    with op.batch_alter_table("playlist_track", schema=None) as batch_op:
        batch_op.alter_column(
            "track_id",
            existing_type=sa.String(),
            type_=sa.INTEGER(),
            existing_nullable=False,
        )

    with op.batch_alter_table("playlist_track", schema=None) as batch_op:
        batch_op.create_foreign_key(
            constraint_name="fk_playlist_track_track_id_track_reference",
            referent_table="track_reference",
            remote_cols=["id"],
            local_cols=["track_id"],
            ondelete="CASCADE",
        )
