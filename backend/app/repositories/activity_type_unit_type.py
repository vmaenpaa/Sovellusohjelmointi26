from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity_type_unit_type import ActivityTypeUnitType


def get_or_create(
    db: Session,
    *,
    activity_type_id: int,
    unit_type_id: int,
    sort_order: int,
    is_required: bool,
    per_set: bool,
) -> ActivityTypeUnitType:
    link = db.scalar(
        select(ActivityTypeUnitType).where(
            ActivityTypeUnitType.activity_type_id == activity_type_id,
            ActivityTypeUnitType.unit_type_id == unit_type_id,
        )
    )
    if link is None:
        link = ActivityTypeUnitType(
            activity_type_id=activity_type_id,
            unit_type_id=unit_type_id,
            sort_order=sort_order,
            is_required=is_required,
            per_set=int(per_set),
        )
        db.add(link)
    return link