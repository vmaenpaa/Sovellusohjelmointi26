from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.workout_session import WorkoutSession
from app.models.workout_session_item import WorkoutSessionItem


def get_session_for_user(
    db: Session,
    user_id: int,
    session_id: int,
) -> WorkoutSession | None:
    return db.scalar(
        select(WorkoutSession)
        .where(
            WorkoutSession.id == session_id,
            WorkoutSession.user_id == user_id,
        )
        .options(
            selectinload(WorkoutSession.items).selectinload(
                WorkoutSessionItem.measurements
            )
        )
    )


def list_for_user(
    db: Session,
    user_id: int,
    *,
    session_from: datetime | None = None,
    session_to: datetime | None = None,
    status: str | None = None,
    activity_type_id: int | None = None,
    unscheduled: bool | None = None,
    plan_id: int | None = None,
) -> list[WorkoutSession]:
    statement = select(WorkoutSession).where(
        WorkoutSession.user_id == user_id,
    )

    if unscheduled is True:
        statement = statement.where(WorkoutSession.session_at.is_(None))
    else:
        if unscheduled is False:
            statement = statement.where(WorkoutSession.session_at.is_not(None))
        if session_from is not None:
            statement = statement.where(WorkoutSession.session_at >= session_from)
        if session_to is not None:
            statement = statement.where(WorkoutSession.session_at <= session_to)

    if status is not None:
        statement = statement.where(WorkoutSession.status == status)
    if activity_type_id is not None:
        statement = statement.where(
            WorkoutSession.items.any(
                WorkoutSessionItem.activity_type_id == activity_type_id
            )
        )
    if plan_id is not None:
        statement = statement.where(WorkoutSession.plan_id == plan_id)

    return list(
        db.scalars(
            statement
            .order_by(WorkoutSession.created_at.desc())
            .options(
                selectinload(WorkoutSession.items).selectinload(
                    WorkoutSessionItem.measurements
                )
            )
        ).all()
    )