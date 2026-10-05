from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalRead, GoalUpdate
from app.services.ownership import GoalNotFoundError
from app.services.goals import (
	GoalValidationError,
	create_goal,
	delete_goal,
	get_goal,
	list_goals,
	update_goal,
)


router = APIRouter(prefix="/goals", tags=["goals"])


def _not_found(error: GoalNotFoundError) -> HTTPException:
	return HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail="Goal not found",
	)


def _unprocessable_entity(error: ValueError) -> HTTPException:
	return HTTPException(
		status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
		detail=str(error),
	)


@router.get("", response_model=list[GoalRead])
def list_user_goals(
	active: bool | None = Query(default=None),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> list[GoalRead]:
	return list_goals(db, current_user.id, active=active)


@router.post("", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def post_goal(
	goal_data: GoalCreate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> GoalRead:
	try:
		goal = create_goal(db, current_user.id, goal_data)
		db.commit()
	except GoalValidationError as error:
		db.rollback()
		raise _unprocessable_entity(error) from error
	except Exception:
		db.rollback()
		raise

	return goal


@router.get("/{goal_id}", response_model=GoalRead)
def get_user_goal(
	goal_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> GoalRead:
	try:
		return get_goal(db, current_user.id, goal_id)
	except GoalNotFoundError as error:
		raise _not_found(error) from error


@router.patch("/{goal_id}", response_model=GoalRead)
def patch_goal(
	goal_id: int,
	goal_data: GoalUpdate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> GoalRead:
	try:
		goal = update_goal(db, current_user.id, goal_id, goal_data)
		db.commit()
	except GoalNotFoundError as error:
		db.rollback()
		raise _not_found(error) from error
	except GoalValidationError as error:
		db.rollback()
		raise _unprocessable_entity(error) from error
	except Exception:
		db.rollback()
		raise

	return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_goal(
	goal_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> Response:
	try:
		delete_goal(db, current_user.id, goal_id)
		db.commit()
	except GoalNotFoundError as error:
		db.rollback()
		raise _not_found(error) from error
	except Exception:
		db.rollback()
		raise

	return Response(status_code=status.HTTP_204_NO_CONTENT)
