from datetime import datetime

from sqlalchemy.orm import Session

from app.models.workout_session import WorkoutSession
from app.repositories.session import list_scheduled_in_range
from app.services.analytics import (
    MeasurementInput,
    SessionInput,
    SessionItemInput,
    summarize_sessions,
)


def _to_input(session: WorkoutSession) -> SessionInput:
    return SessionInput(
        session_at=session.session_at,
        intensity=session.intensity,
        status=session.status,
        items=tuple(
            SessionItemInput(
                activity_type_slug=item.activity_type.slug,
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
