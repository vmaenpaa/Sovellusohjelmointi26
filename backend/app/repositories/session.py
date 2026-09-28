from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.workout_session import WorkoutSession
from app.models.workout_session_item import WorkoutSessionItem


def get_by_id(
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
) -> list[WorkoutSession]:
    return list(
        db.scalars(
            select(WorkoutSession)
            .where(WorkoutSession.user_id == user_id)
            .order_by(WorkoutSession.created_at.desc())
            .options(
                selectinload(WorkoutSession.items).selectinload(
                    WorkoutSessionItem.measurements
                )
            )
        ).all()
    )