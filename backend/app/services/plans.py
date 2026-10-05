from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.workout_plan import WorkoutPlan
from app.models.workout_session import WorkoutSession
from app.repositories.plan import list_for_user
from app.schemas.plan import PlanCreate, PlanUpdate
from app.services.ownership import (
	SessionNotFoundError,
	load_plan_for_user,
	load_plan_with_sessions_for_user,
	load_session_for_user,
)


def create_plan(
	db: Session,
	user_id: int,
	plan_data: PlanCreate,
) -> WorkoutPlan:
	now = datetime.now(timezone.utc)
	plan = WorkoutPlan(
		user_id=user_id,
		name=plan_data.name,
		notes=plan_data.notes,
		start_date=plan_data.start_date,
		length_weeks=plan_data.length_weeks,
		created_at=now,
		updated_at=now,
	)
	db.add(plan)
	db.flush()
	return plan


def get_plan(
	db: Session,
	user_id: int,
	plan_id: int,
) -> WorkoutPlan:
	return load_plan_with_sessions_for_user(db, plan_id, user_id)


def list_plans(
	db: Session,
	user_id: int,
) -> list[WorkoutPlan]:
	return list_for_user(db, user_id)


def update_plan(
	db: Session,
	user_id: int,
	plan_id: int,
	plan_data: PlanUpdate,
) -> WorkoutPlan:
	plan = load_plan_for_user(db, plan_id, user_id)

	updated_fields = plan_data.model_fields_set
	if "name" in updated_fields:
		plan.name = plan_data.name
	if "notes" in updated_fields:
		plan.notes = plan_data.notes
	if "start_date" in updated_fields:
		plan.start_date = plan_data.start_date
	if "length_weeks" in updated_fields:
		plan.length_weeks = plan_data.length_weeks
	plan.updated_at = datetime.now(timezone.utc)

	db.flush()
	return plan


def delete_plan(
	db: Session,
	user_id: int,
	plan_id: int,
) -> None:
	plan = load_plan_for_user(db, plan_id, user_id)

	db.delete(plan)
	db.flush()


def attach_session(
	db: Session,
	user_id: int,
	plan_id: int,
	session_id: int,
) -> WorkoutSession:
	plan = load_plan_for_user(db, plan_id, user_id)

	session = load_session_for_user(db, session_id, user_id)

	session.plan_id = plan_id
	session.updated_at = datetime.now(timezone.utc)

	db.flush()
	return session


def detach_session(
	db: Session,
	user_id: int,
	plan_id: int,
	session_id: int,
) -> None:
	plan = load_plan_for_user(db, plan_id, user_id)

	session = load_session_for_user(db, session_id, user_id)
	if session.plan_id != plan_id:
		raise SessionNotFoundError

	session.plan_id = None
	session.updated_at = datetime.now(timezone.utc)

	db.flush()
