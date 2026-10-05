from sqlalchemy.orm import Session

from app.models.goal import Goal
from app.models.workout_plan import WorkoutPlan
from app.models.workout_session import WorkoutSession
from app.repositories.goal import get_goal_for_user
from app.repositories.plan import (
	get_plan_for_user,
	get_plan_with_sessions_for_user,
)
from app.repositories.session import get_session_for_user


class SessionNotFoundError(ValueError):
	pass


class PlanNotFoundError(ValueError):
	pass


class GoalNotFoundError(ValueError):
	pass


def load_session_for_user(
	db: Session,
	session_id: int,
	user_id: int,
) -> WorkoutSession:
	session = get_session_for_user(db, user_id, session_id)
	if session is None:
		raise SessionNotFoundError
	return session


def load_plan_for_user(
	db: Session,
	plan_id: int,
	user_id: int,
) -> WorkoutPlan:
	plan = get_plan_for_user(db, user_id, plan_id)
	if plan is None:
		raise PlanNotFoundError
	return plan


def load_plan_with_sessions_for_user(
	db: Session,
	plan_id: int,
	user_id: int,
) -> WorkoutPlan:
	plan = get_plan_with_sessions_for_user(db, user_id, plan_id)
	if plan is None:
		raise PlanNotFoundError
	return plan


def load_goal_for_user(
	db: Session,
	goal_id: int,
	user_id: int,
) -> Goal:
	goal = get_goal_for_user(db, user_id, goal_id)
	if goal is None:
		raise GoalNotFoundError
	return goal
