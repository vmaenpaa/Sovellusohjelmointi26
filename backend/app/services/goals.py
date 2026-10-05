from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.goal import Goal
from app.repositories.activity_type import get_visible_to_user
from app.repositories.goal import list_for_user
from app.repositories.unit_type import get_by_id as get_unit_type_by_id
from app.schemas.goal import GoalCreate, GoalUpdate
from app.services.ownership import load_goal_for_user


class GoalValidationError(ValueError):
	pass


def _validate_refs(
	db: Session,
	user_id: int,
	unit_type_id: int,
	activity_type_id: int | None,
) -> None:
	if get_unit_type_by_id(db, unit_type_id) is None:
		raise GoalValidationError("Unknown unit_type_id")
	if activity_type_id is not None:
		if get_visible_to_user(db, user_id, activity_type_id) is None:
			raise GoalValidationError("Unknown activity_type_id")


def list_goals(
	db: Session,
	user_id: int,
	*,
	active: bool | None = None,
) -> list[Goal]:
	return list_for_user(db, user_id, active=active)


def get_goal(db: Session, user_id: int, goal_id: int) -> Goal:
	return load_goal_for_user(db, goal_id, user_id)


def create_goal(db: Session, user_id: int, goal_data: GoalCreate) -> Goal:
	_validate_refs(db, user_id, goal_data.unit_type_id, goal_data.activity_type_id)

	goal = Goal(
		user_id=user_id,
		unit_type_id=goal_data.unit_type_id,
		activity_type_id=goal_data.activity_type_id,
		target_value=goal_data.target_value,
		period=goal_data.period,
		active=goal_data.active,
		created_at=datetime.now(timezone.utc),
	)
	db.add(goal)
	db.flush()
	return goal


def update_goal(
	db: Session,
	user_id: int,
	goal_id: int,
	goal_data: GoalUpdate,
) -> Goal:
	goal = load_goal_for_user(db, goal_id, user_id)

	updated_fields = goal_data.model_fields_set

	if "unit_type_id" in updated_fields or "activity_type_id" in updated_fields:
		unit_type_id = (
			goal_data.unit_type_id
			if "unit_type_id" in updated_fields
			else goal.unit_type_id
		)
		activity_type_id = (
			goal_data.activity_type_id
			if "activity_type_id" in updated_fields
			else goal.activity_type_id
		)
		_validate_refs(db, user_id, unit_type_id, activity_type_id)

	if "unit_type_id" in updated_fields:
		goal.unit_type_id = goal_data.unit_type_id
	if "activity_type_id" in updated_fields:
		goal.activity_type_id = goal_data.activity_type_id
	if "target_value" in updated_fields:
		goal.target_value = goal_data.target_value
	if "period" in updated_fields:
		goal.period = goal_data.period
	if "active" in updated_fields:
		goal.active = goal_data.active

	db.flush()
	return goal


def delete_goal(db: Session, user_id: int, goal_id: int) -> None:
	goal = load_goal_for_user(db, goal_id, user_id)

	db.delete(goal)
	db.flush()
