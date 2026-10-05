from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.calendar import CalendarSessionRead
from app.services.calendar import get_calendar_sessions


router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("", response_model=list[CalendarSessionRead])
def get_user_calendar(
	session_from: datetime | None = Query(default=None, alias="from"),
	session_to: datetime | None = Query(default=None, alias="to"),
	plan_id: int | None = Query(default=None),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> list[CalendarSessionRead]:
	if (
		session_from is not None
		and session_to is not None
		and session_from > session_to
	):
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="from must not be after to",
		)

	return get_calendar_sessions(
		db,
		current_user.id,
		session_from=session_from,
		session_to=session_to,
		plan_id=plan_id,
	)
