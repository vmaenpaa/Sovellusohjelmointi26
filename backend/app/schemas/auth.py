from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
	email: EmailStr
	password: str
	display_name: str


class UserPublic(BaseModel):
	id: int
	email: EmailStr
	display_name: str


class AuthResponse(BaseModel):
	user: UserPublic
	access_token: str
	token_type: str = "bearer"
