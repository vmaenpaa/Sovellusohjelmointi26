from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest, TokenResponse, UserCreate, UserPublic
from app.services.auth import (
	DuplicateEmailError,
	InvalidCredentialsError,
	login_user,
	register_user,
)


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


@router.post("/login", response_model=TokenResponse, tags=["auth"])
def login(user_data: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
	try:
		return login_user(db, user_data)
	except InvalidCredentialsError as error:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail=str(error),
		) from error


@router.get("/me", response_model=UserPublic, tags=["auth"])
def me(current_user: User = Depends(get_current_user)) -> UserPublic:
	return UserPublic(
		id=current_user.id,
		email=current_user.email,
		display_name=current_user.display_name,
	)
