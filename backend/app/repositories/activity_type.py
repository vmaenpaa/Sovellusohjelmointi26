from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity_type import ActivityType


def get_or_create_system(
    db: Session,
    *,
    name: str,
    slug: str,
) -> ActivityType:
    activity_type = db.scalar(
        select(ActivityType).where(
            ActivityType.slug == slug,
            ActivityType.is_system.is_(True),
        )
    )
    if activity_type is None:
        activity_type = ActivityType(
            name=name,
            slug=slug,
            is_system=True,
        )
        db.add(activity_type)
    else:
        activity_type.name = name
    return activity_type