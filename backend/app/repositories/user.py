from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_by_email(db: Session, email: str) -> User | None:
	return db.scalar(select(User).where(User.email == email))


def create_user(
	db: Session,
	*,
	email: str,
	password_hash: str,
	display_name: str,
) -> User:
	user = User(
		email=email,
		password_hash=password_hash,
		display_name=display_name,
		created_at=datetime.now(timezone.utc)
		.isoformat(timespec="microseconds")
		.replace("+00:00", "Z"),
	)
	db.add(user)
	return user
