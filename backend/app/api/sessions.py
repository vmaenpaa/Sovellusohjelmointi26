from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.session import SessionCreate, SessionRead, SessionUpdate
from app.services.sessions import (
	PlanNotFoundError,
	SessionItemValidationError,
	SessionNotFoundError,
	create_session,
	delete_session,
	get_session,
	list_sessions,
	update_session,
)


router = APIRouter(prefix="/sessions", tags=["sessions"])


def _not_found(error: ValueError) -> HTTPException:
	return HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail=str(error),
	)


def _unprocessable_entity(error: ValueError) -> HTTPException:
	return HTTPException(
		status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
		detail=str(error),
	)


@router.get("", response_model=list[SessionRead])
def list_user_sessions(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> list[SessionRead]:
	return list_sessions(db, current_user.id)


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


@router.get("/{session_id}", response_model=SessionRead)
def get_user_session(
	session_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> SessionRead:
	session = get_session(db, current_user.id, session_id)
	if session is None:
		raise HTTPException(status_code=404, detail="Session not found")
	return session


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
