from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.plan import PlanCreate, PlanDetail, PlanRead, PlanUpdate
from app.schemas.session import SessionRead
from app.services.ownership import PlanNotFoundError, SessionNotFoundError
from app.services.plans import (
	attach_session,
	create_plan,
	delete_plan,
	detach_session,
	get_plan,
	list_plans,
	update_plan,
)
from app.services.sessions import get_session


router = APIRouter(prefix="/plans", tags=["plans"])


def _not_found(error: PlanNotFoundError | SessionNotFoundError) -> HTTPException:
	detail = {
		PlanNotFoundError: "Plan not found",
		SessionNotFoundError: "Session not found",
	}[type(error)]
	return HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=detail,
	)


@router.post("", response_model=PlanRead, status_code=status.HTTP_201_CREATED)
def create_user_plan(
	plan_data: PlanCreate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> PlanRead:
	plan = create_plan(db, current_user.id, plan_data)
	db.commit()
	return plan


@router.get("", response_model=list[PlanRead])
def list_user_plans(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> list[PlanRead]:
	return list_plans(db, current_user.id)


@router.get("/{plan_id}", response_model=PlanDetail)
def get_user_plan(
	plan_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> PlanDetail:
	try:
		return get_plan(db, current_user.id, plan_id)
	except PlanNotFoundError as error:
		raise _not_found(error) from error


@router.patch("/{plan_id}", response_model=PlanRead)
def update_user_plan(
	plan_id: int,
	plan_data: PlanUpdate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> PlanRead:
	try:
		plan = update_plan(db, current_user.id, plan_id, plan_data)
		db.commit()
	except PlanNotFoundError as error:
		db.rollback()
		raise _not_found(error) from error
	except Exception:
		db.rollback()
		raise

	return plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_plan(
	plan_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> None:
	try:
		delete_plan(db, current_user.id, plan_id)
		db.commit()
	except PlanNotFoundError as error:
		db.rollback()
		raise _not_found(error) from error
	except Exception:
		db.rollback()
		raise


@router.post(
	"/{plan_id}/sessions/{session_id}",
	response_model=SessionRead,
)
def attach_user_session(
	plan_id: int,
	session_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> SessionRead:
	try:
		session = attach_session(db, current_user.id, plan_id, session_id)
		db.commit()
	except (PlanNotFoundError, SessionNotFoundError) as error:
		db.rollback()
		raise _not_found(error) from error
	except Exception:
		db.rollback()
		raise

	return get_session(db, current_user.id, session.id)


@router.delete(
	"/{plan_id}/sessions/{session_id}",
	status_code=status.HTTP_204_NO_CONTENT,
)
def detach_user_session(
	plan_id: int,
	session_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> None:
	try:
		detach_session(db, current_user.id, plan_id, session_id)
		db.commit()
	except (PlanNotFoundError, SessionNotFoundError) as error:
		db.rollback()
		raise _not_found(error) from error
	except Exception:
		db.rollback()
		raise
