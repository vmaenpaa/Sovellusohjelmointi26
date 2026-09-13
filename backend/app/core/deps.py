import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User


bearer_scheme = HTTPBearer(auto_error=False)


def _unauthorized() -> HTTPException:
	return HTTPException(
		status_code=401,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)


def get_current_user(
	credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
	db: Session = Depends(get_db),
) -> User:
	if credentials is None:
		raise _unauthorized()

	try:
		payload = decode_token(credentials.credentials)
		subject = payload.get("sub")
		if not isinstance(subject, str):
			raise ValueError
		user_id = int(subject)
	except (ValueError, TypeError, jwt.InvalidTokenError):
		raise _unauthorized()

	user = db.scalar(select(User).where(User.id == user_id))
	if user is None:
		raise _unauthorized()

	return user
