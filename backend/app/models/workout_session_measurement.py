from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .unit_type import UnitType
    from .workout_session_item import WorkoutSessionItem


class WorkoutSessionMeasurement(Base):
    __tablename__ = "workout_session_measurements"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_item_id: Mapped[int] = mapped_column(
        ForeignKey("workout_session_items.id", ondelete="CASCADE"),
    )
    unit_type_id: Mapped[int] = mapped_column(
        ForeignKey("unit_types.id", ondelete="RESTRICT"),
    )
    planned_value: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 3),
        nullable=True,
    )
    actual_value: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 3),
        nullable=True,
    )
    set_index: Mapped[int | None] = mapped_column(nullable=True)

    session_item: Mapped["WorkoutSessionItem"] = relationship(
        back_populates="measurements",
    )
    unit_type: Mapped["UnitType"] = relationship()