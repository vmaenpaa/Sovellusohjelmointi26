from app.db.base import Base
from app.models.activity_type_unit_type import ActivityTypeUnitType
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Index
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .activity_type_unit_type import ActivityTypeUnitType

class ActivityType(Base):
    __tablename__ = "activity_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    slug: Mapped[str] = mapped_column()
    is_system: Mapped[bool] = mapped_column(default=True)
    user_id: Mapped[int | None] = mapped_column(nullable=True)

    __table_args__ = (
        Index(
            "uq_activity_type_system_slug",
            "slug",
            unique=True,
            postgresql_where=(is_system.is_(True)),
            ),
        Index(
            "uq_activity_type_custom_user_slug",
            "user_id",
            "slug",
            unique=True,
            postgresql_where=(is_system.is_(False)),
            )
        )

    unit_links: Mapped[list["ActivityTypeUnitType"]] = relationship(
        back_populates="activity_type"
        )
    
    def __str__(self) -> str:
        return self.slug