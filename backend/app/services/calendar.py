from datetime import datetime

from sqlalchemy.orm import Session

from app.models.workout_session import WorkoutSession
from app.services.sessions import list_sessions


def get_calendar_sessions(
	db: Session,
	user_id: int,
	*,
	session_from: datetime | None = None,
	session_to: datetime | None = None,
	plan_id: int | None = None,
) -> list[WorkoutSession]:
	sessions = list_sessions(
		db,
		user_id,
		session_from=session_from,
		session_to=session_to,
		unscheduled=False,
		plan_id=plan_id,
	)
	return sorted(sessions, key=lambda session: session.session_at)
