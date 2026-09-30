from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.workout_plan import WorkoutPlan


def get_by_id(
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
        .options(selectinload(WorkoutPlan.sessions))
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
