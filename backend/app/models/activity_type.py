from app.db.base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import NULL, Index

class ActivityType(Base):
    __tablename__ = "activity_types"

    name: Mapped[int]
    slug: Mapped[str]
    is_system: Mapped[bool] = mapped_column(default=True)
    user_id: Mapped[int | NULL] = mapped_column(default=NULL)

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
        ),
    )
    def __str__(self) -> str:
        return self.slug