from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .activity_type import ActivityType
    from .workout_session import WorkoutSession
    from .workout_session_measurement import WorkoutSessionMeasurement


class WorkoutSessionItem(Base):
    __tablename__ = "workout_session_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("workout_sessions.id", ondelete="CASCADE"),
    )
    activity_type_id: Mapped[int] = mapped_column(
        ForeignKey("activity_types.id", ondelete="RESTRICT"),
    )
    sort_order: Mapped[int]
    notes: Mapped[str | None] = mapped_column(nullable=True)

    session: Mapped["WorkoutSession"] = relationship(
        back_populates="items",
    )
    activity_type: Mapped["ActivityType"] = relationship()
    measurements: Mapped[list["WorkoutSessionMeasurement"]] = relationship(
        back_populates="session_item",
        cascade="all, delete-orphan",
        order_by="WorkoutSessionMeasurement.set_index",
    )