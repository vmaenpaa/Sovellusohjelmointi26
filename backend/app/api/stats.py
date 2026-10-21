from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.stats import StatsSummary
from app.services.stats import get_summary

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/summary", response_model=StatsSummary)
def read_summary(
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StatsSummary:
    if (
        session_from is not None
        and session_to is not None
        and session_from > session_to
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="from must not be after to",
        )
    return get_summary(
        db,
        current_user.id,
        session_from=session_from,
        session_to=session_to,
    )
