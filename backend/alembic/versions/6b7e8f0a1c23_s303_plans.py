"""s303_workout_plans

Revision ID: 6b7e8f0a1c23
Revises: 9c2a1d9e4f31
Create Date: 2026-09-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6b7e8f0a1c23"
down_revision: Union[str, Sequence[str], None] = "9c2a1d9e4f31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "workout_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("length_weeks", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column(
        "workout_sessions",
        sa.Column("plan_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_workout_sessions_plan_id_workout_plans",
        "workout_sessions",
        "workout_plans",
        ["plan_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_workout_sessions_plan_id_session_at",
        "workout_sessions",
        ["plan_id", "session_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_workout_sessions_plan_id_session_at",
        table_name="workout_sessions",
    )
    op.drop_constraint(
        "fk_workout_sessions_plan_id_workout_plans",
        "workout_sessions",
        type_="foreignkey",
    )
    op.drop_column("workout_sessions", "plan_id")
    op.drop_table("workout_plans")
