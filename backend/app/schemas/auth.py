from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
	email: EmailStr
	password: str
	display_name: str


class LoginRequest(BaseModel):
	email: EmailStr
	password: str


class UserPublic(BaseModel):
	id: int
	email: EmailStr
	display_name: str


class TokenResponse(BaseModel):
	access_token: str
	token_type: str = "bearer"


class AuthResponse(BaseModel):
	user: UserPublic
	access_token: str
	token_type: str = "bearer"
