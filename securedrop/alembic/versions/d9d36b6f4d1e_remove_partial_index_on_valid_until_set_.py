"""remove partial_index on valid_until, set it to nullable=false, add message filter fields

Revision ID: d9d36b6f4d1e
Revises: 2e24fc7536e8
Create Date: 2022-03-16 17:31:28.408112

"""

from datetime import datetime

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d9d36b6f4d1e"
down_revision = "2e24fc7536e8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # remove the old partial index on valid_until, as alembic can't handle it.
    op.execute(sa.text("DROP INDEX IF EXISTS ix_one_active_instance_config"))

    # valid_until will be non-nullable after batch, so set existing nulls to
    # the new default unix epoch datetime
    op.execute(
        sa.text(
            "UPDATE OR IGNORE instance_config SET " "valid_until=:epoch WHERE valid_until IS NULL;"
        ).bindparams(epoch=datetime.fromtimestamp(0))
    )

    # add new columns with default values
    with op.batch_alter_table("instance_config", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("initial_message_min_len", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(
            sa.Column(
                "reject_message_with_codename", sa.Boolean(), nullable=False, server_default="0"
            )
        )
        batch_op.alter_column("valid_until", existing_type=sa.DATETIME(), nullable=False)

    # remove the old partial index *again* in case the batch op recreated it.
    op.execute(sa.text("DROP INDEX IF EXISTS ix_one_active_instance_config"))

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("instance_config", schema=None) as batch_op:
        batch_op.alter_column("valid_until", existing_type=sa.DATETIME(), nullable=True)
        batch_op.drop_column("reject_message_with_codename")
        batch_op.drop_column("initial_message_min_len")

    # valid_until is nullable again, set entries with unix epoch datetime value to NULL
    op.execute(
        sa.text(
            "UPDATE OR IGNORE instance_config SET " "valid_until = NULL WHERE valid_until=:epoch;"
        ).bindparams(epoch=datetime.fromtimestamp(0))
    )

    # manually restore the partial index
    op.execute(
        sa.text(
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_one_active_instance_config ON "
            "instance_config (valid_until IS NULL) WHERE valid_until IS NULL"
        )
    )

    # ### end Alembic commands ###
