from app.db.base import Base
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .activity_type import ActivityType
    from .unit_type import UnitType

class ActivityTypeUnitType(Base):
    __tablename__ = "activity_type_unit_types"

    activity_type_id: Mapped[int] = mapped_column(
        ForeignKey("activity_types.id"),
        primary_key=True,
    )
    unit_type_id: Mapped[int] = mapped_column(
        ForeignKey("unit_types.id"),
        primary_key=True,
    )
    sort_order: Mapped[int]
    is_required: Mapped[bool]
    per_set: Mapped[int]

    activity_type: Mapped["ActivityType"] = relationship(
        back_populates="unit_links"
    )

    unit_type: Mapped["UnitType"] = relationship(
        back_populates="activity_type_links"
    )

    __table_args__ = (
        UniqueConstraint(
            "activity_type_id",
            "unit_type_id",
            name="uq_activity_type_unit_type_pair",
        ),
    )
