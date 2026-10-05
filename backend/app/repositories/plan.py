from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.workout_plan import WorkoutPlan
from app.models.workout_session import WorkoutSession


def get_plan_for_user(
    db: Session,
    user_id: int,
    plan_id: int,
) -> WorkoutPlan | None:
    return db.scalar(
        select(WorkoutPlan)
        .where(
            WorkoutPlan.id == plan_id,
            WorkoutPlan.user_id == user_id,
        )
    )


def get_plan_with_sessions_for_user(
    db: Session,
    user_id: int,
    plan_id: int,
) -> WorkoutPlan | None:
    return db.scalar(
        select(WorkoutPlan)
        .where(
            WorkoutPlan.id == plan_id,
            WorkoutPlan.user_id == user_id,
        )
        .options(
            selectinload(
                WorkoutPlan.sessions.and_(WorkoutSession.user_id == user_id)
            )
        )
    )


def list_for_user(
    db: Session,
    user_id: int,
) -> list[WorkoutPlan]:
    return list(
        db.scalars(
            select(WorkoutPlan)
            .where(WorkoutPlan.user_id == user_id)
            .order_by(WorkoutPlan.created_at.desc())
        ).all()
    )
