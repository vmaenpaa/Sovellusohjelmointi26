"""s302_goals

Revision ID: 9c2a1d9e4f31
Revises: f0a07af64e1b
Create Date: 2026-09-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9c2a1d9e4f31"
down_revision: Union[str, Sequence[str], None] = "f0a07af64e1b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "goals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("unit_type_id", sa.Integer(), nullable=False),
        sa.Column("activity_type_id", sa.Integer(), nullable=True),
        sa.Column("target_value", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("period", sa.String(), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "period IN ('week', 'month')",
            name="ck_goals_period",
        ),
        sa.ForeignKeyConstraint(
            ["activity_type_id"],
            ["activity_types.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["unit_type_id"],
            ["unit_types.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("goals")
