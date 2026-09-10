from sqlalchemy.orm import Session

from app.repositories.activity_type import get_or_create_system as get_or_create_system_activity
from app.repositories.activity_type_unit_type import get_or_create as get_or_create_link
from app.repositories.unit_type import get_or_create_system


SYSTEM_UNIT_TYPES = (
    {"name": "Duration", "slug": "duration_min", "unit_label": "min"},
    {"name": "Distance", "slug": "distance_km", "unit_label": "km"},
    {"name": "Repetitions", "slug": "reps", "unit_label": "reps"},
    {"name": "Weight", "slug": "weight_kg", "unit_label": "kg"},
)

SYSTEM_ACTIVITY_TYPES = (
    {"name": "Running", "slug": "running"},
    {"name": "Cycling", "slug": "cycling"},
    {"name": "Bench Press", "slug": "bench_press"},
    {"name": "Barbell Curl", "slug": "barbell_curl"},
    {"name": "Hammer Curl", "slug": "hammer_curl"},
    {"name": "Incline Curl", "slug": "incline_curl"},
    {"name": "Face Pull", "slug": "face_pull"},
    {"name": "Other", "slug": "other"},
)

SYSTEM_ACTIVITY_UNIT_LINKS = (
    ("running", "duration_min", False),
    ("running", "distance_km", False),
    ("cycling", "duration_min", False),
    ("cycling", "distance_km", False),
    ("bench_press", "reps", True),
    ("bench_press", "weight_kg", True),
    ("barbell_curl", "reps", True),
    ("barbell_curl", "weight_kg", True),
    ("hammer_curl", "reps", True),
    ("hammer_curl", "weight_kg", True),
    ("incline_curl", "reps", True),
    ("incline_curl", "weight_kg", True),
    ("face_pull", "reps", True),
    ("face_pull", "weight_kg", True),
    ("other", "duration_min", False),
)


def seed_system_unit_types(db: Session) -> list:
    return [
        get_or_create_system(db, **unit_type_data)
        for unit_type_data in SYSTEM_UNIT_TYPES
    ]


def seed_system_activity_types(db: Session) -> list:
    return [
        get_or_create_system_activity(db, **activity_type_data)
        for activity_type_data in SYSTEM_ACTIVITY_TYPES
    ]


def seed_system_activity_unit_links(
    db: Session,
    activity_types: list,
    unit_types: list,
) -> list:
    activities_by_slug = {activity.slug: activity for activity in activity_types}
    units_by_slug = {unit.slug: unit for unit in unit_types}
    links = []

    for sort_order, (activity_slug, unit_slug, per_set) in enumerate(
        SYSTEM_ACTIVITY_UNIT_LINKS
    ):
        links.append(
            get_or_create_link(
                db,
                activity_type_id=activities_by_slug[activity_slug].id,
                unit_type_id=units_by_slug[unit_slug].id,
                sort_order=sort_order,
                is_required=True,
                per_set=per_set,
            )
        )
    return links