from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.session import (
	SessionClone,
	SessionCreate,
	SessionRead,
	SessionStatus,
	SessionUpdate,
)
from app.services.ownership import PlanNotFoundError, SessionNotFoundError
from app.services.sessions import (
	SessionItemValidationError,
	clone_session,
	create_session,
	delete_session,
	get_session,
	list_sessions,
	update_session,
)


router = APIRouter(prefix="/sessions", tags=["sessions"])


def _not_found(error: PlanNotFoundError | SessionNotFoundError) -> HTTPException:
	detail = {
		SessionNotFoundError: "Session not found",
		PlanNotFoundError: "Plan not found",
	}[type(error)]
	return HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=detail,
	)


def _unprocessable_entity(error: ValueError) -> HTTPException:
	return HTTPException(
		status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
		detail=str(error),
	)


@router.get("", response_model=list[SessionRead])
def list_user_sessions(
	session_from: datetime | None = Query(
		default=None,
		alias="from",
		description="Include sessions at or after this date and time.",
	),
	session_to: datetime | None = Query(
		default=None,
		alias="to",
		description="Include sessions at or before this date and time.",
	),
	session_status: SessionStatus | None = Query(
		default=None,
		alias="status",
		description="Filter by exact session status.",
	),
	activity_type_id: int | None = Query(
		default=None,
		description="Include sessions containing at least one item of this activity type.",
	),
	unscheduled: bool | None = Query(
		default=None,
		description=(
			"True selects undated sessions and ignores from/to; false selects "
			"dated sessions and applies any supplied date bounds."
		),
	),
	plan_id: int | None = Query(
		default=None,
		description="Filter by plan ID.",
	),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> list[SessionRead]:
	if (
		session_from is not None
		and session_to is not None
		and session_from > session_to
	):
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="from must not be after to",
		)

	return list_sessions(
		db,
		current_user.id,
		session_from=session_from,
		session_to=session_to,
		status=session_status.value if session_status is not None else None,
		activity_type_id=activity_type_id,
		unscheduled=unscheduled,
		plan_id=plan_id,
	)


@router.post(
	"",
	response_model=SessionRead,
	status_code=status.HTTP_201_CREATED,
)
def create_user_session(
	session_data: SessionCreate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> SessionRead:
	try:
		session = create_session(db, current_user.id, session_data)
		db.commit()
	except PlanNotFoundError as error:
		db.rollback()
		raise _not_found(error) from error
	except SessionItemValidationError as error:
		db.rollback()
		raise _unprocessable_entity(error) from error
	except Exception:
		db.rollback()
		raise

	return get_session(db, current_user.id, session.id)


@router.post(
	"/{session_id}/clone",
	response_model=SessionRead,
	status_code=status.HTTP_201_CREATED,
)
def clone_user_session(
	session_id: int,
	session_data: SessionClone | None = None,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> SessionRead:
	try:
		session = clone_session(
			db,
			current_user.id,
			session_id,
			session_data or SessionClone(),
		)
		db.commit()
	except (PlanNotFoundError, SessionNotFoundError) as error:
		db.rollback()
		raise _not_found(error) from error
	except Exception:
		db.rollback()
		raise

	return get_session(db, current_user.id, session.id)


@router.get("/{session_id}", response_model=SessionRead)
def get_user_session(
	session_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> SessionRead:
	try:
		return get_session(db, current_user.id, session_id)
	except SessionNotFoundError as error:
		raise _not_found(error) from error


@router.patch("/{session_id}", response_model=SessionRead)
def update_user_session(
	session_id: int,
	session_data: SessionUpdate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> SessionRead:
	try:
		session = update_session(
			db,
			current_user.id,
			session_id,
			session_data,
		)
		db.commit()
	except (PlanNotFoundError, SessionNotFoundError) as error:
		db.rollback()
		raise _not_found(error) from error
	except SessionItemValidationError as error:
		db.rollback()
		raise _unprocessable_entity(error) from error
	except Exception:
		db.rollback()
		raise

	return get_session(db, current_user.id, session.id)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_session(
	session_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> Response:
	try:
		delete_session(db, current_user.id, session_id)
		db.commit()
	except SessionNotFoundError as error:
		db.rollback()
		raise _not_found(error) from error
	except Exception:
		db.rollback()
		raise

	return Response(status_code=status.HTTP_204_NO_CONTENT)
