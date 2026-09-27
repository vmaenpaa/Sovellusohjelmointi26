from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .activity_type import ActivityType
    from .unit_type import UnitType
    from .user import User


class Goal(Base):
    __tablename__ = "goals"

    __table_args__ = (
        CheckConstraint(
            "period IN ('week', 'month')",
            name="ck_goals_period",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    unit_type_id: Mapped[int] = mapped_column(
        ForeignKey("unit_types.id", ondelete="RESTRICT"),
    )
    activity_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("activity_types.id", ondelete="SET NULL"),
        nullable=True,
    )
    target_value: Mapped[Decimal] = mapped_column(Numeric(12, 3))
    period: Mapped[str]
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship()
    unit_type: Mapped["UnitType"] = relationship()
    activity_type: Mapped["ActivityType | None"] = relationship()
