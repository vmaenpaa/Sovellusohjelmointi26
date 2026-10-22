from datetime import datetime

from sqlalchemy.orm import Session

from app.models.workout_session import WorkoutSession
from app.repositories.activity_type import get_visible_to_user
from app.repositories.session import list_scheduled_in_range
from app.services.analytics import (
    Granularity,
    MeasurementInput,
    Metric,
    SessionInput,
    SessionItemInput,
    build_series,
    build_streaks,
    summarize_sessions,
)


class ActivityTypeNotFoundError(ValueError):
    pass


def _to_input(session: WorkoutSession) -> SessionInput:
    return SessionInput(
        session_at=session.session_at,
        intensity=session.intensity,
        status=session.status,
        items=tuple(
            SessionItemInput(
                activity_type_slug=item.activity_type.slug,
                activity_type_id=item.activity_type_id,
                measurements=tuple(
                    MeasurementInput(
                        unit_slug=m.unit_type.slug,
                        actual_value=m.actual_value,
                        planned_value=m.planned_value,
                        set_index=m.set_index,
                    )
                    for m in item.measurements
                ),
            )
            for item in session.items
        ),
    )


def get_summary(
    db: Session,
    user_id: int,
    *,
    session_from: datetime | None = None,
    session_to: datetime | None = None,
) -> dict:
    sessions = list_scheduled_in_range(
        db, user_id, session_from=session_from, session_to=session_to
    )
    return summarize_sessions([_to_input(s) for s in sessions])


def get_streaks(db: Session, user_id: int) -> dict[str, int]:
    sessions = list_scheduled_in_range(db, user_id)
    return build_streaks([_to_input(session) for session in sessions])


def get_progress(
    db: Session,
    user_id: int,
    *,
    metric: Metric,
    granularity: Granularity,
    activity_type_id: int | None = None,
    session_from: datetime | None = None,
    session_to: datetime | None = None,
) -> list[dict]:
    if (
        activity_type_id is not None
        and get_visible_to_user(db, user_id, activity_type_id) is None
    ):
        raise ActivityTypeNotFoundError(f"Unknown activity_type_id: {activity_type_id}")
    sessions = list_scheduled_in_range(
        db, user_id, session_from=session_from, session_to=session_to
    )
    return build_series(
        [_to_input(s) for s in sessions],
        metric,
        granularity,
        activity_type_id=activity_type_id,
    )
