from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.stats import (
    ProgressGranularity,
    ProgressMetric,
    ProgressSeries,
    StreakStats,
    StatsSummary,
)
from app.services.stats import (
    ActivityTypeNotFoundError,
    get_progress,
    get_streaks,
    get_summary,
)

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


@router.get(
    "/streaks",
    response_model=StreakStats,
    description=(
        "Returns current and longest consecutive-day streaks across all of the "
        "authenticated user's history. Only sessions with a non-null "
        "session_at count."
    ),
)
def read_streaks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreakStats:
    return get_streaks(db, current_user.id)


@router.get("/progress", response_model=ProgressSeries)
def read_progress(
    metric: ProgressMetric = Query(
        description=(
            "session_count (sessions per bucket) or a unit slug: duration_min, "
            "distance_km, reps, weight_kg (sum of actual values)."
        ),
    ),
    granularity: ProgressGranularity = Query(default=ProgressGranularity.week),
    activity_type_id: int | None = Query(
        default=None,
        description="Catalog activity type id; filters before bucketing.",
    ),
    session_from: datetime | None = Query(default=None, alias="from"),
    session_to: datetime | None = Query(default=None, alias="to"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProgressSeries:
    if (
        session_from is not None
        and session_to is not None
        and session_from > session_to
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="from must not be after to",
        )
    try:
        points = get_progress(
            db,
            current_user.id,
            metric=metric.value,
            granularity=granularity.value,
            activity_type_id=activity_type_id,
            session_from=session_from,
            session_to=session_to,
        )
    except ActivityTypeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return ProgressSeries(
        metric=metric,
        granularity=granularity,
        activity_type_id=activity_type_id,
        points=points,
    )
