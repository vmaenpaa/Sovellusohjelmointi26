from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity_type import ActivityType
from app.models.activity_type_unit_type import ActivityTypeUnitType
from app.models.workout_plan import WorkoutPlan
from app.models.workout_session import WorkoutSession
from app.models.workout_session_item import WorkoutSessionItem
from app.models.workout_session_measurement import WorkoutSessionMeasurement
from app.repositories.session import get_by_id, list_for_user
from app.schemas.session import SessionUpdate


class PlanNotFoundError(ValueError):
	pass


class SessionNotFoundError(ValueError):
	pass


class SessionItemValidationError(ValueError):
	pass


class ActivityTypeNotFoundError(SessionItemValidationError):
	pass


def _get_owned_plan(
	db: Session,
	user_id: int,
	plan_id: int | None,
) -> WorkoutPlan | None:
	if plan_id is None:
		return None

	plan = db.scalar(
		select(WorkoutPlan).where(
			WorkoutPlan.id == plan_id,
			WorkoutPlan.user_id == user_id,
		)
	)
	if plan is None:
		raise PlanNotFoundError("Plan not found")
	return plan


def _add_items(db: Session, session: WorkoutSession, items: list) -> None:
	for item_data in items:
		activity_type = db.get(ActivityType, item_data.activity_type_id)
		if activity_type is None:
			raise ActivityTypeNotFoundError("Activity type not found")
		unit_links = {
			link.unit_type_id: link
			for link in activity_type.unit_links
		}
		for measurement in item_data.measurements:
			unit_link = unit_links.get(measurement.unit_type_id)
			if unit_link is None:
				raise SessionItemValidationError(
					"Unit type is not linked to the activity type"
				)
			if unit_link.per_set and measurement.set_index is None:
				raise SessionItemValidationError(
					"set_index is required for per-set measurements"
				)

		item = WorkoutSessionItem(
			activity_type_id=item_data.activity_type_id,
			sort_order=item_data.sort_order,
			notes=item_data.notes,
		)
		item.measurements = [
			WorkoutSessionMeasurement(
				unit_type_id=measurement.unit_type_id,
				planned_value=measurement.planned_value,
				actual_value=measurement.actual_value,
				set_index=measurement.set_index,
			)
			for measurement in item_data.measurements
		]
		session.items.append(item)


def create_session(
	db: Session,
	user_id: int,
	session_data,
) -> WorkoutSession:
	_get_owned_plan(db, user_id, session_data.plan_id)

	now = datetime.now(timezone.utc)
	session = WorkoutSession(
		user_id=user_id,
		plan_id=session_data.plan_id,
		name=session_data.name,
		session_at=session_data.session_at,
		status=session_data.status.value,
		notes=session_data.notes,
		intensity=session_data.intensity,
		created_at=now,
		updated_at=now,
	)
	_add_items(db, session, session_data.items)
	db.add(session)
	db.flush()
	return session


def get_session(
	db: Session,
	user_id: int,
	session_id: int,
) -> WorkoutSession | None:
	return get_by_id(db, user_id, session_id)


def list_sessions(
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
	return list_for_user(
		db,
		user_id,
		session_from=session_from,
		session_to=session_to,
		status=status,
		activity_type_id=activity_type_id,
		unscheduled=unscheduled,
		plan_id=plan_id,
	)


def update_session(
	db: Session,
	user_id: int,
	session_id: int,
	session_data: SessionUpdate,
) -> WorkoutSession:
	session = get_by_id(db, user_id, session_id)
	if session is None:
		raise SessionNotFoundError("Session not found")

	updated_fields = session_data.model_fields_set
	if "plan_id" in updated_fields:
		_get_owned_plan(db, user_id, session_data.plan_id)
		session.plan_id = session_data.plan_id
	if "name" in updated_fields:
		session.name = session_data.name
	if "session_at" in updated_fields:
		session.session_at = session_data.session_at
	if "status" in updated_fields:
		session.status = session_data.status.value
	if "notes" in updated_fields:
		session.notes = session_data.notes
	if "intensity" in updated_fields:
		session.intensity = session_data.intensity
	if "items" in updated_fields:
		session.items.clear()
		_add_items(db, session, session_data.items)
	session.updated_at = datetime.now(timezone.utc)

	db.flush()
	return session


def delete_session(
	db: Session,
	user_id: int,
	session_id: int,
) -> None:
	session = get_by_id(db, user_id, session_id)
	if session is None:
		raise SessionNotFoundError("Session not found")

	db.delete(session)
	db.flush()
