from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.repositories.user import create_user, get_by_email
from app.schemas.auth import UserCreate


class DuplicateEmailError(ValueError):
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
