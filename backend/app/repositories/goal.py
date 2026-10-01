from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.goal import Goal


def get_by_id(db: Session, user_id: int, goal_id: int) -> Goal | None:
    return db.scalar(
        select(Goal).where(
            Goal.id == goal_id,
            Goal.user_id == user_id,
        )
    )


def list_for_user(
    db: Session,
    user_id: int,
    *,
    active: bool | None = None,
) -> list[Goal]:
    statement = select(Goal).where(Goal.user_id == user_id)

    if active is not None:
        statement = statement.where(Goal.active == active)

    statement = statement.order_by(Goal.created_at.desc())
    return list(db.scalars(statement).all())
