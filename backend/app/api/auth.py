from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.session import get_db
from app.schemas.auth import AuthResponse, UserCreate, UserPublic
from app.services.auth import DuplicateEmailError, register_user


router = APIRouter(prefix="/auth")


@router.post(
	"/register",
	response_model=AuthResponse,
	status_code=status.HTTP_201_CREATED,
	tags=["auth"],
)
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> AuthResponse:
	try:
		user = register_user(db, user_data)
	except DuplicateEmailError as error:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=str(error),
		) from error

	try:
		db.commit()
	except Exception:
		db.rollback()
		raise

	public_user = UserPublic(
		id=user.id,
		email=user.email,
		display_name=user.display_name,
	)
	return AuthResponse(
		user=public_user,
		access_token=create_access_token(user.id),
	)
