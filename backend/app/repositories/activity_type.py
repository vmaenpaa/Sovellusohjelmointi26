from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.activity_type import ActivityType
from app.models.activity_type_unit_type import ActivityTypeUnitType


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


def get_visible_to_user(
    db: Session,
    user_id: int,
    activity_type_id: int,
) -> ActivityType | None:
    return db.scalar(
        select(ActivityType).where(
            ActivityType.id == activity_type_id,
            or_(
                ActivityType.is_system.is_(True),
                ActivityType.user_id == user_id,
            ),
        )
    )


def list_visible_to_user(db: Session, user_id: int) -> list[ActivityType]:
    statement = (
        select(ActivityType)
        .where(
            or_(
                ActivityType.is_system.is_(True),
                ActivityType.user_id == user_id,
            )
        )
        .options(
            selectinload(ActivityType.unit_links).selectinload(
                ActivityTypeUnitType.unit_type
            )
        )
        .order_by(ActivityType.is_system.desc(), ActivityType.name)
    )
    return list(db.scalars(statement).all())


def get_custom_by_slug(
    db: Session,
    user_id: int,
    slug: str,
) -> ActivityType | None:
    return db.scalar(
        select(ActivityType).where(
            ActivityType.user_id == user_id,
            ActivityType.is_system.is_(False),
            ActivityType.slug == slug,
        )
    )


def create_custom(
    db: Session,
    *,
    user_id: int,
    name: str,
    slug: str,
) -> ActivityType:
    activity_type = ActivityType(
        name=name,
        slug=slug,
        is_system=False,
        user_id=user_id,
    )
    db.add(activity_type)
    db.flush()
    return activity_type