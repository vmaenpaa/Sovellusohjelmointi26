from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.activity_type import ActivityTypeCreate, ActivityTypeRead
from app.services.activity_types import (
	ActivityTypeConflictError,
	ActivityTypeValidationError,
	create_activity_type,
	list_activity_types,
)


router = APIRouter(prefix="/activity-types", tags=["activity-types"])


@router.get("", response_model=list[ActivityTypeRead])
def get_activity_types(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> list[ActivityTypeRead]:
	return list_activity_types(db, current_user.id)


@router.post(
	"",
	response_model=ActivityTypeRead,
	status_code=status.HTTP_201_CREATED,
)
def post_activity_type(
	activity_type_data: ActivityTypeCreate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> ActivityTypeRead:
	try:
		activity_type = create_activity_type(
			db,
			current_user.id,
			activity_type_data,
		)
		db.commit()
		return activity_type
	except ActivityTypeConflictError as error:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail=str(error),
		) from error
	except ActivityTypeValidationError as error:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail=str(error),
		) from error
	except Exception:
		db.rollback()
		raise
