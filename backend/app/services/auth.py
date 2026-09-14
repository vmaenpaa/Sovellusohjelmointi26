from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user import create_user, get_by_email
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate


class DuplicateEmailError(ValueError):
	pass


class InvalidCredentialsError(ValueError):
	pass


def register_user(db: Session, user_data: UserCreate) -> User:
	if get_by_email(db, user_data.email) is not None:
		raise DuplicateEmailError("A user with this email already exists")

	password_hash = hash_password(user_data.password)
	return create_user(
		db,
		email=user_data.email,
		password_hash=password_hash,
		display_name=user_data.display_name,
	)


def login_user(db: Session, user_data: LoginRequest) -> TokenResponse:
	user = get_by_email(db, user_data.email)
	if user is None or not verify_password(user_data.password, user.password_hash):
		raise InvalidCredentialsError("Invalid email or password")

	return TokenResponse(access_token=create_access_token(user.id))
