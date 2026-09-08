from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .activity_type_unit_type import ActivityTypeUnitType


class UnitType(Base):
    __tablename__ = "unit_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    slug: Mapped[str]
    unit_label: Mapped[str | None] = mapped_column(nullable=True)
    is_system: Mapped[bool] = mapped_column(default=True)

    activity_type_links: Mapped[list["ActivityTypeUnitType"]] = relationship(
        back_populates="unit_type"
    )

    def __str__(self) -> str:
        return self.slug