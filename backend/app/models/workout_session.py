from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .user import User
    from .workout_session_item import WorkoutSessionItem


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    __table_args__ = (
        CheckConstraint(
            "status IN ('planned', 'in_progress', 'completed')",
            name="ck_workout_sessions_status",
        ),
        CheckConstraint(
            "intensity IS NULL OR intensity BETWEEN 1 AND 10",
            name="ck_workout_sessions_intensity",
        ),
        Index(
            "ix_workout_sessions_user_id_session_at",
            "user_id",
            "session_at",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    name: Mapped[str]
    session_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(default="planned")
    notes: Mapped[str | None] = mapped_column(nullable=True)
    intensity: Mapped[int | None] = mapped_column(nullable=True)
    source_session_id: Mapped[int | None] = mapped_column(
        ForeignKey("workout_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship()
    items: Mapped[list["WorkoutSessionItem"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="WorkoutSessionItem.sort_order",
    )
    source_session: Mapped["WorkoutSession | None"] = relationship(
        remote_side=[id],
        back_populates="derived_sessions",
    )
    derived_sessions: Mapped[list["WorkoutSession"]] = relationship(
        back_populates="source_session",
    )