import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

from app.core.config import Settings


ALGORITHM = "HS256"


def hash_password(plain: str) -> str:
	return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, password_hash: str) -> bool:
	return bcrypt.checkpw(plain.encode("utf-8"), password_hash.encode("utf-8"))

def create_access_token(subject: int) -> str:
	settings = Settings()
	expires_at = datetime.now(timezone.utc) + timedelta(
		minutes=settings.access_token_expire_minutes
	)
	payload = {"sub": str(subject), "exp": expires_at}
	return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
	settings = Settings()
	return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
